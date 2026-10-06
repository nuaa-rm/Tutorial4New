import copy
import rclpy
from rclpy.node import Node
from foxglove_msgs.msg import ImageAnnotations


class ShiftAnnotations(Node):
    def __init__(self):
        super().__init__('viz_annotation_offset_test')
        self.publisher = self.create_publisher(ImageAnnotations, '/viz/annotations_shifted', 10)
        self.subscriber = self.create_subscription(ImageAnnotations, '/viz/annotations', self.receive, 10)
        self.count = 0

    def receive(self, message):
        shifted = copy.deepcopy(message)
        stamps = [item.timestamp for items in (shifted.points, shifted.circles, shifted.texts) for item in items]
        if hasattr(shifted, 'timestamp'):
            stamps.append(shifted.timestamp)
        for stamp in stamps:
            stamp.sec, stamp.nanosec = divmod(stamp.sec * 1000000000 + stamp.nanosec + 50000000, 1000000000)
        self.publisher.publish(shifted)
        self.count += 1
        if self.count % 50 == 0:
            print(f'{self.count} annotation messages shifted by 50000000 ns', flush=True)


rclpy.init()
node = ShiftAnnotations()
try:
    rclpy.spin(node)
except KeyboardInterrupt:
    pass
finally:
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()
