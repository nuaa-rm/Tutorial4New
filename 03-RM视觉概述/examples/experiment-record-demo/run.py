"""复用雷达选源，固定输入/判据，只改一个限龄参数并保存证据。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / "radar-fusion-demo"
sys.path.insert(0, str(SOURCE))
from choose import choose


def experiment(radio_limit):
    if radio_limit < 0:
        raise ValueError("无线电限龄不能为负")
    data = json.loads((SOURCE / "sources.json").read_text())
    data["limits_ms"]["radio"] = radio_limit
    result = choose(data)
    # 任务判据先固定，不跟着试验参数一起放宽。
    required_max_age = 100
    age = data["now_ms"] - result["sample_ms"] if result["valid"] else None
    passed = age is not None and 0 <= age <= required_max_age
    files = [Path(__file__), SOURCE / "choose.py", SOURCE / "sources.json"]
    hashes = {str(f.resolve()): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in files}
    return {
        "input_sha256": hashes[str((SOURCE / "sources.json").resolve())],
        "source_sha256": hashes,
        "hypothesis": "放宽无线电限龄能切回无线电，同时满足任务时效",
        "variable": {"radio_limit_ms": radio_limit},
        "fixed": {"now_ms": data["now_ms"],
                  "vision_limit_ms": data["limits_ms"]["vision"],
                  "required_max_age_ms": required_max_age},
        "observations": result, "selected_age_ms": age, "passed": passed,
        "boundary": "人工消息/软件选源，未验证真实通信与实车"}



def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--radio-limit", type=int, default=100)
    p.add_argument("--record", type=Path, required=True)
    a = p.parse_args()
    try:
        record = experiment(a.radio_limit)
    except ValueError as error:
        p.error(str(error))
    a.record.parent.mkdir(parents=True, exist_ok=True)
    a.record.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"file": str(a.record.resolve()), "passed": record["passed"],
                      "source": record["observations"]["source"],
                      "age_ms": record["selected_age_ms"]}))


if __name__ == "__main__":
    main()
