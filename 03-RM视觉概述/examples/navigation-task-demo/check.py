"""核对导航任务前提和实际结果；不发送速度或修改急停。"""
import argparse
import json
import math
from pathlib import Path


def width_check(corridor, robot, margin):
    values = (corridor, robot, margin)
    if not all(math.isfinite(x) and x >= 0 for x in values):
        raise ValueError("尺寸必须为非负有限数")
    required = robot + 2 * margin
    return {"required_m": required, "straight_width_ok": corridor >= required}


def map_point(point, yaw_deg, translation):
    # 约定：p_map = R(yaw) p_field + translation，长度统一用米。
    angle = math.radians(yaw_deg)
    c, s = math.cos(angle), math.sin(angle)
    x, y = point
    return [c*x-s*y+translation[0], s*x+c*y+translation[1]]


def explain_result(result):
    if result["plan_status"] != 4:
        return {"next": "inspect goal, map and TF",
                "plan_error": result["plan_error"], "follow_requested": False}
    if result.get("follow_status") != 4:
        return {"next": "inspect controller and execution",
                "follow_error": result.get("follow_error")}
    return {"next": "review trajectory and conditions",
            "goal_error_m": result.get("goal_error_m"),
            "boundary": "software result, not physical arrival"}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--corridor", type=float, default=0.8)
    cli.add_argument("--robot", type=float, default=0.6)
    cli.add_argument("--margin", type=float, default=0.15)
    cli.add_argument("--result", type=Path)
    args = cli.parse_args()
    try:
        data = {"width": width_check(args.corridor, args.robot, args.margin),
                "patrol_goal_map_m": map_point([2, 0], 90, [1, 1])}
    except ValueError as error:
        cli.error(str(error))
    if args.result:
        data["run"] = explain_result(json.loads(args.result.read_text()))
    print(json.dumps(data, ensure_ascii=False, indent=2))
