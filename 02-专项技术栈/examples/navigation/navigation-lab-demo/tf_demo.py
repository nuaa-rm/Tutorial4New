"""在真实tf2 Buffer中合成两个变换，并查询一条缺失分支。"""
import json
import math
import rclpy
from geometry_msgs.msg import TransformStamped
from tf2_ros import Buffer, TransformException

rclpy.init()
node = rclpy.create_node("tf_buffer_demo")
buffer = Buffer(node=node)
for parent, child, x, y, yaw in (("demo_map", "demo_odom", 1, 2, math.pi/2),
                               ("demo_odom", "demo_base", 2, 0, 0)):
    t = TransformStamped()
    t.header.stamp = node.get_clock().now().to_msg()
    t.header.frame_id, t.child_frame_id = parent, child
    t.transform.translation.x, t.transform.translation.y = float(x), float(y)
    t.transform.rotation.z = math.sin(yaw/2)
    t.transform.rotation.w = math.cos(yaw/2)
    buffer.set_transform_static(t, "textbook")
t = buffer.lookup_transform("demo_map", "demo_base", rclpy.time.Time())
result = {"xy": [t.transform.translation.x, t.transform.translation.y]}
try:
    buffer.lookup_transform("demo_map", "missing_laser", rclpy.time.Time())
except TransformException as error:
    result["missing"] = type(error).__name__
print(json.dumps(result))
node.destroy_node(); rclpy.shutdown()
