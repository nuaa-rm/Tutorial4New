#!/usr/bin/env python3
"""在 Humble 临时工作空间验证 Launch 正文与练习副本，不改教学源码。"""
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

repo = Path('/home/mijiao/Apps/Tutorial4New')
evidence = repo / 'docs/revision/evidence/ros2-launch-20261005'
work = Path('/tmp/tutorial4new-launch-20261005-runtime')
work.mkdir(exist_ok=True)
pkg = work / 'src/training_tools'
pkg.parent.mkdir(exist_ok=True)
shutil.copytree(repo / '02-专项技术栈/examples/ros2/training_tools', pkg,
                dirs_exist_ok=True)
launch_dir = pkg / 'launch'
basic = (launch_dir / 'basic.launch.py').read_text()
(launch_dir / 'pulse.launch.py').write_text(basic.replace("name='heartbeat'", "name='pulse'"))
heartbeat = (launch_dir / 'heartbeat.launch.py').read_text()
yaml_only = re.sub(r"parameters=\[LaunchConfiguration\('params_file'\),.*?value_type=str\)\}\],",
                   "parameters=[LaunchConfiguration('params_file')],", heartbeat, flags=re.S)
assert yaml_only != heartbeat
(launch_dir / 'yaml_only.launch.py').write_text(yaml_only)
team = (launch_dir / 'team.launch.py').read_text()
fixed = team.replace("'/red/health'", "['/', LaunchConfiguration('robot'), '/health']")
(launch_dir / 'fixed_team.launch.py').write_text(fixed)
shutdown = fixed.replace('DeclareLaunchArgument, ExecuteProcess,',
                         'DeclareLaunchArgument, EmitEvent, ExecuteProcess,')
shutdown = shutdown.replace('from launch.conditions import',
                             'from launch.events import Shutdown\nfrom launch.conditions import')
shutdown = shutdown.replace("LogInfo(msg='Observer exited; heartbeat keeps running.')",
                             "EmitEvent(event=Shutdown(reason='Observer finished.'))")
(launch_dir / 'shutdown_team.launch.py').write_text(shutdown)
multi = (launch_dir / 'multi.launch.py').read_text()
three = multi.replace("('red', 'blue')", "('red', 'blue', 'green')").replace("'robot': 'sensors'", "'robot': 'camera'")
(launch_dir / 'three.launch.py').write_text(three)
(launch_dir / 'absolute.launch.py').write_text(heartbeat.replace("('status', 'health')", "('status', '/health')"))
(launch_dir / 'three_absolute.launch.py').write_text(three.replace('heartbeat.launch.py', 'absolute.launch.py'))
custom = work / 'custom.yaml'
custom.write_text('/**:\n  ros__parameters:\n    text: "external yaml"\n')

os.environ.update(ROS_DOMAIN_ID='87', ROS_LOCALHOST_ONLY='1',
                  RMW_IMPLEMENTATION='rmw_fastrtps_cpp',
                  ROS_LOG_DIR=str(work / 'ros-logs'))
records = []

def run(cmd, timeout=25, expect=0):
    result = subprocess.run(cmd, cwd=work, text=True, capture_output=True,
                            timeout=timeout, env=os.environ)
    assert result.returncode == expect, (cmd, result.returncode, result.stdout, result.stderr)
    return result.stdout + result.stderr

build = run(['colcon', 'build', '--packages-select', 'training_tools',
             '--cmake-args', '-DBUILD_TESTING=ON'], timeout=120)
(evidence / 'build.txt').write_text(build)
raw = subprocess.check_output(['bash', '-c', 'source install/setup.bash; env -0'], cwd=work)
os.environ.update(dict(item.split('=', 1) for item in raw.decode().split('\0') if '=' in item))
test = run(['colcon', 'test', '--packages-select', 'training_tools'], timeout=60)
test += run(['colcon', 'test-result', '--verbose'])
(evidence / 'ament-test.txt').write_text(test)

class Session:
    def __init__(self, tag, file, *args):
        self.tag = tag
        self.file = evidence / (tag + '.txt')
        self.stream = self.file.open('w')
        self.proc = subprocess.Popen(['ros2', 'launch', 'training_tools', file, *args],
                                     cwd=work, env=os.environ, stdout=self.stream,
                                     stderr=subprocess.STDOUT, start_new_session=True)
    def __enter__(self):
        time.sleep(1.5)
        assert self.proc.poll() is None, self.file.read_text()
        return self
    def log(self):
        return self.file.read_text()
    def wait_text(self, text, timeout=15):
        end = time.monotonic() + timeout
        while text not in self.log() and time.monotonic() < end:
            time.sleep(.1)
        assert text in self.log(), self.log()
    def __exit__(self, *error):
        if self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGINT)
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait(timeout=5)
        self.stream.close()
        time.sleep(.25)


def check(tag, data):
    records.append({'case': tag, 'status': '通过', **data})
    (evidence / 'runtime.json').write_text(json.dumps({
        'environment': {'os': 'Ubuntu 22.04.5 LTS', 'ros_distro': os.environ['ROS_DISTRO'],
                        'rmw': os.environ['RMW_IMPLEMENTATION'], 'domain': '87',
                        'boundary': '独立临时副本、本机无硬件验证'},
        'checks': records}, ensure_ascii=False, indent=2) + '\n')
    print(tag, '通过', flush=True)


