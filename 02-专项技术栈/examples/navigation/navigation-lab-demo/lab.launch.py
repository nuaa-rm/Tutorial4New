"""启动最小的地图、规划、控制闭环，不加载整套机器人bringup。"""
import sys
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    root = Path(__file__).resolve().parent
    params = str(root/"params.yaml")
    servers = [("nav2_map_server", "map_server"),
               ("nav2_planner", "planner_server"),
               ("nav2_controller", "controller_server")]
    nodes = []
    for package, name in servers:
        settings = [params]
        if name == "map_server":
            settings += [{"yaml_filename": LaunchConfiguration("map")}]
        nodes.append(Node(package=package, executable=name, name=name,
                          parameters=settings, output="screen"))
    nodes += [Node(package="nav2_lifecycle_manager", executable="lifecycle_manager",
                   name="lifecycle_manager", parameters=[{"autostart": True,
                   "node_names": [name for _, name in servers]}]),
              ExecuteProcess(cmd=[sys.executable, str(root/"sim.py")])]
    return LaunchDescription([DeclareLaunchArgument("map",
        default_value=str(root/"out/map/map.yaml"))]+nodes)
