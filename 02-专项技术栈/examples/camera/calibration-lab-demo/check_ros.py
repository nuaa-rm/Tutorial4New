"""核对 image_proc 实际输出与相同模型的 remap。"""
import argparse
import json
import time
from pathlib import Path
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from rclpy.qos import qos_profile_sensor_data

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--namespace", default="camera")
cli.add_argument("--output", type=Path, default=Path("out/ros-check"))
args, ros_args = cli.parse_known_args()
rclpy.init(args=ros_args)
node = Node("rectification_check")
cache = {}


def receive(kind, message):
    key = (message.header.stamp.sec, message.header.stamp.nanosec)
    cache.setdefault(key, {})[kind] = message
    while len(cache) > 30:
        del cache[next(iter(cache))]


for kind, cls, topic in (("raw", Image, "image_raw"), ("rect", Image, "image_rect"),
                         ("info", CameraInfo, "camera_info")):
    node.create_subscription(cls, f"/{args.namespace}/{topic}",
                             lambda msg, k=kind: receive(k, msg), qos_profile_sensor_data)
deadline = time.monotonic()+15
pair = None
while rclpy.ok() and time.monotonic() < deadline:
    rclpy.spin_once(node, timeout_sec=.1)
    pair = next((p for p in cache.values() if len(p) == 3), None)
    if pair: break
if not pair:
    raise TimeoutError("未收到时间戳匹配的原图、参数和校正图")
raw, rect, info = pair["raw"], pair["rect"], pair["info"]
assert raw.encoding == rect.encoding == "mono8" and raw.step == rect.step == 640
assert raw.header.frame_id == rect.header.frame_id == info.header.frame_id
K = np.array(info.k).reshape(3, 3); P = np.array(info.p).reshape(3, 4)
maps = cv2.initUndistortRectifyMap(K, np.array(info.d), np.array(info.r).reshape(3, 3),
                                  P[:, :3], (640, 480), cv2.CV_32FC1)
a = np.frombuffer(bytes(raw.data), np.uint8).reshape(480, 640)
b = np.frombuffer(bytes(rect.data), np.uint8).reshape(480, 640)
expected = cv2.remap(a, *maps, cv2.INTER_LINEAR)
error = int(np.max(np.abs(b.astype(int)-expected.astype(int))))
assert error <= 1, f"与相同模型的 remap 不符：{error}"
args.output.mkdir(parents=True, exist_ok=True)
for name, image in (("raw.png", a), ("rectified.png", b)):
    assert cv2.imwrite(str(args.output / name), image)
print(json.dumps({"matched_stamp": [raw.header.stamp.sec, raw.header.stamp.nanosec],
                  "frame_id": raw.header.frame_id, "max_abs": error, "K00": info.k[0],
                  "D": list(info.d), "size": [info.width, info.height], "encoding": rect.encoding}))
node.destroy_node(); rclpy.shutdown()
