"""最小教学驱动：回放原图，保存/重载参数；不模拟曝光硬件。"""
import argparse
import copy
import time
from pathlib import Path
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from sensor_msgs.srv import SetCameraInfo
from model_io import load_yaml, save_matrices

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--images", type=Path, default=Path("data/train"))
cli.add_argument("--yaml", type=Path, default=Path("out/ros-front.yaml"))
cli.add_argument("--namespace", default="camera")
cli.add_argument("--period", type=float, default=.5)
cli.add_argument("--right", type=Path)
cli.add_argument("--no-service", action="store_true")
args, ros_args = cli.parse_known_args()
if not np.isfinite(args.period) or args.period <= 0:
    cli.error("换图周期须为正有限秒数")


class Replay(Node):
    def __init__(self):
        super().__init__("camera_replay")
        paths = sorted(args.images.glob("*.png"))
        if not paths:
            raise ValueError("没有输入 PNG")
        self.frames = [cv2.imread(str(p), cv2.IMREAD_GRAYSCALE) for p in paths]
        if any(f is None or f.shape != (480, 640) for f in self.frames):
            raise ValueError("本回放固定 640×480 mono8")
        self.sides = []
        specs = [(args.namespace, args.yaml, self.frames)]
        if args.right:
            right = [cv2.imread(str(args.right / p.name), cv2.IMREAD_GRAYSCALE) for p in paths]
            if any(f is None or f.shape != (480, 640) for f in right):
                raise ValueError("右图缺失或尺寸不同")
            specs.append(("right", args.yaml.with_name(args.yaml.stem+"_right.yaml"), right))
        for ns, path, frames in specs:
            ns = "/" + ns.strip("/")
            info = CameraInfo(width=640, height=480)
            if path.exists():
                K, D, R, P, size = load_yaml(path)
                if size != (640, 480):
                    raise ValueError("YAML 尺寸与回放不同")
                info.k = K.reshape(-1).tolist(); info.d = D.tolist()
                info.r = R.reshape(-1).tolist(); info.p = P.reshape(-1).tolist()
                info.distortion_model = "plumb_bob"
            entry = [path, info, frames, self.create_publisher(Image, ns+"/image_raw", 10),
                     self.create_publisher(CameraInfo, ns+"/camera_info", 10)]
            self.sides.append(entry)
            if not args.no_service:
                self.create_service(SetCameraInfo, ns+"/set_camera_info",
                                    lambda req, rsp, side=entry: self.store(req, rsp, side))
        self.start = time.monotonic()
        self.create_timer(.1, self.publish)

    def store(self, req, rsp, side):
        info = req.camera_info
        try:
            if (info.width, info.height) != (640, 480) or info.distortion_model != "plumb_bob":
                raise ValueError("要求 640×480 plumb_bob")
            K = np.array(info.k).reshape(3, 3); D = np.array(info.d)
            R = np.array(info.r).reshape(3, 3); P = np.array(info.p).reshape(3, 4)
            if len(D) != 5 or K[0, 0] <= 0 or K[1, 1] <= 0:
                raise ValueError("畸变数量或焦距无效")
            if not all(np.isfinite(a).all() for a in (K, D, R, P)):
                raise ValueError("参数必须有限")
            save_matrices(side[0], K, D, R, P, (640, 480), "front")
            side[1] = copy.deepcopy(info)
            rsp.success = True; rsp.status_message = "已保存并更新回放参数"
        except (ValueError, OSError) as error:
            rsp.success = False; rsp.status_message = str(error)
        return rsp

    def publish(self):
        index = int((time.monotonic()-self.start)/args.period) % len(self.frames)
        stamp = self.get_clock().now().to_msg()
        for path, info, frames, images, infos in self.sides:
            message = Image(height=480, width=640, encoding="mono8", step=640)
            message.header.stamp = stamp
            message.header.frame_id = images.topic_name.split("/")[1]+"_optical_frame"
            message.data = frames[index].tobytes()
            current = copy.deepcopy(info); current.header = message.header
            images.publish(message); infos.publish(current)


rclpy.init(args=ros_args)
node = None
try:
    node = Replay()
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    if node: node.destroy_node()
    if rclpy.ok(): rclpy.shutdown()
