"""只写标准输出的部署练习，不访问相机、串口或控制设备。"""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--count", type=int, default=0, help="输出次数，0 为持续运行")
parser.add_argument("--interval", type=float, default=1.0, help="输出间隔，单位秒")
parser.add_argument("--fail-after", type=int, default=0, help="第几次输出后模拟失败")
args = parser.parse_args()
if args.count < 0 or args.interval <= 0 or args.fail_after < 0:
    parser.error("次数不能为负，间隔必须大于 0")

version = os.environ.get("RM_DEMO_VERSION", "manual-v1")
print(f"start pid={os.getpid()} version={version} cwd={Path.cwd()}", flush=True)
try:
    sequence = 0
    while args.count == 0 or sequence < args.count:
        sequence += 1
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"{now} heartbeat={sequence}", flush=True)
        if args.fail_after and sequence >= args.fail_after:
            print("模拟失败：以状态码 1 退出", flush=True)
            raise SystemExit(1)
        if args.count == 0 or sequence < args.count:
            time.sleep(args.interval)
except KeyboardInterrupt:
    print("收到 Ctrl+C，正常结束", flush=True)
