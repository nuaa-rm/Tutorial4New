"""MarkerArray：移动球、方向箭头、轨迹和文字。"""
from builtin_interfaces.msg import Duration
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray


def make_markers(pose, path, visible=True):
    def base(marker_id, kind):
        marker = Marker()
        marker.header = pose.header
        marker.ns, marker.id = 'target', marker_id
        marker.type, marker.action = kind, Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.color = ColorRGBA(r=0.1, g=0.7, b=1.0, a=1.0)
        marker.lifetime = Duration(sec=0, nanosec=500000000)
        return marker

    sphere = base(0, Marker.SPHERE)
    sphere.pose = pose.pose
    sphere.scale.x = sphere.scale.y = sphere.scale.z = 0.25
    if not visible:
        sphere.action = Marker.DELETE

    arrow = base(1, Marker.ARROW)
    p = pose.pose.position
    # points 写起点和终点；这里的 scale 表示箭杆、箭头直径及头长。
    arrow.points = [p, Point(x=p.x - 0.4 * p.y,
                             y=p.y + 0.4 * p.x, z=p.z)]
    arrow.scale.x, arrow.scale.y, arrow.scale.z = 0.04, 0.08, 0.12

    line = base(2, Marker.LINE_STRIP)
    line.points = [item.pose.position for item in path.poses]
    line.scale.x = 0.02
    line.color = ColorRGBA(r=1.0, g=0.8, b=0.1, a=1.0)

    text = base(3, Marker.TEXT_VIEW_FACING)
    text.pose.position = Point(x=p.x, y=p.y, z=p.z + 0.35)
    text.scale.z = 0.18
    text.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)
    text.text = 'target'
    return MarkerArray(markers=[sphere, arrow, line, text])
