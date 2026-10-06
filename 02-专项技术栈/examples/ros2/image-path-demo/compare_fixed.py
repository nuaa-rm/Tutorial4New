#!/usr/bin/env python3
"""运行两个固定图像进程，保存统计及共享段偏移；RouDi 由调用者启动。"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
from compare import stop_process


def mapping(pid, address):
    """跨进程比较同一共享文件及文件偏移，不比较虚拟地址数值。"""
    for line in Path(f'/proc/{pid}/maps').read_text().splitlines():
        fields = line.split(maxsplit=5)
        start, end = (int(value, 16) for value in fields[0].split('-'))
        if start <= address < end:
            return dict(device=fields[3], inode=fields[4],
                        object=fields[5] if len(fields) == 6 else '',
                        offset=int(fields[2], 16) + address - start)
    return None


def run(args, number, executable):
    env = os.environ.copy()
    for key in ('CYCLONEDDS_URI', 'FASTRTPS_DEFAULT_PROFILES_FILE',
                'FASTDDS_DEFAULT_PROFILES_FILE', 'RMW_FASTRTPS_USE_QOS_FROM_XML'):
        env.pop(key, None)
    env.update(RMW_IMPLEMENTATION='rmw_cyclonedds_cpp', ROS_LOCALHOST_ONLY='1',
               ROS_DOMAIN_ID=str(args.domain),
               ROS_DISABLE_LOANED_MESSAGES='0' if args.cyclone_config else '1')
    if args.cyclone_config:
        env['CYCLONEDDS_URI'] = 'file://' + str(args.cyclone_config.resolve())
    paths = {role: args.output / f'{number}-{role}.log' for role in ('receive', 'send')}
    children, streams, pointers = {}, {}, {}
    start, done = time.monotonic(), None
    try:
        for role in ('receive', 'send'):
            streams[role] = paths[role].open('w')
            command = [str(executable), '--ros-args', '-r', f'__node:=fixed_image_{role}',
                       '-p', f'role:={role}',
                       '-p', f'loan:={str(args.publish_mode == "loan").lower()}',
                       '-p', f'require_loan:={str(bool(args.cyclone_config)).lower()}',
                       '-p', f'frames:={args.frames}', '-p', f'rate:={args.rate}',
                       '-p', f'verify_full:={str(args.verify_full).lower()}']
            children[role] = subprocess.Popen(command, env=env, stdout=streams[role],
                                              stderr=subprocess.STDOUT, start_new_session=True)
        while True:
            for role, path in paths.items():
                for item in re.findall(r'FIXED_POINTER (\{[^\n]*\})', path.read_text()):
                    row = json.loads(item)
                    key = (role, row['sequence'])
                    if key not in pointers:
                        row['mapping'] = mapping(row['pid'], row['pixel_address'])
                        pointers[key] = row
            if any(child.poll() is not None for child in children.values()):
                raise RuntimeError('收发进程提前退出，查看本轮日志')
            if f'FIXED_DONE {args.frames}' in paths['send'].read_text() and done is None:
                done = time.monotonic()
            if done is not None and time.monotonic() - done >= 2:
                break
            if time.monotonic() - start > max(30, args.frames / args.rate * 6 + 15):
                raise RuntimeError('发布未完成，查看本轮日志')
            time.sleep(0.02)
    finally:
        for child in children.values():
            stop_process(child)
        for stream in streams.values():
            stream.close()
    stats, caps = {}, {}
    for role, path in paths.items():
        text = path.read_text()
        stats[role] = json.loads(re.findall(r'FIXED_STATS (\{[^\n]*\})', text)[-1])
        caps[role] = json.loads(re.findall(r'FIXED_CAP (\{[^\n]*\})', text)[-1])
    pairs = []
    for (role, sequence), source in pointers.items():
        sink = pointers.get(('receive', sequence))
        if role != 'send' or not sink:
            continue
        a, b = source['mapping'], sink['mapping']
        shared = bool(a and b and a['object'].startswith('/dev/shm/') and
                      a['device'] == b['device'] and a['inode'] == b['inode'] and
                      a['offset'] == b['offset'])
        pairs.append(dict(sequence=sequence, source=source, sink=sink, same_shared_sample=shared))
    if stats['send']['count'] != args.frames or stats['receive']['count'] == 0:
        raise RuntimeError('发送帧数不足或没有收到图像')
    if stats['receive']['bad_frames']:
        raise RuntimeError('像素检查失败')
    if args.publish_mode == 'loan' and args.cyclone_config and not any(
            pair['same_shared_sample'] for pair in pairs):
        raise RuntimeError('没有获得相同共享段偏移的证据')
    return dict(repeat=number, publish_mode=args.publish_mode,
                iceoryx=bool(args.cyclone_config), verify_full=args.verify_full,
                sent=stats['send']['count'], received=stats['receive']['count'],
                send_hz=stats['send']['hz'], receive_hz=stats['receive']['hz'],
                delivery_ratio=stats['receive']['count'] / args.frames,
                p95_ms=stats['receive']['p95_ms'], p99_ms=stats['receive']['p99_ms'],
                bad_frames=stats['receive']['bad_frames'], capabilities=caps,
                pointer_pairs=pairs, returncodes={k: v.returncode for k, v in children.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cyclone-config', type=Path)
    parser.add_argument('--publish-mode', choices=('regular', 'loan'), default='loan')
    parser.add_argument('--rate', type=float, default=250.0)
    parser.add_argument('--frames', type=int, default=1000)
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--domain', type=int, default=89)
    parser.add_argument('--verify-full', action='store_true')
    args = parser.parse_args()
    if args.frames < 2 or not 0 < args.rate <= 10000 or args.repeat < 1 or not 0 <= args.domain <= 101:
        parser.error('核对帧数、频率、重复次数与域编号')
    if args.cyclone_config and not args.cyclone_config.is_file():
        parser.error('Cyclone DDS 配置不存在')
    prefix = subprocess.check_output(['ros2', 'pkg', 'prefix', 'image_path_demo'], text=True).strip()
    executable = Path(prefix) / 'lib/image_path_demo/fixed_image'
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'environment.json').write_text(json.dumps(dict(
        ros_distro=os.environ.get('ROS_DISTRO'), payload_bytes=4665600,
        width=1440, height=1080, encoding='bgr8', depth=5, reliability='best_effort',
        rate=args.rate, frames=args.frames, repeats=args.repeat, drain_seconds=2,
        cyclone_config=str(args.cyclone_config.resolve()) if args.cyclone_config else None,
        receiver_callback='const FixedImage &; used only inside callback',
        latency='after fill, before publish -> callback entry', synthetic=True), indent=2)+'\n')
    rows = []
    for number in range(1, args.repeat + 1):
        row = run(args, number, executable)
        rows.append(row)
        (args.output / 'results.json').write_text(json.dumps(rows, indent=2)+'\n')
        print(f"第 {number} 轮：发送 {row['send_hz']:.1f} Hz，接收 {row['delivery_ratio']:.1%}，"
              f"P95 {row['p95_ms']:.3f} ms", flush=True)


if __name__ == '__main__':
    main()
