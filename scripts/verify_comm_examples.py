#!/usr/bin/env python3
"""核验卷二通信小工程：真实 TCP/PTY/ROS 与固定故障输入，修改只在副本。"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time

SOURCE = Path(__file__).resolve().parents[1] / '02-专项技术栈/examples/communication/stream-link-demo'
records, live = [], []

def stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=5)

def run(command, folder, env, expected=0):
    proc = subprocess.Popen(command, cwd=folder, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        output, _ = proc.communicate(timeout=25)
    except subprocess.TimeoutExpired:
        stop(proc)
        output, _ = proc.communicate()
        raise RuntimeError(output)
    records.append({'command': command, 'returncode': proc.returncode, 'output': output})
    print(f'{len(records)}: {command[:2]} -> {proc.returncode}', flush=True)
    assert proc.returncode == expected, output
    return output

def background(command, folder, env):
    log = tempfile.TemporaryFile(mode='w+t')
    proc = subprocess.Popen(command, cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
    live.append((proc, log))
    return proc, log

def read(log):
    log.seek(0)
    return log.read()

def finish(proc, log, label, natural=False):
    if natural:
        proc.wait(timeout=8)
        assert proc.returncode == 0, read(log)
    else:
        stop(proc)
    output = read(log)
    records.append({'background': label, 'returncode': proc.returncode, 'output': output})
    return output

def tcp_server(folder, env):
    proc, log = background(['python3', '-u', 'tcp_demo.py', 'server', '--port', '0'], folder, env)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        match = re.search(r"监听 \('127\.0\.0\.1', (\d+)\)", read(log))
        if match:
            return proc, log, match.group(1)
        assert proc.poll() is None, read(log)
        time.sleep(.05)
    raise RuntimeError(read(log))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    env = os.environ.copy()
    assert env.get('ROS_DISTRO') == 'jazzy', '先加载 Jazzy 环境'
    env.update(ROS_DOMAIN_ID='79', ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST', RCUTILS_COLORIZED_OUTPUT='0')
    for key in ['ROS_LOCALHOST_ONLY', 'ROS_STATIC_PEERS', 'RMW_IMPLEMENTATION']:
        env.pop(key, None)
    try:
        with tempfile.TemporaryDirectory(prefix='comm-textbook-') as temp:
            folder = Path(temp) / 'demo'
            shutil.copytree(SOURCE, folder)
            env['ROS_LOG_DIR'] = str(Path(temp) / 'ros-logs')
            run(['ros2', 'daemon', 'stop'], folder, env)
            for name in ['ping', 'parser', 'latest', 'event', 'fault', 'serial', 'bridge']:
                run(['python3', name + '_demo.py'], folder, env)
            original = (folder / 'ping_demo.py').read_text()
            (folder / 'ping_demo.py').write_text(original.replace('b"ping"', 'b"pong"'))
            assert 'pong' in run(['python3', 'ping_demo.py'], folder, env)
            (folder / 'ping_demo.py').write_text(original.replace('client.sendall(b"ping")', 'client.sendall(b"po")\n            client.shutdown(socket.SHUT_WR)'))
            assert '连接提前关闭' in run(['python3', 'ping_demo.py'], folder, env, expected=1)
            (folder / 'ping_demo.py').write_text(original)
            run(['python3', '-c', '''from framing import *
data = encode_length(b'AB') + encode_length(b'XYZ')
for step in range(1, len(data)+1):
    parser, frames = LengthParser(), []
    for start in range(0,len(data),step): frames += parser.feed(data[start:start+step])
    assert frames == [b'AB',b'XYZ'] and not parser.buffer
parser = LengthParser()
assert parser.feed(b'\\x10'+b'A'*15) == [] and len(parser.buffer)==16
assert parser.feed(b'A') == [b'A'*16]
for size in [0,17,255]:
    try: LengthParser().feed(bytes([size]))
    except ValueError: pass
    else: raise AssertionError(size)
parser, values = CRCParser(), []
for value in range(256):
    for byte in encode_crc(value): values += parser.feed(bytes([byte]))
assert values == list(range(256)) and not parser.buffer
damaged=bytearray(encode_crc(7)); damaged[1] ^= 1
parser=CRCParser()
assert parser.feed(damaged+encode_crc(9)) == [9] and parser.bad_crc==1
print('所有分片、长度边界、256载荷、坏数据与恢复通过')'''], folder, env)
            proc, log, port = tcp_server(folder, env)
            for _ in range(2):
                run(['python3', 'tcp_demo.py', 'client', '--port', port], folder, env)
            output = finish(proc, log, 'TCP 两次连接与迟到清理', natural=True)
            assert '迟到清理 1 实际清理: False' in output and "代次 2 回显 b'XYZ'" in output
            for data in [b'\x03A', b'\x00']:
                proc, log, port = tcp_server(folder, env)
                run(['python3', '-c', "import socket; s=socket.create_connection(('127.0.0.1'," + port + ")); s.sendall(" + repr(data) + "); s.close()"], folder, env)
                run(['python3', 'tcp_demo.py', 'client', '--port', port], folder, env)
                output = finish(proc, log, '半帧/非法长度后新连接 ' + repr(data), natural=True)
                assert (('丢弃半帧字节: 2' if data[0] else '非法长度') in output)
            run(['python3', '-c', '''import socket, threading
from state import Session
a,b=socket.socketpair();c,d=socket.socketpair()
with a,b,c,d:
    session=Session();first=session.connect(a)
    ready=threading.Event()
    def late():
        ready.wait();assert not session.disconnect(first)
    thread=threading.Thread(target=late);thread.start()
    second=session.connect(c);session.put(second,'position',42,at=0)
    ready.set();thread.join(timeout=2);assert not thread.is_alive()
    assert session.take(second,now=2,max_age=2)==('position',42)
    session.put(second,'position',99,at=0)
    assert session.take(second,now=3,max_age=2) is None and session.expired==1
    session.put(second,'position',30,at=3);session.put(second,'status','ready',at=3)
    session.priority=('status','position')
    assert session.take(second,now=3,max_age=2)==('status','ready')
    assert session.take(second,now=3,max_age=2)==('position',30)
    assert not session.put(first,'position',100,at=3)
    try: session.put(second,'unknown',100,at=3)
    except ValueError: pass
    else: raise AssertionError('无限槽位')
    session.disconnect(second)
print('真实线程迟到清理、时效边界、优先级与拒绝旧写入通过')'''], folder, env)
            code = (folder / 'event_demo.py').read_text()
            (folder / 'event_demo.py').write_text(code.replace('event[0] == 1 and attempt == 1', 'event[0] == 1'))
            assert '三次未确认' in run(['python3', 'event_demo.py'], folder, env, expected=1)
            original = (folder / 'parser_demo.py').read_text()
            (folder / 'parser_demo.py').write_text(original.replace('stream = b"noise" + bad + encode_crc(7)', 'damaged = bytearray(encode_crc(7))\ndamaged[1] ^= 1\nstream = b"noise" + bad + damaged + encode_crc(9)').replace('values == [7] and parser.bad_crc == 1', 'values == [9] and parser.bad_crc == 2'))
            assert '坏 CRC: 2' in run(['python3', 'parser_demo.py'], folder, env)
            original = (folder / 'fault_demo.py').read_text()
            changed = original.replace('left.take(a, now=second, max_age=2) is None', 'left.take(a, now=second, max_age=4) == ("position", 11)').replace('left.expired == 1', 'left.expired == 0').replace('A 过期丢弃:', 'A 未过期:').replace('，此时采用 B 的新值', '，A 的旧值仍被允许')
            (folder / 'fault_demo.py').write_text(changed)
            assert 'A 未过期: 0' in run(['python3', 'fault_demo.py'], folder, env)
            code = (folder / 'bridge_demo.py').read_text()
            (folder / 'bridge_demo.py').write_text(code.replace('8, 1250', '8, 2000'))
            assert '(8, 2.0)' in run(['python3', 'bridge_demo.py'], folder, env)
            for millimeters, meters in [(1250, '1.25'), (2000, '2.0')]:
                (folder / 'bridge_demo.py').write_text(code.replace('8, 1250', '8, ' + str(millimeters)))
                proc, log = background(['python3', 'bridge_demo.py', '--ros'], folder, env)
                output = run(['ros2', 'topic', 'echo', '/range_m', 'std_msgs/msg/Float64', '--once'], folder, env)
                assert 'data: ' + meters in output
                assert 'seq=8, range_m=' + meters in finish(proc, log, 'Jazzy 实际桥接话题 ' + meters)
            run(['ros2', 'daemon', 'stop'], folder, env)
    finally:
        for proc, log in live:
            stop(proc)
            log.close()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({'ROS_DISTRO': 'jazzy', 'records': records}, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
