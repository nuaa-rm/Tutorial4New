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
        DeclareLaunchArgument('robot', default_value='robot1',
                             description='节点所在的相对命名空间'),
        DeclareLaunchArgument('text', default_value='ready from launch',
                             description='心跳消息的字符串内容'),
        DeclareLaunchArgument('params_file',
                             default_value=str(share / 'config' / 'heartbeat.yaml'),
                             description='ROS 参数 YAML 文件路径'),
        Node(
            package='training_tools', executable='heartbeat',
            name='heartbeat', namespace=LaunchConfiguration('robot'),
            output='screen',
            parameters=[LaunchConfiguration('params_file'),
                        {'text': ParameterValue(
                            LaunchConfiguration('text'), value_type=str)}],
            remappings=[('status', 'health')],
            additional_env={'RCUTILS_COLORIZED_OUTPUT': '1'},
        ),
    ])
