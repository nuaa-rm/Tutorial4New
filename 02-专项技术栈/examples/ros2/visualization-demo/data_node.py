#!/usr/bin/env python3
"""用同一组数据练习曲线、图像、三维图形和图像标注。"""
import math
from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TransformStamped, TwistStamped
from nav_msgs.msg import Path
from sensor_msgs.msg import Image
from std_msgs.msg import Float64
from tf2_ros import TransformBroadcaster
from visualization_msgs.msg import MarkerArray
from foxglove_msgs.msg import ImageAnnotations, SceneUpdate

from markers import make_markers
from annotations import make_annotations
from scene import make_scene


class VisualizationDemo(Node):
    def __init__(self):
        super().__init__('viz_demo')
        self.declare_parameter('show_target', True)
        types = {'signal': Float64, 'pose': PoseStamped,
                 'twist': TwistStamped, 'path': Path, 'image': Image,
                 'markers': MarkerArray, 'annotations': ImageAnnotations,
                 'scene': SceneUpdate}
        self.pubs = {name: self.create_publisher(kind, '/viz/' + name, 10)
                     for name, kind in types.items()}
        self.tf = TransformBroadcaster(self)
        self.history = deque(maxlen=120)
        self.start = self.get_clock().now()
        self.background = bytes([30, 45, 60]) * (640 * 360)
        self.timer = self.create_timer(0.1, self.tick)

    def tick(self):
        now = self.get_clock().now()
        stamp = now.to_msg()
        t = (now - self.start).nanoseconds / 1e9
        signal = Float64(data=math.sin(t))
        self.pubs['signal'].publish(signal)

        # 位置在 map 中绕一米半径的圆，朝向沿着圆的切线。
        pose = PoseStamped()
        pose.header.stamp, pose.header.frame_id = stamp, 'map'
        pose.pose.position.x = math.cos(t)
        pose.pose.position.y = math.sin(t)
        pose.pose.position.z = 0.4
        yaw = t + math.pi / 2
        pose.pose.orientation.z = math.sin(yaw / 2)
        pose.pose.orientation.w = math.cos(yaw / 2)
        self.pubs['pose'].publish(pose)

        twist = TwistStamped()
        twist.header = pose.header
        twist.twist.linear.x = -math.sin(t)
        twist.twist.linear.y = math.cos(t)
        twist.twist.angular.z = 1.0
        self.pubs['twist'].publish(twist)

        transform = TransformStamped()
        transform.header = pose.header
        transform.child_frame_id = 'target'
        p = pose.pose.position
        transform.transform.translation.x = p.x
        transform.transform.translation.y = p.y
        transform.transform.translation.z = p.z
        transform.transform.rotation = pose.pose.orientation
        self.tf.sendTransform(transform)
        self.history.append(pose)
        path = Path(header=pose.header, poses=list(self.history))
        self.pubs['path'].publish(path)
        visible = self.get_parameter('show_target').value
        self.pubs['markers'].publish(make_markers(pose, path, visible))
        self.pubs['scene'].publish(make_scene(pose))

        # 直接填充 rgb8 像素；图像上只有色块，检测框另发标注消息。
        cx, cy = 320 + int(160 * math.sin(t)), 180
        pixels = bytearray(self.background)
        for y in range(cy - 30, cy + 30):
            offset = (y * 640 + cx - 40) * 3
            pixels[offset:offset + 80 * 3] = bytes([20, 180, 100]) * 80
        image = Image()
        image.header.stamp, image.header.frame_id = stamp, 'camera_optical'
        image.height, image.width = 360, 640
        image.encoding, image.is_bigendian, image.step = 'rgb8', 0, 640 * 3
        image.data = bytes(pixels)
        self.pubs['image'].publish(image)
        self.pubs['annotations'].publish(make_annotations(stamp, cx, cy))


def main():
    rclpy.init()
    node = VisualizationDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
