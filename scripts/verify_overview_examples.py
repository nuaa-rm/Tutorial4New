#!/usr/bin/env python3
"""按正文运行接口演示，独立核对含义/时效，并保存纸面演练产物。"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument('--project', type=Path, required=True)
cli.add_argument('--evidence', type=Path, required=True)
a = cli.parse_args(); p = a.project.resolve(); records = []
def record(name, details): records.append({'name': name, 'status': 'PASS', 'details': details})
for name, opts, decision, reason in [
    ('默认消息', [], 'accept', None),
    ('仅发送端改度', ['--unit', 'deg'], 'hold', 'unit mismatch'),
    ('过期101', ['--age-ms', '101'], 'hold', 'time invalid'),
    ('无效观测', ['--invalid'], 'hold', 'observation invalid'),
    ('负角度', ['--delta', '-0.1'], 'accept', None),
    ('边界100', ['--age-ms', '100'], 'accept', None),
    ('未来时间', ['--age-ms', '-1'], 'hold', 'time invalid'),
    ('相机坐标系', ['--frame', 'camera'], 'hold', 'frame mismatch'),
    ('非有限值', ['--delta', 'nan'], 'hold', 'invalid number')]:
    command = [sys.executable, str(p/'receiver.py'), *opts]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout); assert data['decision'] == decision
    if reason: assert data['reason'] == reason
    else:
        delta = -0.1 if name == '负角度' else 0.1
        assert abs(data['delta_deg'] - delta*180/math.pi) < 1e-12
        assert data['age_ms'] == (100 if name == '边界100' else 80)
    record(name, {'command': command, 'stdout': data})
sys.path.insert(0, str(p)); from receiver import interpret
card = json.loads((p/'card.json').read_text())
for key, value in [('clock', 'other_clock'), ('version', 2)]:
    variant = copy.deepcopy(card); variant['message'][key] = value
    data = interpret(variant, 100); assert data['reason'] == key + ' mismatch'
    record('消息约定 '+key, data)
variant = copy.deepcopy(card)
variant['message']['unit'] = variant['contract']['unit'] = 'deg'
data = interpret(variant, 100); assert data['reason'] == 'unsupported contract'
record('两端改度仍需修改实现', data)
variant = copy.deepcopy(card); variant['message']['delta_yaw'] = True
assert interpret(variant, 100)['reason'] == 'invalid number'
record('布尔值不是角度', {'delta_yaw': True, 'result': interpret(variant, 100)})
root = p.parents[2]
entries = [('chapters/E_camera.tex', '相机与成像'), ('chapters/G_ba.tex', '几何'), ('chapters/F_filter.tex', '滤波')]
for entry, topic in entries:
    source = root/'02-专项技术栈'/entry
    text = source.read_text(); assert text
    record('实际打开专项入口 '+topic, {'path': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'first_line': text.splitlines()[0]})
artifacts = {
 '路线': ['图像:像素阵列', '网络框:像素坐标', '灯条角点:像素坐标', '位姿:旋转和平移/相机系'],
 '分工': {'跟随装甲转云台': '自瞄', '绕开障碍到补给点': '导航', '共享全场目标位置': '雷达', '网络识别装甲': '待确认输出用途'},
 '帧42': ['图像', '角点/px', '相机系位置/m', '带时间戳状态', '云台水平增量/rad'],
 '接口': {'来源': 'chapters/01_overview.tex 云台目标角需求', '发送': '视觉', '接收': '电控', 'unit': 'rad', 'frame': 'gimbal_delta_left_positive', 'clock': 'demo_clock', '实车发送频率': '待双方确认', '真实失效动作': '待双方确认', '性质': '教学设计，不是现行队内协议'}
}
record('纸面演练已填写', artifacts)
record('90度核对', {'degree': 90, 'radian': math.pi/2, 'only_receiver_still_deg': math.pi/2})
a.evidence.parent.mkdir(parents=True, exist_ok=True)
data = {'python': platform.python_version(), 'platform': platform.platform(), 'files': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name != '.gitignore'}, 'records': records, 'boundaries': ['纸面演练由修订者填写，未冒充两人现场考核', '不连接真实执行器；真实协议、时钟、频率、失效动作待队内确认']}
a.evidence.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
print(len(records), 'records passed', a.evidence)
