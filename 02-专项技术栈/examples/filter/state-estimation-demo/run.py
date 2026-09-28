"""同一序列比较 KF/EKF 与 UKF，记录真值误差和创新量。"""
import argparse
import json
from pathlib import Path
import numpy as np
from data import generate
from linear import predict, update
from ukf import step

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--mode", choices=("linear", "range"), default="linear")
cli.add_argument("--steps", type=int, default=150)
cli.add_argument("--dt", type=float, default=.1)
cli.add_argument("--q", type=float, default=.5)
cli.add_argument("--r", type=float, default=.04)
cli.add_argument("--bias", type=float, default=0.)
cli.add_argument("--seed", type=int, default=42)
cli.add_argument("--drop-every", type=int, default=0)
cli.add_argument("--alpha", type=float, default=1.)
cli.add_argument("--output", type=Path, default=Path("out/linear"))
args = cli.parse_args()
if (args.steps < 3 or args.drop_every < 0 or args.dt <= 0 or args.r <= 0 or args.q < 0 or
        not np.isfinite([args.dt, args.q, args.r, args.bias, args.alpha]).all()):
    cli.error("长度至少3，dt/R为正、Q方差非负，参数为有限数")
truth, position, distance, F, G = generate(args.steps, args.dt, args.seed, args.bias)
Q = args.q*np.outer(G, G)
observe = (lambda x: float(x[0])) if args.mode == "linear" else (lambda x: float(np.hypot(x[0], 2.)))
measurements = position if args.mode == "linear" else distance
x = np.array([1., .3]); P = np.diag([.25, 1.])
u = x.copy(); U = P.copy()
estimates, unscented, innovations, nis, minimum = [], [], [], [], []
dropped = 0
for i, measurement in enumerate(measurements):
    missing = args.drop_every > 0 and (i+1) % args.drop_every == 0
    dropped += int(missing)
    x, P = predict(x, P, F, Q)
    if missing:
        residual = score = np.nan
    else:
        H = np.array([[1., 0.]]) if args.mode == "linear" else np.array([[x[0]/observe(x), 0.]])
        x, P, error, S = update(x, P, measurement, H, args.r, np.array([observe(x)]))
        residual = float(error[0]); score = residual**2/float(S[0, 0])
    u, U, _, _ = step(u, U, F, Q, None if missing else measurement, args.r, observe, args.alpha)
    estimates.append(x.copy()); unscented.append(u.copy())
    innovations.append(residual); nis.append(score)
    minimum.append(min(np.linalg.eigvalsh(P).min(), np.linalg.eigvalsh(U).min()))
estimates, unscented = np.array(estimates), np.array(unscented)
args.output.mkdir(parents=True, exist_ok=True)
np.savez(args.output/"series.npz", truth=truth, observed=measurements, estimate=estimates,
         ukf=unscented, innovations=innovations, nis=nis, dt=args.dt, Q=Q, R=args.r)
result = {"synthetic": True, "mode": args.mode, "steps": args.steps, "dropped": dropped,
    "dt_s": args.dt, "q_acceleration_variance": args.q, "r_measurement_variance": args.r,
    "assumed_height_m": 2., "rmse_position_m": {
        "kf" if args.mode == "linear" else "ekf": float(np.sqrt(np.mean((estimates[:, 0]-truth[:, 0])**2))),
        "ukf": float(np.sqrt(np.mean((unscented[:, 0]-truth[:, 0])**2)))},
    "max_state_difference": float(np.max(abs(estimates-unscented))),
    "mean_nis": float(np.nanmean(nis)), "minimum_covariance_eigenvalue": float(min(minimum)),
    "last_state": estimates[-1].tolist(), "Q": Q.tolist()}
(args.output/"metrics.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result))
