#!/usr/bin/env python3
"""同一收发程序比较三种 RMW 的普通 Image 与 FixedImage。"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from compare import stop_process, zenoh_router


@contextmanager
def shared_pool(args):
    """RouDi 只管理本次实验；已有管理进程时拒绝启动第二个。"""
    if 'shared' not in args.profiles or 'rmw_cyclonedds_cpp' not in args.rmws:
        yield
        return
    if subprocess.run(['pgrep', '-x', 'iox-roudi'], stdout=subprocess.DEVNULL).returncode == 0:
        raise RuntimeError('已有 RouDi；结束已有实验，或只选择 default 配置')
    before = sorted(p.name for p in Path('/dev/shm').iterdir())
    path = args.output / 'roudi.log'
    with path.open('w') as stream:
        child = subprocess.Popen(['iox-roudi', '-c', str(args.share / 'config/roudi.toml')],
                                 stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            end = time.monotonic() + 15
            while 'RouDi is ready' not in path.read_text():
                if child.poll() is not None or time.monotonic() > end:
                    raise RuntimeError(f'RouDi 未就绪，查看 {path}')
                time.sleep(0.05)
            yield
        finally:
            stop_process(child)
            after = sorted(p.name for p in Path('/dev/shm').iterdir())
            (args.output / 'shared-pool-cleanup.json').write_text(json.dumps(dict(
                before=before, after=after, added=sorted(set(after) - set(before)),
                roudi_returncode=child.returncode), indent=2) + '\n')


def run_case(args, rmw, kind, profile, publish_mode, number):
    env = os.environ.copy()
    for key in ('CYCLONEDDS_URI', 'FASTRTPS_DEFAULT_PROFILES_FILE',
                'FASTDDS_DEFAULT_PROFILES_FILE', 'RMW_FASTRTPS_USE_QOS_FROM_XML',
                'RMW_FASTRTPS_PUBLICATION_MODE', 'ROS_DISABLE_LOANED_MESSAGES'):
        env.pop(key, None)
    for key in list(env):
        if key.startswith(('ZENOH_', 'RMW_ZENOH_')):
            env.pop(key)
    env.update(RMW_IMPLEMENTATION=rmw, ROS_LOCALHOST_ONLY='1',
               ROS_DOMAIN_ID=str(args.domain), ROS_DISABLE_LOANED_MESSAGES='0')
    if profile == 'shared' and rmw == 'rmw_cyclonedds_cpp':
        env['CYCLONEDDS_URI'] = 'file://' + str(args.share / 'config/cyclone-iceoryx.xml')
    if profile == 'shared' and rmw == 'rmw_fastrtps_cpp':
        env.update(FASTRTPS_DEFAULT_PROFILES_FILE=str(args.share / 'config/fastdds-loan.xml'),
                   RMW_FASTRTPS_USE_QOS_FROM_XML='1')
    args.zenoh_shm = profile == 'shared'
    name = f'{rmw}-{kind}-{profile}-{publish_mode}-{number}'
    paths = {role: args.output / f'{name}-{role}.log' for role in ('receive', 'send')}
    router_log = args.output / f'{name}-router.log'
    children, streams = {}, {}
    start, done = time.monotonic(), None
    with zenoh_router(args, rmw, env, router_log):
        try:
            for role in ('receive', 'send'):
                streams[role] = paths[role].open('w')
                command = [str(args.executable), kind, '--ros-args', '-r',
                           f'__node:=benchmark_{role}', '-p', f'role:={role}',
                           '-p', f'loan:={str(publish_mode == "loan").lower()}',
                           '-p', f'frames:={args.frames}', '-p', f'rate:={args.rate}',
                           '-p', f'verify_full:={str(args.verify_full).lower()}']
                children[role] = subprocess.Popen(command, env=env, stdout=streams[role],
                                                  stderr=subprocess.STDOUT, start_new_session=True)
            while True:
                if any(child.poll() is not None for child in children.values()):
                    raise RuntimeError(f'收发进程提前退出，查看 {name} 的日志')
                if f'BENCH_DONE {args.frames}' in paths['send'].read_text() and done is None:
                    done = time.monotonic()
                if done is not None and time.monotonic() - done >= args.drain_seconds:
                    break
                if time.monotonic() - start > max(30, args.frames / args.rate * 6 + 15):
                    raise RuntimeError(f'发布未完成，查看 {name} 的日志')
                time.sleep(0.02)
        finally:
            for child in children.values():
                stop_process(child)
            for stream in streams.values():
                stream.close()
    stats, capabilities = {}, {}
    for role, path in paths.items():
        content = path.read_text()
        stats[role] = json.loads(re.findall(r'BENCH_STATS (\{[^\n]*\})', content)[-1])
        capabilities[role] = json.loads(re.findall(r'BENCH_CAP (\{[^\n]*\})', content)[-1])
    if stats['send']['count'] != args.frames or not 0 < stats['receive']['count'] <= args.frames:
        raise RuntimeError(f'帧数不正确，查看 {name} 的日志')
    if stats['receive']['bad_frames']:
        raise RuntimeError(f'像素检查失败，查看 {name} 的日志')
    return dict(rmw=rmw, message_type=kind, profile=profile, publish_mode=publish_mode,
                repeat=number, sent=stats['send']['count'], received=stats['receive']['count'],
                send_hz=stats['send']['hz'], receive_hz=stats['receive']['hz'],
                delivery_ratio=stats['receive']['count'] / args.frames,
                p95_ms=stats['receive']['p95_ms'], p99_ms=stats['receive']['p99_ms'],
                bad_frames=stats['receive']['bad_frames'], capabilities=capabilities,
                zenoh_shm_provider_error=any('Error creating lazy ShmProvider' in p.read_text()
                                             for p in [*paths.values(), router_log] if p.exists()),
                returncodes={k: v.returncode for k, v in children.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rmws', nargs='+', choices=['rmw_fastrtps_cpp', 'rmw_cyclonedds_cpp',
                        'rmw_zenoh_cpp'], default=['rmw_fastrtps_cpp', 'rmw_cyclonedds_cpp', 'rmw_zenoh_cpp'])
    parser.add_argument('--types', nargs='+', choices=['dynamic', 'fixed'], default=['dynamic', 'fixed'])
    parser.add_argument('--profiles', nargs='+', choices=['default', 'shared'], default=['default', 'shared'])
    parser.add_argument('--include-loan', action='store_true')
    parser.add_argument('--verify-full', action='store_true')
    parser.add_argument('--rate', type=float, default=250.0)
    parser.add_argument('--frames', type=int, default=1000)
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--domain', type=int, default=90)
    parser.add_argument('--drain-seconds', type=float, default=2.0)
    parser.add_argument('--zenoh-port', type=int, default=17876)
    parser.add_argument('--zenoh-shm-pool-mib', type=int, default=6)
    args = parser.parse_args()
    if (args.frames < 2 or not 0 < args.rate <= 10000 or args.repeat < 1 or
            not 0 <= args.domain <= 101 or args.drain_seconds < 0 or
            not 1024 <= args.zenoh_port <= 65535 or args.zenoh_shm_pool_mib < 5):
        parser.error('核对帧数、频率、重复次数、域、排空时间、端口与共享池容量')
    if Path('DEFAULT_FASTRTPS_PROFILES.xml').exists():
        parser.error('当前目录存在隐式 Fast DDS 配置，请换到干净目录')
    prefix = Path(subprocess.check_output(['ros2', 'pkg', 'prefix', 'image_path_demo'], text=True).strip())
    args.executable = prefix / 'lib/image_path_demo/image_benchmark'
    args.share = Path(subprocess.check_output(['ros2', 'pkg', 'prefix', '--share', 'image_path_demo'], text=True).strip())
    args.output.mkdir(parents=True, exist_ok=False)
    metadata = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()}
    metadata.update(ros_distro=os.environ.get('ROS_DISTRO'), width=1440, height=1080,
                    encoding='bgr8', payload_bytes=4665600, depth=5, reliability='best_effort',
                    layout='separate', callback='const Message &; only within callback',
                    latency='after fill, before publish -> callback entry', synthetic=True)
    (args.output / 'environment.json').write_text(json.dumps(metadata, indent=2) + '\n')
    rows = []
    with shared_pool(args):
        for number in range(1, args.repeat + 1):
            for profile in args.profiles:
                for rmw in args.rmws:
                    for kind in args.types:
                        ordinary = run_case(args, rmw, kind, profile, 'regular', number)
                        modes = [ordinary]
                        if (args.include_loan and kind == 'fixed' and
                                all(cap['can_loan'] for cap in ordinary['capabilities'].values())):
                            modes.append(run_case(args, rmw, kind, profile, 'loan', number))
                        for row in modes:
                            rows.append(row)
                            (args.output / 'results.json').write_text(json.dumps(rows, indent=2) + '\n')
                            print(f"{rmw} {kind} {profile} {row['publish_mode']} 第 {number} 轮："
                                  f"{row['send_hz']:.1f} Hz，接收 {row['delivery_ratio']:.1%}，"
                                  f"P95 {row['p95_ms']:.3f} ms", flush=True)


if __name__ == '__main__':
    main()