def echo(topic, value):
    out = run(['ros2', 'topic', 'echo', topic, 'std_msgs/msg/String', '--once'])
    assert 'data: ' + value in out or "data: '" + value + "'" in out, out
    return out


def nodes(*names):
    end = time.monotonic() + 12
    while True:
        out = run(['ros2', 'node', 'list', '--no-daemon', '--spin-time', '2'])
        if all(name in out.splitlines() for name in names):
            return out
        assert time.monotonic() < end, out

args = run(['ros2', 'launch', 'training_tools', 'heartbeat.launch.py', '--show-args'])
assert all(key in args for key in ['robot', 'text', 'params_file']), args
check('启动参数查询', {'output': args})
with Session('basic', 'basic.launch.py'):
    check('单节点启动', {'nodes': nodes('/heartbeat'), 'message': echo('/status', 'ready')})
with Session('pulse', 'pulse.launch.py'):
    check('程序名与节点名', {'nodes': nodes('/pulse'), 'message': echo('/status', 'ready')})
with Session('launch-default', 'heartbeat.launch.py'):
    check('字典覆盖YAML', {'message': echo('/robot1/health', 'ready from launch')})
with Session('string-true', 'heartbeat.launch.py', 'robot:=blue', 'text:=true'):
    param = run(['ros2', 'param', 'get', '/blue/heartbeat', 'text'])
    assert 'String value is: true' in param, param
    check('字符串类型与重映射', {'nodes': nodes('/blue/heartbeat'),
                              'parameter': param, 'message': echo('/blue/health', 'true')})
with Session('yaml-only', 'yaml_only.launch.py', 'text:=true'):
    check('仅YAML参数', {'message': echo('/robot1/health', 'ready from yaml')})
with Session('yaml-external', 'yaml_only.launch.py', 'params_file:=' + str(custom)):
    check('外部配置路径', {'message': echo('/robot1/health', 'external yaml')})
with Session('team', 'team.launch.py') as session:
    session.wait_text('Observer exited; heartbeat keeps running.')
    assert session.proc.poll() is None
    check('嵌套与退出事件', {'nodes': nodes('/red/heartbeat'),
                          'message': echo('/red/health', 'team ready'),
                          'event': '观测退出后心跳继续运行'})
with Session('watch-false', 'team.launch.py', 'watch:=false') as session:
    session.wait_text('Observer disabled.')
    assert not re.search(r'\[ros2-\d+\]: process started', session.log()), session.log()
    check('If与Unless条件', {'nodes': nodes('/red/heartbeat'),
                            'message': echo('/red/health', 'team ready'),
                            'event': '关闭观测且无echo进程启动'})
with Session('fixed-blue', 'fixed_team.launch.py', 'robot:=blue') as session:
    session.wait_text('Observer exited; heartbeat keeps running.')
    check('观测重映射练习', {'nodes': nodes('/blue/heartbeat'),
                          'message': echo('/blue/health', 'team ready')})
with Session('multi', 'multi.launch.py'):
    check('分组命名空间', {'nodes': nodes('/red/sensors/heartbeat', '/blue/sensors/heartbeat'),
                         'red': echo('/red/sensors/health', 'red ready'),
                         'blue': echo('/blue/sensors/health', 'blue ready')})
with Session('three', 'three.launch.py'):
    data = {'nodes': nodes(*(f'/{name}/camera/heartbeat' for name in ['red', 'blue', 'green']))}
    data.update({name: echo(f'/{name}/camera/health', name + ' ready') for name in ['red', 'blue', 'green']})
    check('三组相对名字练习', data)
with Session('three-absolute', 'three_absolute.launch.py'):
    out = run(['ros2', 'topic', 'info', '/health', '-v'])
    assert 'Publisher count: 3' in out, out
    check('绝对话题反例', {'topic_info': out})
with Session('checked', 'checked.launch.py', 'robot:=blue') as session:
    session.wait_text('Using parameters:')
    check('OpaqueFunction成功路径', {'nodes': nodes('/blue/heartbeat'),
                                  'message': echo('/blue/health', 'checked ready')})
missing = work / 'definitely-absent.yaml'
assert not missing.exists()
result = subprocess.run(['ros2', 'launch', 'training_tools', 'checked.launch.py',
                         'params_file:=' + str(missing)], cwd=work, env=os.environ,
                        capture_output=True, text=True, timeout=15)
output = result.stdout + result.stderr
(evidence / 'checked-missing.txt').write_text(output)
assert result.returncode != 0 and '参数文件不存在' in output, output
assert 'process started' not in output, output
check('OpaqueFunction缺失文件负例', {'returncode': result.returncode, 'output': output})
# 本轮通常在1.5秒内结束，故不用持续运行的 Session.__enter__。
shutdown_run = Session('shutdown', 'shutdown_team.launch.py')
try:
    shutdown_run.proc.wait(timeout=20)
    assert shutdown_run.proc.returncode == 0, shutdown_run.log()
    out = nodes()
    assert '/red/heartbeat' not in out.splitlines(), out
    assert 'process has finished cleanly' in shutdown_run.log(), shutdown_run.log()
    check('Shutdown退出练习', {'returncode': 0, 'remaining_nodes': out})
finally:
    shutdown_run.__exit__()
check('构建与ament测试', {'build': 'build.txt', 'test': 'ament-test.txt'})
