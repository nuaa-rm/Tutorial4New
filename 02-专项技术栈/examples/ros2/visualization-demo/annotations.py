"""二维检测框、中心点和文字，所有标注沿用原图时间戳。"""
from foxglove_msgs.msg import (ImageAnnotations, PointsAnnotation,
                               CircleAnnotation, TextAnnotation, Point2, Color)


def make_annotations(stamp, cx, cy):
    box = PointsAnnotation()
    box.timestamp, box.type = stamp, PointsAnnotation.LINE_LOOP
    box.points = [Point2(x=float(x), y=float(y)) for x, y in
                  [(cx - 40, cy - 30), (cx + 40, cy - 30),
                   (cx + 40, cy + 30), (cx - 40, cy + 30)]]
    box.outline_color = Color(r=1.0, g=0.8, b=0.1, a=1.0)
    box.thickness = 3.0

    center = CircleAnnotation()
    center.timestamp = stamp
    center.position = Point2(x=float(cx), y=float(cy))
    center.diameter, center.thickness = 10.0, 2.0
    center.outline_color = Color(r=1.0, g=0.2, b=0.2, a=1.0)

    label = TextAnnotation()
    label.timestamp = stamp
    label.position = Point2(x=float(cx - 40), y=float(cy - 35))
    label.text, label.font_size = 'target  confidence=0.95', 18.0
    label.text_color = Color(r=1.0, g=1.0, b=1.0, a=1.0)
    label.background_color = Color(r=0.0, g=0.0, b=0.0, a=0.7)
    result = ImageAnnotations(points=[box], circles=[center], texts=[label])
    # 新版有整条消息的时间戳；旧版仍可用各条标注的时间戳。
    if hasattr(result, 'timestamp'):
        result.timestamp = stamp
    return result
