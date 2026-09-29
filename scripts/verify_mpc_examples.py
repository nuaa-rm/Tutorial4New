#!/usr/bin/env python3
"""实际运行MPC项目，并独立核对离散化、QP、约束与回退。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.optimize import minimize
import osqp

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--project", type=Path, required=True)
cli.add_argument("--work", type=Path, required=True)
cli.add_argument("--evidence", type=Path, required=True)
args = cli.parse_args(); args.work.mkdir(parents=True, exist_ok=True)
records = []
def record(name, data):
    records.append({"name": name, "status": "PASS", "details": data})
def run(name, file, *options, fail=False):
    cmd = [sys.executable, str(args.project/file), *map(str, options)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    assert (result.returncode != 0) if fail else result.returncode == 0, result.stderr
    data = {"exit": result.returncode, "stderr": result.stderr[-500:]} if fail else json.loads(result.stdout)
    record(name, {"command": cmd, "result": data}); return data

response = run("一阶响应默认", "response.py", "--output", args.work/"response")
assert response["steps_90"] == 11 and response["steps_98"] == 18
fast = run("一阶响应a0.5", "response.py", "--a", .5, "--output", args.work/"fast")
assert fast["steps_90"] == 4 and fast["steps_98"] == 6
far = run("距离10m", "response.py", "--distance", 10, "--output", args.work/"far")
assert abs(far["epsilon_rad"]-np.arctan(.005)) < 1e-14
scalar = run("手算优化和滚动扰动", "scalar.py")
assert abs(scalar["cost"]-.68) < 1e-12 and scalar["weight9_u"] == .1
assert abs(scalar["feedback"]["states"][-1]-.925) < 1e-12
assert abs(scalar["old_sequence"]["states"][-1]-.85) < 1e-12

cases = [("default", []), ("short", ["--horizon", 1]),
         ("long", ["--horizon", 30]), ("weight", ["--r", 1.]),
         ("speed", ["--vmax", .3]), ("jump", ["--reference", .7]),
         ("disturb", ["--disturb", -.1]), ("mismatch", ["--gain", .6]),
         ("filtered", ["--command-alpha", .1]),
         ("infeasible", ["--horizon", 2, "--terminal", "--steps", 3]),
         ("maxiter", ["--max-iter", 1, "--steps", 3]),
         ("deadline", ["--work-ms", 20, "--steps", 3]),
         ("stale", ["--age-ms", 200, "--steps", 3])]
outputs = {}
for tag, options in cases:
    output = args.work/tag
    data = run("有限时域闭环 "+tag, "run.py", "--output", output, *options)
    logs = json.loads((output/"log.json").read_text())
    arrays = np.load(output/"result.npz")
    assert np.isfinite(arrays["states"]).all()
    assert data["max_abs_control"] <= 2+1e-10
    for log in logs:
        if log["reason"] == "accepted":
            assert log["status_val"] == 1 and log["violation"] <= 1e-5
            assert log["elapsed_ms"] <= 10 and log["age_ms"] <= 100
    if tag == "infeasible": assert data["statuses"] == ["primal infeasible"]
    if tag == "maxiter": assert data["statuses"] == ["maximum iterations reached"]
    if tag == "deadline":
        assert data["reasons"] == ["deadline"] and min(l["elapsed_ms"] for l in logs) >= 20
    if tag == "stale": assert data["reasons"] == ["stale_input"]
    if tag in ("infeasible", "maxiter", "deadline", "stale"):
        assert data["fallback_count"] == 3
    outputs[tag] = data
assert abs(outputs["default"]["final_state"][0]-.4) < 1e-3
assert outputs["short"]["angle_rmse"] > outputs["default"]["angle_rmse"]

sys.path.insert(0, str(args.project))
from model import model, step
from prediction import prediction
from qp import solve
from controller import choose
from response import analyze
import time
for name, action in (
    ("未来单调时间戳拒绝", lambda: choose(np.zeros(2), .4, time.perf_counter()+1)),
    ("非有限状态拒绝", lambda: solve(np.array([float("nan"), 0]), .4)),
    ("零采样周期拒绝", lambda: model(0)),
    ("负实际增益拒绝", lambda: step(np.zeros(2), 1, .05, -1))):
    try: action()
    except ValueError as error: record(name, str(error))
    else: raise AssertionError(name+"未拒绝")
A, B = model(.05)
continuous = np.array([[0., 1., 0.], [0., 0., 1.], [0., 0., 0.]])
discrete = expm(continuous*.05)
assert np.allclose(A, discrete[:2, :2]) and np.allclose(B, discrete[:2, 2:])
record("独立矩阵指数零阶保持", {"A": A.tolist(), "B": B.tolist()})
for N in (1, 2, 15):
    Phi, Theta = prediction(A, B, N)
    x = np.array([.1, -.2]); U = np.linspace(-.5, .7, N); rolled = []; current = x.copy()
    for u in U:
        current = step(current, u, .05); rolled.extend(current)
    err = float(np.max(abs(Phi @ x+Theta @ U-rolled)))
    assert err < 1e-13
    record("预测矩阵与独立逐步递推 N"+str(N), {"max_error": err})
data = solve(np.array([.1, -.2]), .4, horizon=5)
Phi = data["Phi"]; Theta = data["Theta"]; U = data["U"]
def cost(U):
    e = Phi @ np.array([.1, -.2])+Theta @ U-data["desired"]
    return float(np.sum(data["weights"]*e*e)+.1*(U @ U))
constant = cost(np.zeros(5))
expanded = .5*U @ data["H"] @ U+data["g"] @ U+constant
assert abs(cost(U)-expanded) < 1e-12
eps = 1e-6
numeric = np.array([(cost(U+eps*np.eye(5)[i])-cost(U-eps*np.eye(5)[i]))/(2*eps) for i in range(5)])
assert np.allclose(numeric, data["H"] @ U+data["g"], atol=1e-8)
assert np.min(np.linalg.eigvalsh(data["H"])) > 0
record("完整代价/梯度/正定性", {"full_cost": cost(U), "expanded_cost": float(expanded),
       "hessian_min_eigenvalue": float(np.min(np.linalg.eigvalsh(data["H"])))})
speed_offset = (Phi @ np.array([.1, -.2]))[1::2]
independent = minimize(cost, np.zeros(5), method="SLSQP", bounds=[(-2, 2)]*5,
    constraints=[{"type": "ineq", "fun": lambda u: .8-speed_offset-Theta[1::2] @ u},
                 {"type": "ineq", "fun": lambda u: .8+speed_offset+Theta[1::2] @ u}],
    options={"ftol": 1e-12, "maxiter": 200})
assert independent.success and np.max(abs(independent.x-U)) < 1e-5
record("OSQP与独立SLSQP", {"max_control_difference": float(np.max(abs(independent.x-U)))})
for speed in (.4, 1.2):
    u, log = choose(np.array([0., speed]), .4, __import__("time").perf_counter()-.2)
    assert log["reason"] != "accepted" and abs(u) <= 2
    new = step([0., speed], u, .05)
    assert abs(new[1]) < speed
    record("非零速度回退 "+str(speed), {"log": log, "next_state": new.tolist()})
for a in (.8, .5):
    result, _ = analyze(a)
    # 直接递推两种正弦，舍弃2000步初始过渡，再以sin/cos最小二乘辨识。
    for f, gain, phase in zip((1., 10.), result["steady_gain"], result["steady_phase"]):
        t = np.arange(4000)*.01; input_signal = np.sin(2*np.pi*f*t); y = np.zeros(4000)
        for k in range(3999): y[k+1] = a*y[k]+(1-a)*input_signal[k]
        basis = np.column_stack([np.sin(2*np.pi*f*t[2000:]), np.cos(2*np.pi*f*t[2000:])])
        coefficients = np.linalg.lstsq(basis, y[2000:], rcond=None)[0]
        measured = np.hypot(*coefficients); measured_phase = np.arctan2(coefficients[1], coefficients[0])
        assert abs(measured-gain) < 1e-12 and abs(measured_phase-phase) < 1e-12
        record("独立稳态递推 a%s f%s" % (a, f), {"gain": float(measured), "phase": float(measured_phase)})
for name, options in (("负权重", ["--r", -1]), ("零时域", ["--horizon", 0]),
                      ("NaN参考", ["--reference", "nan"]), ("无效滤波", ["--command-alpha", 0]),
                      ("负输入年龄", ["--age-ms", -1])):
    run(name+"明确拒绝", "run.py", *options, fail=True)
run("不稳定一阶参数拒绝", "response.py", "--a", 1.1, fail=True)
evidence = {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
            "osqp": osqp.__version__, "offline": True,
            "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(args.project.glob("*.py"))}, "records": records}
args.evidence.parent.mkdir(parents=True, exist_ok=True)
args.evidence.write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+"\n")
print(json.dumps({"records": len(records), "closed_loop": outputs}, ensure_ascii=False, indent=2))
