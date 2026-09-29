"""DLT、PnP和P3P使用同一批点，候选按额外点核对。"""
import argparse
import json
import cv2
import numpy as np
from model import K, pose, transform, project
from dlt import solve

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--scale", type=float, default=1.)
cli.add_argument("--noise", type=float, default=0.)
cli.add_argument("--swap", action="store_true")
args = cli.parse_args()
if not np.isfinite([args.scale, args.noise]).all() or args.scale <= 0 or args.noise < 0:
    cli.error("scale为正、noise非负且有限")
points = np.array([[x, y, z] for x in [-.1, .1]
                   for y in [-.1, .1] for z in [0., .2]])*args.scale
truth = pose([.1, .2, 0.], [0., 0., 2.*args.scale])
pixels = project(points, truth)
observed = pixels+np.random.default_rng(42).normal(0, args.noise, pixels.shape)
if args.swap: observed[[0, 7]] = observed[[7, 0]]
ok, r, t = cv2.solvePnP(points, observed, K, None, flags=cv2.SOLVEPNP_ITERATIVE)
if not ok: raise RuntimeError("PnP失败")
estimated = pose(r, t.ravel()); dlt = solve(points, observed, K)
results = {}
for name, T in (("pnp", estimated), ("dlt", dlt)):
    positive = bool(np.all(transform(points, T)[:, 2]>0))
    error = project(points, T)-observed if positive else None
    results[name] = {"rms_pixel": float(np.sqrt(np.mean(np.sum(error**2, axis=1)))) if positive else None,
        "translation": T[:3, 3].tolist(), "positive_depth": bool(np.all(transform(points, T)[:, 2]>0)),
        "rotation_determinant": float(np.linalg.det(T[:3, :3]))}
indices = [0, 3, 5]
count, rotations, translations = cv2.solveP3P(points[indices], observed[indices], K, None, cv2.SOLVEPNP_P3P)
results["p3p_candidates"] = []
extra = [i for i in range(len(points)) if i not in indices]
for rv, tv in zip(rotations, translations):
    T = pose(rv, tv.ravel()); positive = bool(np.all(transform(points, T)[:, 2]>0))
    squared = np.sum((project(points, T)-observed)**2, axis=1) if positive else None
    rms = lambda subset: float(np.sqrt(np.mean(squared[subset]))) if positive else None
    results["p3p_candidates"].append({"rms_all_points": rms(list(range(len(points)))),
        "rms_three_points": rms(indices), "rms_extra_points": rms(extra),
        "positive_depth": positive, "translation": tv.ravel().tolist()})
results["p3p_count"] = count
print(json.dumps(results))
