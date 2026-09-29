"""实际调用Nav2规划/控制action，保存路径、里程计和速度。"""
import argparse
import json
import math
import time
from pathlib import Path
import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from lifecycle_msgs.srv import GetState
from lifecycle_msgs.msg import State
from nav2_msgs.action import ComputePathToPose, FollowPath
from rclpy.action import ActionClient

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--blocked-goal", action="store_true")
cli.add_argument("--output", type=Path, default=Path("out/nav2"))
args = cli.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
rclpy.init(); node = rclpy.create_node("navigation_client")
trajectory, commands = [], []
node.create_subscription(Odometry, "odom", lambda m: trajectory.append(
    [m.pose.pose.position.x, m.pose.pose.position.y]), 10)
node.create_subscription(Twist, "cmd_vel", lambda m: commands.append(
    [m.linear.x, m.angular.z]), 10)


def wait(future, seconds):
    rclpy.spin_until_future_complete(node, future, timeout_sec=seconds)
    if not future.done() or future.exception():
        raise RuntimeError("action通信超时或异常；请检查服务和日志")
    return future.result()


def call(action_type, name, goal):
    client = ActionClient(node, action_type, name)
    if not client.wait_for_server(timeout_sec=20):
        raise RuntimeError(name+"服务未就绪")
    handle = wait(client.send_goal_async(goal), 10)
    if not handle.accepted:
        raise RuntimeError(name+"拒绝了请求")
    future = handle.get_result_async()
    try:
        return wait(future, 40)
    except RuntimeError:
        wait(handle.cancel_goal_async(), 5)
        raise
    finally:
        client.destroy()


try:
    # action已经能连接，不代表服务器的地图/TF初始化已经完成。
    for server in ("map_server", "planner_server", "controller_server"):
        state = node.create_client(GetState, server+"/get_state")
        if not state.wait_for_service(timeout_sec=20):
            raise RuntimeError(server+"生命周期服务未就绪")
        deadline = time.monotonic()+20
        while time.monotonic() < deadline:
            response = wait(state.call_async(GetState.Request()), 2)
            if response.current_state.id == State.PRIMARY_STATE_ACTIVE:
                break
            rclpy.spin_once(node, timeout_sec=.1)
        else:
            raise RuntimeError(server+"未激活，请看launch终端")
        node.destroy_client(state)
    goal = ComputePathToPose.Goal(); goal.planner_id = "GridBased"
    goal.goal = PoseStamped(); goal.goal.header.frame_id = "map"
    goal.goal.header.stamp = node.get_clock().now().to_msg()
    goal.goal.pose.position.x = 3. if args.blocked_goal else 5.05
    goal.goal.pose.position.y = 2. if args.blocked_goal else 3.05
    goal.goal.pose.orientation.w = 1.
    planned = call(ComputePathToPose, "compute_path_to_pose", goal)
    path = planned.result.path
    result = {"plan_status": planned.status, "plan_error": planned.result.error_code,
              "path_poses": len(path.poses)}
    if planned.status == GoalStatus.STATUS_SUCCEEDED:
        follow = FollowPath.Goal(); follow.path = path
        follow.controller_id = "FollowPath"; follow.goal_checker_id = "goal"
        follow.progress_checker_id = "progress"
        followed = call(FollowPath, "follow_path", follow)
        result.update(follow_status=followed.status, follow_error=followed.result.error_code)
    points = [[p.pose.position.x, p.pose.position.y] for p in path.poses]
    result.update(odom_samples=len(trajectory), command_samples=len(commands))
    if trajectory:
        result["final_xy"] = trajectory[-1]
        result["goal_error_m"] = math.dist(trajectory[-1],
            [goal.goal.pose.position.x, goal.goal.pose.position.y])
    np.savez(args.output/"nav2.npz", path=np.array(points).reshape(-1, 2),
             trajectory=np.array(trajectory).reshape(-1, 2),
             commands=np.array(commands).reshape(-1, 2))
    (args.output/"result.json").write_text(json.dumps(result))
    print(json.dumps(result))
finally:
    node.destroy_node(); rclpy.shutdown()
