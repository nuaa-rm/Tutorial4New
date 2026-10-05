#!/usr/bin/env python3
"""同一输入比较多种 RMW 和三种进程布局；只管理本次启动的进程。"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import time


def stop_process(child):
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGINT)
        try:
            child.wait(timeout=12)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()


@contextmanager
def zenoh_router(args, rmw, env, log):
    """Zenoh 每轮使用本程序自己的本机路由器，不连接或关闭用户的路由器。"""
    if rmw != 'rmw_zenoh_cpp':
        yield None
        return
    with socket.socket() as check:
        check.bind(('127.0.0.1', args.zenoh_port))
    shm = str(args.zenoh_shm).lower()
    common = (f'transport/shared_memory/enabled={shm};'
              'transport/shared_memory/transport_optimization/enabled=true;'
              f'transport/shared_memory/transport_optimization/pool_size={args.zenoh_shm_pool_mib * 1048576}')
    env.update(ZENOH_CONFIG_OVERRIDE=(
        f'connect/endpoints=["tcp/127.0.0.1:{args.zenoh_port}"];{common}'),
        ZENOH_ROUTER_CHECK_ATTEMPTS='5')
    router_env = dict(env, ZENOH_CONFIG_OVERRIDE=(
        f'listen/endpoints=["tcp/127.0.0.1:{args.zenoh_port}"];{common}'))
    with log.open('w') as stream:
        router = subprocess.Popen(['ros2', 'run', 'rmw_zenoh_cpp', 'rmw_zenohd'],
                                  env=router_env, stdout=stream, stderr=subprocess.STDOUT,
                                  start_new_session=True)
        try:
            deadline = time.monotonic() + 15
            while True:
                if router.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(f'Zenoh 路由器未就绪，查看 {log}')
                try:
                    with socket.create_connection(('127.0.0.1', args.zenoh_port), timeout=0.2):
                        break
                except OSError:
                    time.sleep(0.05)
            yield router
        finally:
            stop_process(router)


def process_usage(group):
    """累计本实验进程组 CPU 秒；RSS 相加会重复计算共享页。"""
    cpu, rss = 0.0, 0
    for item in Path('/proc').iterdir():
        if not item.name.isdigit():
            continue
        try:
            fields = (item / 'stat').read_text().rsplit(')', 1)[1].split()
            if int(fields[2]) == group:
                cpu += (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')
                rss += int(fields[21]) * os.sysconf('SC_PAGE_SIZE')
        except (OSError, ValueError, IndexError):
            continue
    return cpu, rss


def run_case(args, rmw, mode, repeat):
    env = os.environ.copy()
    # 在独立域内排除用户 DDS 调优变量，以默认配置作对照。
    for key in ('CYCLONEDDS_URI', 'FASTRTPS_DEFAULT_PROFILES_FILE',
                'FASTDDS_DEFAULT_PROFILES_FILE', 'RMW_FASTRTPS_USE_QOS_FROM_XML',
                'RMW_FASTRTPS_PUBLICATION_MODE', 'ROS_DISABLE_LOANED_MESSAGES'):
        env.pop(key, None)
    for key in list(env):
        if key.startswith(('ZENOH_', 'RMW_ZENOH_')):
            env.pop(key)
    env.update(RMW_IMPLEMENTATION=rmw, ROS_DOMAIN_ID=str(args.domain), ROS_LOCALHOST_ONLY='1')
    parameters = dict(mode=mode, width=args.width, height=args.height, channels=args.channels,
                      rate=args.rate, frames=args.frames, depth=args.depth,
                      reliable=str(args.reliable).lower(), work_ms=args.work_ms)
    command = ['ros2', 'launch', 'image_path_demo', 'path.launch.py',
               *[f'{k}:={v}' for k, v in parameters.items()]]
    log = args.output / f'{rmw}-{mode}-{repeat}.log'
    start, done, peak_rss, cpu = time.monotonic(), None, 0, 0.0
    router_log = args.output / f'{rmw}-{mode}-{repeat}-router.log'
    with zenoh_router(args, rmw, env, router_log) as router, log.open('w') as stream:
        child = subprocess.Popen(command, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        try:
            while child.poll() is None:
                cpu, rss = process_usage(child.pid)
                if router is not None:
                    router_cpu, router_rss = process_usage(router.pid)
                    cpu += router_cpu
                    rss += router_rss
                    if router.poll() is not None:
                        raise RuntimeError(f'Zenoh 路由器提前退出，查看 {router_log}')
                peak_rss = max(peak_rss, rss)
                text = log.read_text()
                if 'SOURCE_DONE' in text and done is None:
                    done = time.monotonic()
                if done is not None and time.monotonic() - done > args.drain_seconds:
                    break
                if time.monotonic() - start > max(30, args.frames / args.rate * 6 + 15):
                    raise RuntimeError(f'发布未完成，查看 {log}')
                time.sleep(0.05)
        finally:
            stop_process(child)
    text = log.read_text()
    source = re.findall(r'SOURCE (\{[^\n]*\})', text)
    sink = re.findall(r'SINK (\{[^\n]*\})', text)
    if len(source) != 1 or len(sink) != 1:
        raise RuntimeError(f'缺少正常退出的统计，查看 {log}')
    row = dict(rmw=rmw, repeat=repeat, **parameters,
               **json.loads(source[0]), **json.loads(sink[0]),
               wall_seconds=round(time.monotonic() - start, 3),
               cpu_seconds_before_stop=round(cpu, 3),
               peak_rss_sum_mb=round(peak_rss / 1e6, 3),
               launch_returncode=child.returncode, log=log.name)
    if rmw == 'rmw_zenoh_cpp':
        row.update(zenoh_shm=args.zenoh_shm, zenoh_router_port=args.zenoh_port,
                   zenoh_shm_pool_mib=args.zenoh_shm_pool_mib,
                   zenoh_shm_provider_error='Error creating lazy ShmProvider' in text,
                   router_in_resource_totals=True, router_log=router_log.name,
                   router_returncode=router.returncode)
    if row['sent'] != args.frames or row['bad_frames']:
        raise RuntimeError(f'帧数或内容不正确，查看 {log}')
    if row['received'] == 0:
        raise RuntimeError(f'没有收到样本，不能给出延迟统计，查看 {log}')
    row['delivery_ratio'] = row['received'] / row['sent']
    if mode == 'intra' and row['pointer_matches'] != row['received']:
        raise RuntimeError(f'进程内数据地址不一致，查看 {log}')
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--width', type=int, default=64)
    parser.add_argument('--height', type=int, default=48)
    parser.add_argument('--channels', type=int, choices=(1, 3), default=3)
    parser.add_argument('--rate', type=float, default=25.0)
    parser.add_argument('--frames', type=int, default=100)
    parser.add_argument('--depth', type=int, default=5)
    parser.add_argument('--work-ms', type=int, default=0)
    parser.add_argument('--reliable', action='store_true')
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--domain', type=int, default=87)
    parser.add_argument('--drain-seconds', type=float, default=2.0)
    parser.add_argument('--modes', nargs='+', choices=('separate', 'same', 'intra'),
                        default=['separate', 'same', 'intra'])
    parser.add_argument('--rmws', nargs='+', default=['rmw_fastrtps_cpp', 'rmw_cyclonedds_cpp'],
                        choices=['rmw_fastrtps_cpp', 'rmw_cyclonedds_cpp', 'rmw_zenoh_cpp'])
    parser.add_argument('--zenoh-port', type=int, default=17447)
    parser.add_argument('--zenoh-shm', action='store_true',
                        help='显式开启 Zenoh 共享内存传输优化；默认关闭')
    parser.add_argument('--zenoh-shm-pool-mib', type=int, default=48,
                        help='每个 Zenoh 会话的共享池大小；需同时核对 memlock 和 /dev/shm')
    args = parser.parse_args()
    if (args.width <= 0 or args.height <= 0 or args.width * args.height * args.channels > 64000000
            or not 0 < args.rate <= 10000 or args.frames < 2 or args.depth < 1
            or args.work_ms < 0 or args.repeat < 1 or args.drain_seconds <= 0
            or not 0 <= args.domain <= 101 or not 1024 <= args.zenoh_port <= 65535
            or not 1 <= args.zenoh_shm_pool_mib <= 1024):
        parser.error('核对尺寸、频率、帧数、深度、耗时、重复次数与域编号')
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'environment.json').write_text(json.dumps(dict(
        ros_distro=os.environ.get('ROS_DISTRO'), uname=list(os.uname()),
        default_profiles_in_cwd=Path('DEFAULT_FASTRTPS_PROFILES.xml').exists(),
        clock='Linux CLOCK_MONOTONIC via C++ steady_clock; same host only',
        payload_bytes=args.width * args.height * args.channels,
        latency='after allocation/fill, before publish -> callback entry; excludes processing',
        cpu='launch and live child processes, includes discovery/load/drain; not steady-state %',
        rss='sum of process RSS, shared pages counted repeatedly; includes owned Zenoh router',
        zenoh_router='owned loopback router for each Zenoh case; included in CPU/RSS totals',
        zenoh_port=args.zenoh_port, zenoh_shm=args.zenoh_shm,
        zenoh_shm_pool_mib=args.zenoh_shm_pool_mib,
        synthetic=True, hardware_camera=False), ensure_ascii=False, indent=2) + '\n')
    if Path('DEFAULT_FASTRTPS_PROFILES.xml').exists():
        raise RuntimeError('当前目录有隐式 Fast DDS 配置；请换到干净目录运行')
    rows = []
    for repeat in range(1, args.repeat + 1):
        for rmw in args.rmws:
            for mode in args.modes:
                print(f'运行 {rmw} / {mode} / 第 {repeat} 次', flush=True)
                rows.append(run_case(args, rmw, mode, repeat))
                (args.output / 'results.json').write_text(
                    json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
                row = rows[-1]
                print(f"  发送 {row['send_hz']:.1f} Hz，接收 {row['receive_hz']:.1f} Hz，"
                      f"接收比例 {row['delivery_ratio']:.1%}，P95 {row['p95_ms']:.3f} ms", flush=True)


if __name__ == '__main__':
    main()
