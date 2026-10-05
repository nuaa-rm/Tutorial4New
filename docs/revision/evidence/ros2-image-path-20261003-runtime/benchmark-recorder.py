#!/usr/bin/env python3
"""同一输入比较两种 RMW 和三种进程布局；只管理本次启动的进程。"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


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
    env.update(RMW_IMPLEMENTATION=rmw, ROS_DOMAIN_ID=str(args.domain), ROS_LOCALHOST_ONLY='1')
    parameters = dict(mode=mode, width=args.width, height=args.height, channels=args.channels,
                      rate=args.rate, frames=args.frames, depth=args.depth,
                      reliable=str(args.reliable).lower(), work_ms=args.work_ms)
    command = ['ros2', 'launch', 'image_path_demo', 'path.launch.py',
               *[f'{k}:={v}' for k, v in parameters.items()]]
    log = args.output / f'{rmw}-{mode}-{repeat}.log'
    start, done, peak_rss, cpu = time.monotonic(), None, 0, 0.0
    with log.open('w') as stream:
        child = subprocess.Popen(command, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        try:
            while child.poll() is None:
                cpu, rss = process_usage(child.pid)
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
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGINT)
                try:
                    child.wait(timeout=12)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
    text = log.read_text()
    source = re.findall(r'SOURCE (\{[^\n]*\})', text)
    sink = re.findall(r'SINK (\{[^\n]*\})', text)
    if len(source) != 1 or len(sink) != 1:
        raise RuntimeError(f'缺少正常退出的统计，查看 {log}')
    row = dict(rmw=rmw, repeat=repeat, **parameters,
               **json.loads(source[0]), **json.loads(sink[0]),
               wall_seconds=round(time.monotonic() - start, 3),
               cpu_seconds_before_stop=round(cpu, 3),
               peak_rss_sum_mb=round(peak_rss / 1e6, 3), log=log.name)
    if row['sent'] != args.frames or row['bad_frames']:
        raise RuntimeError(f'帧数或内容不正确，查看 {log}')
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
                        choices=['rmw_fastrtps_cpp', 'rmw_cyclonedds_cpp'])
    args = parser.parse_args()
    if (args.width <= 0 or args.height <= 0 or args.width * args.height * args.channels > 64000000
            or not 0 < args.rate <= 10000 or args.frames < 2 or args.depth < 1
            or args.work_ms < 0 or args.repeat < 1 or args.drain_seconds <= 0
            or not 0 <= args.domain <= 101):
        parser.error('核对尺寸、频率、帧数、深度、耗时、重复次数与域编号')
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'environment.json').write_text(json.dumps(dict(
        ros_distro=os.environ.get('ROS_DISTRO'), uname=list(os.uname()),
        default_profiles_in_cwd=Path('DEFAULT_FASTRTPS_PROFILES.xml').exists(),
        clock='Linux CLOCK_MONOTONIC via C++ steady_clock; same host only',
        payload_bytes=args.width * args.height * args.channels,
        latency='after allocation/fill, before publish -> callback entry; excludes processing',
        cpu='launch and live child processes, includes discovery/load/drain; not steady-state %',
        rss='sum of process RSS, shared pages counted repeatedly',
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
