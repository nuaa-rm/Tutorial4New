"""用真实单调时钟检查输入年龄、整轮耗时和求解结果。"""
import time
import numpy as np
from qp import solve

def choose(state, reference, sample_time, budget_ms=10., max_age_ms=100.,
           work_ms=0., **options):
    start = time.perf_counter()
    dt = options.get("dt", .05); amax = options.get("amax", 2.)
    if not np.isfinite([budget_ms, max_age_ms, work_ms, sample_time]).all():
        raise ValueError("时间参数须有限")
    if min(budget_ms, max_age_ms) <= 0 or work_ms < 0 or sample_time > start:
        raise ValueError("预算/年龄为正、负载非负，时间戳不能来自未来")
    result = solve(state, reference, **options)
    # 主动等待只用于离线超时实验，不伪造计时或返回状态。
    if work_ms: time.sleep(work_ms/1000)
    end = time.perf_counter()
    elapsed = (end-start)*1000
    age = (end-sample_time)*1000
    reason = "accepted"
    if result["status_val"] != 1: reason = "solver_status"
    elif result["violation"] is None or result["violation"] > 1e-5: reason = "constraint"
    elif elapsed > budget_ms: reason = "deadline"
    elif age > max_age_ms: reason = "stale_input"
    # 离线模型中的受限减速；不保证已超限状态立刻恢复。
    fallback = float(np.clip(-state[1]/dt, -amax, amax))
    u = float(np.clip(result["U"][0], -amax, amax)) if reason == "accepted" else fallback
    return u, {"reason": reason, "status": result["status"],
               "status_val": int(result["status_val"]), "elapsed_ms": elapsed,
               "age_ms": age, "solver_ms": result["solver_ms"],
               "violation": result["violation"], "control": u,
               "sample_time": sample_time, "start_time": start, "end_time": end}
