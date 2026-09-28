"""将固定外部帧转换成米；--ros 用真实 rclpy 发布转换结果。"""
import argparse
import struct
from framing import LengthParser, encode_length


def decode_distance():
    wire = encode_length(struct.pack(">HH", 8, 1250))
    parser, frames = LengthParser(), []
    for chunk in [wire[:2], wire[2:]]:
        frames.extend(parser.feed(chunk))
    sequence, millimeters = struct.unpack(">HH", frames[0])
    return sequence, millimeters / 1000.0


def publish_ros():
    import rclpy
    from std_msgs.msg import Float64
    rclpy.init()
    node = rclpy.create_node("distance_bridge_demo")
    publisher = node.create_publisher(Float64, "range_m", 10)
    def send():
        sequence, meters = decode_distance()
        publisher.publish(Float64(data=meters))
        node.get_logger().info(f"seq={sequence}, range_m={meters}")
    timer = node.create_timer(0.5, send)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        timer.cancel()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--ros", action="store_true")
    args = cli.parse_args()
    if args.ros:
        publish_ros()
    else:
        print("seq、距离（米）:", decode_distance())
