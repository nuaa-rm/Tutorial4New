from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    heartbeat = Node(
        package='training_tools',
        executable='heartbeat',
        name='heartbeat',
        output='screen',
    )
    return LaunchDescription([heartbeat])
