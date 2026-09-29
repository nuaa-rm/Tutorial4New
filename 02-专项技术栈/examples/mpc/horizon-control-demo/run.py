"""逐轮重新测量和规划；全部离线，不连接电机或开火接口。"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from controller import choose
from model import step

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--horizon", type=int, default=15)
cli.add_argument("--steps", type=int, default=80)
cli.add_argument("--reference", type=float, default=.4)
cli.add_argument("--q", type=float, default=20.)
cli.add_argument("--r", type=float, default=.1)
cli.add_argument("--amax", type=float, default=2.)
cli.add_argument("--vmax", type=float, default=.8)
cli.add_argument("--gain", type=float, default=1.)
cli.add_argument("--disturb", type=float, default=0.)
cli.add_argument("--command-alpha", type=float, default=1.)
cli.add_argument("--budget-ms", type=float, default=10.)
cli.add_argument("--work-ms", type=float, default=0.)
cli.add_argument("--age-ms", type=float, default=0.)
cli.add_argument("--max-iter", type=int, default=4000)
cli.add_argument("--terminal", action="store_true")
cli.add_argument("--output", type=Path, default=Path("out/default"))
args = cli.parse_args()
numbers = [v for v in vars(args).values() if isinstance(v, (int, float))]
if not np.isfinite(numbers).all() or args.steps < 1 or args.horizon < 1:
    cli.error("参数须有限，步数与时域为正")
if min(args.q, args.r, args.amax, args.vmax, args.gain, args.budget_ms) <= 0:
    cli.error("权重、上限、增益与预算为正")
if args.work_ms < 0 or args.age_ms < 0 or not 0 < args.command_alpha <= 1:
    cli.error("负载/年龄非负，alpha在(0,1]")
dt = .05; x = np.zeros(2); states = [x.copy()]; applied = []; logs = []; previous = 0.
for k in range(args.steps):
    sample = time.perf_counter()-args.age_ms/1000
    u, log = choose(x, args.reference, sample, budget_ms=args.budget_ms,
                   work_ms=args.work_ms, horizon=args.horizon, q=args.q, r=args.r,
                   amax=args.amax, vmax=args.vmax, terminal=args.terminal,
                   max_iter=args.max_iter)
    # 模拟额外低通；回退命令不再被这层拖延。
    actual = args.command_alpha*u+(1-args.command_alpha)*previous if log["reason"] == "accepted" else u
    x = step(x, actual, dt, args.gain); previous = actual
    if k == 19: x[0] += args.disturb
    log.update(k=k, plant_time=k*dt, applied=actual)
    states.append(x.copy()); applied.append(actual); logs.append(log)
states = np.array(states); applied = np.array(applied)
args.output.mkdir(parents=True, exist_ok=True)
np.savez(args.output/"result.npz", states=states, controls=applied,
         dt=dt, reference=args.reference, amax=args.amax, vmax=args.vmax)
(args.output/"log.json").write_text(json.dumps(logs, ensure_ascii=False, indent=2)+"\n")
result = {"final_state": states[-1].tolist(), "max_abs_control": float(max(abs(applied))),
          "max_abs_speed": float(max(abs(states[:, 1]))),
          "angle_rmse": float(np.sqrt(np.mean((states[1:, 0]-args.reference)**2))),
          "fallback_count": sum(l["reason"] != "accepted" for l in logs),
          "reasons": sorted(set(l["reason"] for l in logs)),
          "statuses": sorted(set(l["status"] for l in logs)),
          "max_elapsed_ms": max(l["elapsed_ms"] for l in logs)}
print(json.dumps(result, ensure_ascii=False))
