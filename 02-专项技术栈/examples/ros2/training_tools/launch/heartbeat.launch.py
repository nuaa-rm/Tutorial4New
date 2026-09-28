from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory('training_tools'))
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='robot1'),
        DeclareLaunchArgument('text', default_value='ready from launch'),
        Node(
            package='training_tools', executable='heartbeat',
            name='heartbeat', namespace=LaunchConfiguration('robot'),
            output='screen',
            parameters=[str(share / 'config' / 'heartbeat.yaml'),
                        {'text': ParameterValue(
                            LaunchConfiguration('text'), value_type=str)}],
            remappings=[('status', 'health')],
            additional_env={'RCUTILS_COLORIZED_OUTPUT': '1'},
        ),
    ])
