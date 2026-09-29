"""教学接收端：解释接口卡，只打印决定，不连接云台。"""
import argparse
import json
import math
from pathlib import Path


def interpret(card, now_ms):
    contract, message = card["contract"], card["message"]
    # 名称一样还不够，双方必须约定一样的含义。
    for key in ("version", "unit", "frame", "clock"):
        if message[key] != contract[key]:
            return {"decision": "hold", "reason": key + " mismatch"}
    numbers = [now_ms, message["sample_ms"], message["delta_yaw"],
               contract["max_age_ms"]]
    if any(type(x) not in (int, float) or not math.isfinite(x)
           for x in numbers) or contract["max_age_ms"] < 0:
        return {"decision": "hold", "reason": "invalid number"}
    age = now_ms - message["sample_ms"]
    if not 0 <= age <= contract["max_age_ms"]:
        return {"decision": "hold", "reason": "time invalid", "age_ms": age}
    if message["valid"] is not True:
        return {"decision": "hold", "reason": "observation invalid"}
    # 本示例只实现 rad / 云台水平增量 / 同一教学时钟。
    if (contract["unit"], contract["frame"], contract["clock"]) != (
            "rad", "gimbal_delta_left_positive", "demo_clock"):
        return {"decision": "hold", "reason": "unsupported contract"}
    return {"decision": "accept", "age_ms": age,
            "delta_deg": math.degrees(message["delta_yaw"])}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--card", type=Path, default=Path(__file__).with_name("card.json"))
    cli.add_argument("--now-ms", type=float, default=100)
    cli.add_argument("--unit")
    cli.add_argument("--frame")
    cli.add_argument("--age-ms", type=float)
    cli.add_argument("--delta", type=float)
    cli.add_argument("--invalid", action="store_true")
    args = cli.parse_args()
    card = json.loads(args.card.read_text(encoding="utf-8"))
    message = card["message"]
    for key in ("unit", "frame"):
        value = getattr(args, key)
        if value is not None:
            message[key] = value
    if args.age_ms is not None:
        message["sample_ms"] = args.now_ms - args.age_ms
    if args.delta is not None:
        message["delta_yaw"] = args.delta
    if args.invalid:
        message["valid"] = False
    print(json.dumps(interpret(card, args.now_ms), ensure_ascii=False))
