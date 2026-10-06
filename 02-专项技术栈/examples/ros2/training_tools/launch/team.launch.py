from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,
    LogInfo, OpaqueFunction, RegisterEventHandler, SetEnvironmentVariable,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def report_config(context):
    robot = LaunchConfiguration('robot').perform(context)
    return [LogInfo(msg=f'Observing /{robot}/health')]


def generate_launch_description():
    share = Path(get_package_share_directory('training_tools'))
    observer = ExecuteProcess(
        cmd=['ros2', 'topic', 'echo', '/red/health',
             'std_msgs/msg/String', '--once'],
        output='screen', condition=IfCondition(LaunchConfiguration('watch')),
    )
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='red',
                             description='传给心跳启动文件的命名空间'),
        DeclareLaunchArgument('watch', default_value='true',
                             description='是否启动一次性话题观测进程'),
        SetEnvironmentVariable('RCUTILS_COLORIZED_OUTPUT', '1'),
        OpaqueFunction(function=report_config),
        LogInfo(msg='Observer disabled.',
                condition=UnlessCondition(LaunchConfiguration('watch'))),
        RegisterEventHandler(OnProcessExit(
            target_action=observer,
            on_exit=[LogInfo(msg='Observer exited; heartbeat keeps running.')],
        )),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(share / 'launch' / 'heartbeat.launch.py')),
            launch_arguments={
                'robot': LaunchConfiguration('robot'), 'text': 'team ready',
            }.items(),
        ),
        observer,
    ])
