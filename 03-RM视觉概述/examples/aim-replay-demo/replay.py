"""回放教学中间量与预测时间线；不发送云台或开火指令。"""
import argparse
import csv
import json
import math
from pathlib import Path


def timeline(delay_ms, flight_ms, state_at):
    if not all(math.isfinite(t) and t >= 0 for t in (delay_ms, flight_ms)):
        raise ValueError("时长必须为非负有限数")
    sample_ms, x_sample, velocity = 10, 4.0, 2.0
    control_ms = sample_ms + delay_ms
    hit_ms = control_ms + flight_ms
    state_ms = sample_ms if state_at == "sample" else control_ms
    # 状态外推以后，位置和状态时刻必须一起更新。
    x_state = x_sample + velocity * (state_ms - sample_ms) / 1000
    horizon_ms = hit_ms - state_ms
    x_hit = x_state + velocity * horizon_ms / 1000
    wrong_x = x_state + velocity * (delay_ms + flight_ms) / 1000
    return {"sample_ms": sample_ms, "control_ms": control_ms,
            "hit_ms": hit_ms, "state_ms": state_ms,
            "horizon_ms": horizon_ms, "x_hit_m": x_hit,
            "wrong_repeat_delay_x_m": wrong_x}


def first_changes(file, pixel_threshold):
    if not math.isfinite(pixel_threshold) or pixel_threshold < 0:
        raise ValueError("像素变化阈值必须为非负有限数")
    thresholds = {"corner_u_px": pixel_threshold, "camera_x_m": 0.5,
                  "state_x_m": 0.5, "yaw_command_deg": 10}
    first = {name: None for name in thresholds}
    with file.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for previous, current in zip(rows, rows[1:]):
        for name, threshold in thresholds.items():
            difference = float(current[name]) - float(previous[name])
            if first[name] is None and abs(difference) > threshold:
                first[name] = {"frame": int(current["frame"]),
                               "difference": difference}
    return first


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--delay-ms", type=float, default=35)
    cli.add_argument("--flight-ms", type=float, default=65)
    cli.add_argument("--state-at", choices=["sample", "control"], default="sample")
    cli.add_argument("--pixel-threshold", type=float, default=50)
    cli.add_argument("--replay", type=Path, default=Path(__file__).with_name("frames.csv"))
    args = cli.parse_args()
    try:
        result = {"timeline": timeline(args.delay_ms, args.flight_ms, args.state_at),
                  "first_changes": first_changes(args.replay, args.pixel_threshold)}
    except ValueError as error:
        cli.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
