"""已知三维点的位姿优化，比较普通平方与块Huber。"""
import argparse
import json
from pathlib import Path
import numpy as np
from model import sample, pose, project
from residual import residual
from optimize import optimize

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--noise", type=float, default=.3)
cli.add_argument("--outlier", type=float, default=0.)
cli.add_argument("--huber", type=float, default=0.)
cli.add_argument("--output", type=Path, default=Path("out/pose"))
args = cli.parse_args()
if not np.isfinite([args.noise, args.outlier, args.huber]).all() or min(args.noise, args.outlier, args.huber) < 0:
    cli.error("噪声/异常偏移/Huber阈值须非负有限")
points = sample(); truth = pose([.05, -.03, .01], [.2, -.1, .1])
pixels = project(points, truth)
observed = pixels+np.random.default_rng(2026).normal(0, args.noise, pixels.shape)
observed[0] += [args.outlier, -args.outlier]
initial = pose([.08, -.01, .03], [.25, -.14, .15])
estimated, history = optimize(points, observed, initial, args.huber)
result = {"synthetic": True, "initial_cost": history[0], "final_cost": history[-1],
    "accepted_cost_nonincreasing": bool(np.all(np.diff(history)<=1e-8)),
    "inlier_rms_pixel": float(np.sqrt(np.mean(np.sum((project(points, estimated)[1:]-pixels[1:])**2, axis=1)))),
    "translation_error_m": float(np.linalg.norm(estimated[:3, 3]-truth[:3, 3])),
    "rotation_determinant": float(np.linalg.det(estimated[:3, :3]))}
args.output.mkdir(parents=True, exist_ok=True)
np.savez(args.output/"result.npz", observed=observed[None], initial=project(points, initial)[None],
    final=project(points, estimated)[None], truth=pixels[None], history=history)
(args.output/"metrics.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result))
