from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def setup(context):
    value = lambda name: LaunchConfiguration(name).perform(context)
    mode = value('mode')
    if mode not in ('intra', 'same', 'separate'):
        raise ValueError('mode 应为 intra、same 或 separate')
    qos = dict(depth=int(value('depth')), reliable=value('reliable') == 'true')
    source = ComposableNode(
        package='image_path_demo', plugin='image_path_demo::Source',
        parameters=[dict(qos, width=int(value('width')), height=int(value('height')),
                         channels=int(value('channels')), rate=float(value('rate')),
                         frames=int(value('frames')))],
        extra_arguments=[{'use_intra_process_comms': mode == 'intra'}])
    sink = ComposableNode(
        package='image_path_demo', plugin='image_path_demo::Sink',
        parameters=[dict(qos, work_ms=int(value('work_ms')))],
        extra_arguments=[{'use_intra_process_comms': mode == 'intra'}])
    def container(name, nodes):
        return ComposableNodeContainer(
            name=name, namespace='', package='rclcpp_components',
            executable='component_container', output='screen',
            composable_node_descriptions=nodes)
    if mode == 'separate':
        return [container('sink_box', [sink]), container('source_box', [source])]
    # 同一个单线程执行器，先加载接收端，再开始发送。
    return [container('image_box', [sink, source])]


def generate_launch_description():
    defaults = dict(mode='intra', width='64', height='48', channels='3',
                    rate='25.0', frames='100', depth='5', reliable='false', work_ms='0')
    return LaunchDescription([
        *[DeclareLaunchArgument(k, default_value=v) for k, v in defaults.items()],
        OpaqueFunction(function=setup)])
