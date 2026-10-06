"""Foxglove 原生三维场景：一个实体内组合方块和文字。"""
from builtin_interfaces.msg import Duration
from geometry_msgs.msg import Pose, Point, Vector3
from foxglove_msgs.msg import (SceneUpdate, SceneEntity, CubePrimitive,
                               TextPrimitive, Color)


def make_scene(pose):
    entity = SceneEntity()
    entity.timestamp, entity.frame_id = pose.header.stamp, 'map'
    entity.id = 'target'
    entity.lifetime = Duration(sec=0, nanosec=500000000)
    cube = CubePrimitive()
    cube.pose = pose.pose
    cube.size = Vector3(x=0.25, y=0.25, z=0.25)
    cube.color = Color(r=0.1, g=0.9, b=0.7, a=1.0)
    text = TextPrimitive()
    p = pose.pose.position
    text.pose = Pose(position=Point(x=p.x, y=p.y, z=p.z + 0.6))
    text.pose.orientation.w = 1.0
    text.billboard, text.scale_invariant = True, True
    text.font_size, text.text = 18.0, 'Foxglove SceneEntity'
    text.color = Color(r=1.0, g=1.0, b=1.0, a=1.0)
    entity.cubes, entity.texts = [cube], [text]
    return SceneUpdate(entities=[entity])
