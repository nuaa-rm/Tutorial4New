"""只在软件中积分Twist；不连接真实电机或传感器。"""
import math
import time
import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster

rclpy.init(); node = rclpy.create_node("textbook_sim")
dynamic = TransformBroadcaster(node); static = StaticTransformBroadcaster(node)
t = TransformStamped(); t.header.frame_id = "map"; t.child_frame_id = "odom"
t.header.stamp = node.get_clock().now().to_msg(); t.transform.rotation.w = 1.
static.sendTransform(t)
pub = node.create_publisher(Odometry, "odom", 10)
x, y, yaw, v, w = .55, .55, 0., 0., 0.
last, command_time = time.monotonic(), 0.


def command(msg):
    global v, w, command_time
    v, w, command_time = msg.linear.x, msg.angular.z, time.monotonic()


def update():
    global x, y, yaw, last, v, w
    now = time.monotonic(); dt = now-last; last = now
    if now-command_time > .5:
        v, w = 0., 0.  # 断流停软件模型，不表示真实底盘已有此保护。
    x += v*math.cos(yaw)*dt; y += v*math.sin(yaw)*dt; yaw += w*dt
    t = TransformStamped(); t.header.stamp = node.get_clock().now().to_msg()
    t.header.frame_id, t.child_frame_id = "odom", "base_link"
    t.transform.translation.x, t.transform.translation.y = x, y
    t.transform.rotation.z, t.transform.rotation.w = math.sin(yaw/2), math.cos(yaw/2)
    dynamic.sendTransform(t)
    msg = Odometry(); msg.header = t.header; msg.child_frame_id = "base_link"
    msg.pose.pose.position.x, msg.pose.pose.position.y = x, y
    msg.pose.pose.orientation = t.transform.rotation
    msg.twist.twist.linear.x, msg.twist.twist.angular.z = v, w
    pub.publish(msg)


node.create_subscription(Twist, "cmd_vel", command, 10)
node.create_timer(.05, update)
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node(); rclpy.try_shutdown()
