#!/usr/bin/env python3
"""在加载 Humble 的终端验证图形化示例的数据、桥接和 MCAP；不代替面板点击验收。"""
import argparse
import asyncio
from collections import Counter, defaultdict
import json
import math
import os
from pathlib import Path
import signal
import struct
import subprocess
import time

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.srv import SetParameters
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import rosbag2_py
import websockets

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / '02-专项技术栈/examples/ros2/visualization-demo'
TOPICS = {
    '/viz/signal': 'std_msgs/msg/Float64',
    '/viz/pose': 'geometry_msgs/msg/PoseStamped',
    '/viz/twist': 'geometry_msgs/msg/TwistStamped',
    '/viz/path': 'nav_msgs/msg/Path',
    '/viz/image': 'sensor_msgs/msg/Image',
    '/viz/markers': 'visualization_msgs/msg/MarkerArray',
    '/viz/annotations': 'foxglove_msgs/msg/ImageAnnotations',
    '/viz/scene': 'foxglove_msgs/msg/SceneUpdate',
    '/tf': 'tf2_msgs/msg/TFMessage',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert os.environ.get('ROS_DISTRO') == 'humble'
    processes, handles = [], []

    def launch(name, command):
        log = (out / f'{name}.txt').open('w')
        handles.append(log)
        process = subprocess.Popen(command, cwd=DEMO, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        processes.append(process)
        return process

    def stop(process):
        if process.poll() is None:
            # ros2 launch 自己会给子进程转发信号，避免对子进程重复发送。
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)

    rclpy.init()
    node = Node('verify_visualization')
    received = defaultdict(list)
    subscriptions = [node.create_subscription(get_message(kind), topic,
                     lambda msg, topic=topic: received[topic].append(msg), 10)
                     for topic, kind in TOPICS.items()]

    def until(predicate, timeout=12):
        end = time.monotonic() + timeout
        while not predicate():
            if time.monotonic() > end:
                raise AssertionError('等待数据或服务超时')
            rclpy.spin_once(node, timeout_sec=0.05)

    checks = {}
    try:
        data = launch('data', ['python3', str(DEMO / 'data_node.py')])
        until(lambda: all(len(received[t]) >= 20 for t in TOPICS))
        checks['all_topics_received'] = {t: len(received[t]) for t in TOPICS}
        pose = received['/viz/pose'][-1]
        p, q = pose.pose.position, pose.pose.orientation
        assert abs(p.x * p.x + p.y * p.y - 1) < 1e-8
        assert abs(q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w - 1) < 1e-8
        speed = received['/viz/twist'][-1].twist.linear
        assert abs(math.hypot(speed.x, speed.y) - 1) < 1e-8
        checks['pose_and_speed'] = '单位四元数、1 m 圆与 1 m/s 速度通过'

        def stamp_tuple(stamp):
            return stamp.sec, stamp.nanosec
        images = {stamp_tuple(m.header.stamp): m for m in received['/viz/image']}
        matches = 0
        for annotation in received['/viz/annotations']:
            key = stamp_tuple(annotation.points[0].timestamp)
            if key not in images:
                continue
            image = images[key]
            assert (image.width, image.height, image.step, image.encoding) == (640,360,1920,'rgb8')
            assert len(image.data) == image.height * image.step
            center = annotation.circles[0].position
            offset = (int(center.y) * image.width + int(center.x)) * 3
            assert list(image.data[offset:offset+3]) == [20,180,100]
            assert list(image.data[:3]) == [30,45,60]
            assert stamp_tuple(annotation.texts[0].timestamp) == key
            if hasattr(annotation, 'timestamp'):
                assert stamp_tuple(annotation.timestamp) == key
            matches += 1
        assert matches >= 10
        checks['image_annotation_pairs'] = matches
        checks['tf'] = received['/tf'][-1].transforms[0].child_frame_id
        assert checks['tf'] == 'target'

        client = node.create_client(SetParameters, '/viz_demo/set_parameters')
        until(client.service_is_ready)
        for visible in [False, True]:
            request = SetParameters.Request(parameters=[
                Parameter('show_target', value=visible).to_parameter_msg()])
            future = client.call_async(request)
            until(future.done)
            assert all(result.successful for result in future.result().results)
            wanted = 0 if visible else 2
            until(lambda: received['/viz/markers'][-1].markers[0].action == wanted)
        checks['marker_delete_restore'] = True
        scene = received['/viz/scene'][-1].entities[0]
        assert scene.id == 'target' and len(scene.cubes) == len(scene.texts) == 1
        checks['scene_entity'] = True

        bridge = launch('bridge', ['ros2', 'launch', 'foxglove_bridge',
                         'foxglove_bridge_launch.xml', 'address:=127.0.0.1', 'port:=8765'])
        async def check_websocket():
            deadline = time.monotonic() + 15
            while True:
                try:
                    ws = await websockets.connect('ws://127.0.0.1:8765',
                         subprotocols=['foxglove.sdk.v1', 'foxglove.websocket.v1'],
                         max_size=2**24)
                    break
                except OSError:
                    if time.monotonic() > deadline:
                        raise
                    await asyncio.sleep(0.2)
            try:
                channels = {}
                while not all(t in channels for t in TOPICS):
                    msg = json.loads(await asyncio.wait_for(ws.recv(), 10))
                    if msg.get('op') == 'advertise':
                        channels.update({c['topic']:c for c in msg['channels']})
                ids = {n: topic for n,topic in enumerate(TOPICS,1)}
                await ws.send(json.dumps({'op':'subscribe','subscriptions':[
                    {'id':n,'channelId':channels[t]['id']} for n,t in ids.items()]}))
                decoded = {}
                while len(decoded) < len(TOPICS):
                    payload = await asyncio.wait_for(ws.recv(),10)
                    if isinstance(payload,bytes) and payload[0] == 1:
                        subscription_id = struct.unpack_from('<I',payload,1)[0]
                        topic = ids[subscription_id]
                        assert channels[topic]['encoding'] == 'cdr'
                        deserialize_message(payload[13:],get_message(TOPICS[topic]))
                        decoded[topic] = channels[topic]['schemaName']
                return decoded
            finally:
                await ws.close()
        checks['websocket_cdr'] = asyncio.run(check_websocket())

        bag = out / 'recording'
        if bag.exists():
            raise ValueError('录制目录已存在，请使用新的 --output')
        recorder = launch('record', ['ros2','bag','record','-s','mcap','-o',str(bag),*TOPICS])
        until(lambda: all(node.count_subscribers(t) >= 2 for t in TOPICS))
        end = time.monotonic() + 12
        while time.monotonic() < end:
            rclpy.spin_once(node,timeout_sec=0.05)
        stop(recorder)
        reader = rosbag2_py.SequentialReader()
        reader.open(rosbag2_py.StorageOptions(uri=str(bag),storage_id='mcap'),
                    rosbag2_py.ConverterOptions('cdr','cdr'))
        counts = Counter()
        recorded_times = []
        while reader.has_next():
            topic,payload,recorded_time = reader.read_next()
            deserialize_message(payload,get_message(TOPICS[topic]))
            counts[topic] += 1
            recorded_times.append(recorded_time)
        assert all(counts[t] >= 80 for t in TOPICS)
        duration = (max(recorded_times) - min(recorded_times)) / 1e9
        assert duration >= 10
        checks['mcap_duration_seconds'] = duration
        checks['mcap_deserialized_counts'] = dict(counts)
        # 只留下回放端，确认录制文件能重新进入实际 ROS 订阅链路。
        stop(bridge)
        stop(data)
        until(lambda: all(node.count_publishers(t) == 0 for t in TOPICS))
        # 先排空订阅队列，旧实时帧不能被误计入回放结果。
        drain_end = time.monotonic() + 2
        while time.monotonic() < drain_end:
            rclpy.spin_once(node, timeout_sec=0.02)
        received.clear()
        playback = launch('play', ['ros2', 'bag', 'play', str(bag)])
        until(lambda: playback.poll() is not None, timeout=20)
        assert playback.returncode == 0
        until(lambda: all(len(received[t]) >= counts[t] * 0.9 for t in TOPICS))
        assert all(len(received[t]) <= counts[t] for t in TOPICS)
        checks['mcap_replay_counts'] = {t: len(received[t]) for t in TOPICS}
        checks['status'] = 'passed'
    finally:
        for process in reversed(processes):
            stop(process)
        for handle in handles:
            handle.close()
        node.destroy_node()
        rclpy.shutdown()
        (out/'runtime.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(checks,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
