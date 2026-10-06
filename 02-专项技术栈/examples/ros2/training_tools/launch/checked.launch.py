from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription, LogInfo, OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def checked_start(context):
    config = Path(LaunchConfiguration('params_file').perform(context))
    config = config.expanduser().resolve()
    if not config.is_file():
        raise RuntimeError(f'参数文件不存在：{config}')
    share = Path(get_package_share_directory('training_tools'))
    return [
        LogInfo(msg=f'Using parameters: {config}'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(share / 'launch' / 'heartbeat.launch.py')),
            launch_arguments={
                'robot': LaunchConfiguration('robot'),
                'params_file': str(config), 'text': 'checked ready',
            }.items(),
        ),
    ]


def generate_launch_description():
    share = Path(get_package_share_directory('training_tools'))
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='robot1'),
        DeclareLaunchArgument('params_file',
                             default_value=str(share / 'config' / 'heartbeat.yaml')),
        OpaqueFunction(function=checked_start),
    ])
