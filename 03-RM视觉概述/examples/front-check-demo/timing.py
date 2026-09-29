"""同一时钟、逐帧配对的教学时刻；执行列才是端到端终点。"""
import argparse
import csv
import json
import math
from pathlib import Path


def measure(path):
    rows = list(csv.DictReader(path.open()))
    if len(rows) < 2 or any(row["clock"] != "demo_clock" for row in rows):
        raise ValueError("至少两帧，且本例只接受demo_clock")
    if len({row["frame"] for row in rows}) != len(rows):
        raise ValueError("帧身份重复，不能配对")
    times = [[float(row[key]) for key in ("sample_ms", "result_ms", "execute_ms")]
             for row in rows]
    if any(not all(math.isfinite(v) for v in t) or not t[0] <= t[1] <= t[2] for t in times):
        raise ValueError("时间须有限且采样<=结果<=执行")
    intervals = [b[0] - a[0] for a, b in zip(times, times[1:])]
    if min(intervals) <= 0:
        raise ValueError("采样时刻须递增")
    return {"observed_sample_fps": 1000 * len(intervals) / sum(intervals),
            "result_delay_ms": [t[1] - t[0] for t in times],
            "end_to_end_ms": [t[2] - t[0] for t in times]}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("csv", type=Path)
    a = p.parse_args()
    try:
        print(json.dumps(measure(a.csv), allow_nan=False))
    except (ValueError, KeyError) as error:
        p.error(str(error))


if __name__ == "__main__":
    main()
