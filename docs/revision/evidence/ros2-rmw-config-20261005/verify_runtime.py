#!/usr/bin/env python3
"""在现有 Humble 环境验证正文的 RMW/配置收发，仅关闭本脚本的进程组。"""
from pathlib import Path
import json
import os
import re
import signal
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
TMP = Path('/tmp/tutorial4new-rmw-runtime-20261005')
TMP.mkdir(exist_ok=True)
TOPIC = '/tutorial4new_rmw_check_20261005/chatter'
BASE = os.environ.copy()
CLEAR = ['RMW_IMPLEMENTATION', 'ROS_DOMAIN_ID', 'ROS_LOCALHOST_ONLY',
         'CYCLONEDDS_URI', 'FASTRTPS_DEFAULT_PROFILES_FILE', 'ROS_DISCOVERY_SERVER',
         'RMW_FASTRTPS_USE_QOS_FROM_XML', 'ZENOH_SESSION_CONFIG_URI',
         'ZENOH_ROUTER_CONFIG_URI', 'ZENOH_CONFIG_OVERRIDE',
         'ZENOH_ROUTER_CHECK_ATTEMPTS']
for key in CLEAR:
    BASE.pop(key, None)
BASE.update(ROS_DOMAIN_ID='97', RCUTILS_COLORIZED_OUTPUT='0')

# 用当前机器真实拥有的网卡地址替换教材占位值，不改随书原文件。
addresses = subprocess.check_output(['ip', '-j', '-4', 'addr'], text=True)
network = json.loads(addresses)
local_ip = next(a['local'] for item in network if item['ifname'] != 'lo'
                for a in item.get('addr_info', []) if a.get('scope') == 'global')
config_root = ROOT / '02-专项技术栈/examples/ros2/rmw-config-demo'
for name in ['fastdds.xml', 'cyclonedds.xml']:
    (TMP / name).write_text((config_root / name).read_text().replace('192.168.10.20', local_ip))

# 配置片段按正文修改安装版本的完整文件，未执行安装或升级。
share = Path(subprocess.check_output(['ros2', 'pkg', 'prefix', '--share', 'rmw_zenoh_cpp'], text=True).strip())
for role in ['SESSION', 'ROUTER']:
    src = share / f'config/DEFAULT_RMW_ZENOH_{role}_CONFIG.json5'
    text = src.read_text()
    if role == 'SESSION':
        text, count = re.subn(r'(?m)^(\s*mode:\s*)"peer"', r'\1"client"', text)
        assert count == 1
        text, count = re.subn(r'(?m)^(\s*)"tcp/localhost:7447"', r'\1"tcp/127.0.0.1:17747"', text)
    else:
        text, count = re.subn(r'(?m)^(\s*)"tcp/\[::\]:7447"', r'\1"tcp/127.0.0.1:17747"', text)
    assert count == 1, (role, count)
    (TMP / f'{role.lower()}.json5').write_text(text)

results = []
owned = []

def launch(name, program, env):
    log_path = OUT / f'{name}.log'
    stream = log_path.open('w')
    process = subprocess.Popen(['ros2', 'run', *program], env=env,
                               stdout=stream, stderr=subprocess.STDOUT,
                               start_new_session=True)
    owned.append((process, stream))
    return process, log_path

def stop(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGINT)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)

def free_port(port):
    with socket.socket() as connection:
        connection.bind(('127.0.0.1', port))

def run(name, implementation, fields=None, router=False):
    env = BASE | {'RMW_IMPLEMENTATION': implementation} | (fields or {})
    processes = []
    router_process = None
    try:
        if router:
            port = 17747 if fields else 7447
            free_port(port)
            router_process, router_log = launch(name+'-router', ['rmw_zenoh_cpp', 'rmw_zenohd'], env)
            processes.append(router_process)
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline:
                if router_process.poll() is not None:
                    raise RuntimeError(router_log.read_text())
                with socket.socket() as connection:
                    if connection.connect_ex(('127.0.0.1', port)) == 0:
                        break
                time.sleep(0.1)
            else:
                raise RuntimeError('router 没有开始监听')
        listener, listener_log = launch(name+'-listener',
            ['demo_nodes_cpp', 'listener', '--ros-args', '-r', f'chatter:={TOPIC}'], env)
        processes.append(listener)
        talker, talker_log = launch(name+'-talker',
            ['demo_nodes_cpp', 'talker', '--ros-args', '-r', f'chatter:={TOPIC}'], env)
        processes.append(talker)
        deadline = time.monotonic() + 12
        received = []
        while time.monotonic() < deadline:
            if listener.poll() is not None or talker.poll() is not None:
                raise RuntimeError(listener_log.read_text() + talker_log.read_text())
            received = re.findall(r'I heard: \[Hello World: (\d+)\]', listener_log.read_text())
            if len(received) >= 3:
                break
            time.sleep(0.2)
        assert len(received) >= 3, listener_log.read_text()
        published = re.findall(r"Publishing: 'Hello World: (\d+)'", talker_log.read_text())
        assert set(received).issubset(set(published)), (received, published)
        record = {'case': name, 'implementation': implementation, 'domain': 97,
                  'topic': TOPIC, 'config': fields or {},
                  'received': received, 'published': published,
                  'status': 'passed'}
        results.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
    finally:
        for process in reversed(processes):
            stop(process)

try:
    run('fastdds-default', 'rmw_fastrtps_cpp', {'ROS_LOCALHOST_ONLY': '1'})
    run('cyclonedds-default', 'rmw_cyclonedds_cpp', {'ROS_LOCALHOST_ONLY': '1'})
    run('fastdds-xml', 'rmw_fastrtps_cpp',
        {'FASTRTPS_DEFAULT_PROFILES_FILE': str(TMP / 'fastdds.xml')})
    run('cyclonedds-xml', 'rmw_cyclonedds_cpp',
        {'CYCLONEDDS_URI': 'file://' + str(TMP / 'cyclonedds.xml')})
    run('zenoh-default', 'rmw_zenoh_cpp', router=True)
    run('zenoh-json5-client', 'rmw_zenoh_cpp',
        {'ZENOH_ROUTER_CONFIG_URI': str(TMP / 'router.json5'),
         'ZENOH_SESSION_CONFIG_URI': str(TMP / 'session.json5')}, router=True)
finally:
    for process, stream in reversed(owned):
        stop(process)
        stream.close()
    summary = {'environment': {'ros_distro': os.environ.get('ROS_DISTRO'),
                'local_ip': local_ip, 'address_inventory': network,
                'package_versions': subprocess.check_output(['dpkg-query', '-W',
                'ros-humble-demo-nodes-cpp', 'ros-humble-rmw-fastrtps-cpp',
                'ros-humble-rmw-cyclonedds-cpp', 'ros-humble-rmw-zenoh-cpp'], text=True)},
               'cases': results, 'cleanup': {'all_owned_processes_exited':
               all(p.poll() is not None for p, _ in owned)},
               'limits': ['同一台机器的临时通信测试，未验证第二台主机',
                          '未执行教材中的 apt 安装或源码构建步骤']}
    (OUT / 'runtime.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
