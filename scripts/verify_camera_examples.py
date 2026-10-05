#!/usr/bin/env python3
"""在 Ubuntu/Humble 中核验数值、棋盘格求解、服务持久化和 image_proc。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import cv2
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument('--project', type=Path, required=True)
cli.add_argument('--work', type=Path, required=True)
cli.add_argument('--evidence', type=Path, required=True)
args = cli.parse_args()
if os.environ.get('ROS_DISTRO') != 'humble':
    raise SystemExit('请先 source /opt/ros/humble/setup.bash')
project = args.project.resolve(); args.work.mkdir(parents=True, exist_ok=True)
records = []

def record(name, details):
    records.append({'name': name, 'status': 'PASS', 'details': details})

def run(name, file, *options, expect=0):
    result = subprocess.run([sys.executable, str(project/file), *map(str, options)],
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == expect or expect == -1 and result.returncode != 0, result.stderr
    if expect == 0:
        data = json.loads(result.stdout)
    else:
        data = {'exit': result.returncode, 'stderr': result.stderr[-1200:]}
    record(name, data); return data

data = args.work/'data'; model = args.work/'model'; front = args.work/'front'
run('生成固定种子的模拟照片', 'generate.py', '--output', data)
metrics = run('多姿态标定', 'calibrate.py', '--images', data/'train', '--output', model)
assert metrics['K'][0][0] < 570 and metrics['K'][0][0] > 550
bad = run('只有正面仍可能低 RMS', 'calibrate.py', '--images', data/'front', '--output', front)
assert bad['rms_px'] < .3 and bad['K'][0][0] > 2000
run('独立照片固定内参', 'validate.py', '--image', data/'validation/000.png',
    '--model', model/'model.npz', '--output', args.work/'validation')
run('正面模型独立验证', 'validate.py', '--image', data/'validation/000.png',
    '--model', front/'model.npz', '--output', args.work/'front-validation')
run('另一个未参与拟合的姿态', 'validate.py', '--image', data/'validation/007.png',
    '--model', model/'model.npz', '--output', args.work/'validation-007')
run('方格单位放大千倍', 'calibrate.py', '--images', data/'train', '--square', '25',
    '--output', args.work/'scale')
a = np.load(model/'model.npz'); b = np.load(args.work/'scale/model.npz')
assert np.allclose(a['K'], b['K'], rtol=1e-4)
assert np.allclose(b['tvecs']/a['tvecs'], 1000, rtol=.003)
record('单位误填的参数和位姿尺度', {'K_max_abs': float(np.max(abs(a['K']-b['K']))),
                                   'translation_ratio_median': float(np.median(b['tvecs']/a['tvecs']))})
run('负方格被拒绝', 'calibrate.py', '--square', '-1', expect=-1)
run('15 张不同姿态可求解', 'calibrate.py', '--images', data/'validation', '--output', args.work/'fewer',
    expect=0)  # 15 张足够；另建一个只有 1 张的目录。
small = args.work/'one'; small.mkdir(exist_ok=True)
(small/'000.png').write_bytes((data/'train/001.png').read_bytes())
run('单张照片被拒绝', 'calibrate.py', '--images', small, '--output', args.work/'one-out', expect=-1)
for gamma in (2.2, 1., .5):
    r = run('Bayer 与 Gamma '+str(gamma), 'format_gamma.py', '--gamma', gamma,
            '--output', args.work/('format-'+str(gamma)))
    assert r['center_bgr'] == [50, 100, 200]
run('无效 Gamma 被拒绝', 'format_gamma.py', '--gamma', '0', expect=-1)
for photons in (100, 400, 900):
    run('光子计数 '+str(photons), 'noise.py', '--photons', photons,
        '--output', args.work/('noise-'+str(photons)))
run('默认景深和曝光', 'optics.py')
run('收小光圈', 'optics.py', '--aperture', '8')
run('远界为无穷', 'optics.py', '--distance', '7000')
run('曝光预算 0.5ms', 'optics.py', '--speed', '1200', '--budget', '.6')
run('无效曝光参数', 'optics.py', '--speed', '0', expect=-1)
run('双目几何与纵向残差', 'stereo.py', '--data', data, '--model', model/'front.yaml',
    '--output', args.work/'stereo')

sys.path.insert(0, str(project))
from model_io import load_yaml, save_matrices
K, D, R, P, size = load_yaml(model/'front.yaml')
record('YAML 矩阵往返', {'size': size, 'K': K.tolist(), 'D': D.tolist()})
invalid = args.work/'invalid.yaml'
save_matrices(invalid, K*0, D, R, P, size, 'bad')
try: load_yaml(invalid)
except ValueError as error: record('零焦距 YAML 被拒绝', str(error))
else: raise AssertionError('零焦距未拒绝')

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
from sensor_msgs.srv import SetCameraInfo
from rclpy.qos import qos_profile_sensor_data
env = dict(os.environ, ROS_DOMAIN_ID='186', ROS_LOCALHOST_ONLY='1',
           ROS_LOG_DIR=str(args.work/'ros-logs'))
os.environ.update({key: env[key] for key in ('ROS_DOMAIN_ID','ROS_LOCALHOST_ONLY','ROS_LOG_DIR')})
processes = []; logs = []
def start(command, name):
    log = (args.work/(name+'.txt')).open('w'); logs.append(log)
    proc = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    processes.append(proc); return proc
def stop(proc):
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try: proc.wait(timeout=8)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait()
def until(test, seconds=15):
    deadline = time.monotonic()+seconds
    while not test():
        assert time.monotonic() < deadline, 'ROS 等待超时'
        rclpy.spin_once(node, timeout_sec=.1)
saved = args.work/'service.yaml'
if saved.exists(): saved.unlink()
rclpy.init(); node = Node('camera_verification')
seen = {}; node.create_subscription(CameraInfo, '/camera/camera_info',
    lambda msg: seen.update(info=msg), qos_profile_sensor_data)
def publisher(*extra):
    return start([sys.executable, str(project/'replay_ros.py'), '--images', str(data/'train'),
                  '--yaml', str(saved), *extra], 'publisher-'+str(len(processes)))
try:
    pub = publisher(); until(lambda: 'info' in seen)
    assert seen['info'].k[0] == 0
    record('未标定 CameraInfo', {'K00': seen['info'].k[0], 'size': [seen['info'].width, seen['info'].height]})
    client = node.create_client(SetCameraInfo, '/camera/set_camera_info')
    assert client.wait_for_service(timeout_sec=15)
    def store(info):
        future = client.call_async(SetCameraInfo.Request(camera_info=info))
        until(future.done); return future.result()
    rejected = store(CameraInfo(width=320,height=240))
    assert not rejected.success and not saved.exists()
    record('服务拒绝不匹配的尺寸', {'success': rejected.success, 'message': rejected.status_message})
    info = CameraInfo(width=640, height=480, distortion_model='plumb_bob',
                      k=K.reshape(-1).tolist(), d=D.tolist(), r=R.reshape(-1).tolist(), p=P.reshape(-1).tolist())
    accepted = store(info); assert accepted.success and saved.exists()
    record('SetCameraInfo 实际持久保存', accepted.status_message)
    before = hashlib.sha256(saved.read_bytes()).hexdigest()
    rejected = store(CameraInfo(width=640, height=480, distortion_model='plumb_bob'))
    assert not rejected.success and hashlib.sha256(saved.read_bytes()).hexdigest() == before
    record('无效参数不覆盖原存档', {'success': rejected.success, 'same_sha256': before})
    stop(pub); seen.clear(); pub = publisher()
    until(lambda: 'info' in seen and seen['info'].k[0] > 0)
    assert np.allclose(seen['info'].k, K.reshape(-1)) and np.allclose(seen['info'].d, D)
    record('重启后实际加载', {'K00': seen['info'].k[0], 'D': list(seen['info'].d)})
    rect = start(['ros2','launch','image_proc','image_proc.launch.py','namespace:=camera'], 'image-proc')
    run('真实 image_proc 配对与逐像素比较', 'check_ros.py', '--output', args.work/'ros-check')
    stop(rect); stop(pub)
    pub = publisher('--no-service')
    deadline = time.monotonic()+10
    while client.service_is_ready() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=.1)
    assert not client.service_is_ready()
    record('仅回放没有写入服务', {'service_ready': client.service_is_ready()})
    stop(pub)
    pairs = {}
    for side in ('left','right'):
        node.create_subscription(Image, '/'+side+'/image_raw',
            lambda msg, s=side: pairs.update({s: msg}), qos_profile_sensor_data)
    stereo = start([sys.executable, str(project/'replay_ros.py'), '--images', str(data/'left'),
        '--right', str(data/'right'), '--namespace','left','--yaml',str(args.work/'pair.yaml')], 'stereo-pub')
    until(lambda: len(pairs)==2 and pairs['left'].header.stamp == pairs['right'].header.stamp)
    assert pairs['left'].header.frame_id == 'left_optical_frame'
    assert pairs['right'].header.frame_id == 'right_optical_frame'
    record('双目回放同时间戳', {'stamp': str(pairs['left'].header.stamp),
                              'frames': [pairs[s].header.frame_id for s in ('left','right')]})
finally:
    for proc in reversed(processes): stop(proc)
    node.destroy_node(); rclpy.shutdown()
    for log in logs: log.close()
versions = {'python': sys.version, 'opencv': cv2.__version__, 'numpy': np.__version__,
            'ros_distro': os.environ.get('ROS_DISTRO'), 'video_devices': list(map(str, Path('/dev').glob('video*')))}
args.evidence.parent.mkdir(parents=True, exist_ok=True)
args.evidence.write_text(json.dumps({'versions': versions,
    'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(project.glob('*.py'))},
    'records': records, 'physical_camera_verified': False}, ensure_ascii=False, indent=2))
print(json.dumps({'records': len(records), 'evidence': str(args.evidence)}, ensure_ascii=False))
