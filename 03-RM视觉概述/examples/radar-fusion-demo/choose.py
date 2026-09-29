"""用人工消息观察选源与失效；不接收射频，也不发送裁判帧。"""
import argparse
import json
import math
from pathlib import Path


def assess(message, contract, limit):
    for key in ("target", "frame", "unit", "clock"):
        if message.get(key) != contract[key]:
            return "mismatch: " + key
    if message.get("valid") is not True or message.get("quality_ok") is not True:
        return "invalid or poor quality"
    xy = message.get("xy")
    if not isinstance(xy, list) or len(xy) != 2:
        return "bad coordinates"
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in xy):
        return "bad coordinates"
    sample = message.get("sample_ms")
    if type(sample) is not int:
        return "bad timestamp"
    age = contract["now_ms"] - sample
    if age < 0 or age > limit:
        return "future or expired"
    return "ok"


def choose(data):
    reasons = {name: assess(data[name], data, data["limits_ms"][name])
               for name in ("radio", "vision")}
    for name in ("radio", "vision"):
        if reasons[name] == "ok":
            return {"valid": True, "source": name, "xy_m": data[name]["xy"],
                    "sample_ms": data[name]["sample_ms"], "checks": reasons}
    return {"valid": False, "source": None, "xy_m": None, "checks": reasons}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--radio-age", type=int)
    p.add_argument("--vision-age", type=int)
    p.add_argument("--radio-invalid", action="store_true")
    p.add_argument("--radio-frame")
    a = p.parse_args()
    data = json.loads(Path(__file__).with_name("sources.json").read_text())
    for name in ("radio", "vision"):
        age = getattr(a, name + "_age")
        if age is not None:
            data[name]["sample_ms"] = data["now_ms"] - age
    if a.radio_invalid:
        data["radio"]["valid"] = False
    if a.radio_frame is not None:
        data["radio"]["frame"] = a.radio_frame
    print(json.dumps(choose(data), allow_nan=False))


if __name__ == "__main__":
    main()
