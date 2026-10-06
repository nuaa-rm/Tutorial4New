from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace


def generate_launch_description():
    share = Path(get_package_share_directory('training_tools'))
    groups = []
    for robot in ('red', 'blue'):
        groups.append(GroupAction(actions=[
            PushRosNamespace(robot),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(share / 'launch' / 'heartbeat.launch.py')),
                launch_arguments={
                    'robot': 'sensors', 'text': f'{robot} ready',
                }.items(),
            ),
        ]))
    return LaunchDescription(groups)
