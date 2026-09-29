"""三相机联合BA；固定首相机和首点深度，显式去掉规范自由度。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from scipy.optimize import least_squares
from model import pose, project, sample
from schur import solve

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--noise", type=float, default=.3)
cli.add_argument("--outlier", type=float, default=0.)
cli.add_argument("--loss", choices=("linear", "huber"), default="linear")
cli.add_argument("--output", type=Path, default=Path("out/bundle"))
args = cli.parse_args()
if not np.isfinite([args.noise, args.outlier]).all() or min(args.noise, args.outlier)<0:
    cli.error("噪声和异常偏移须非负有限")
truth_points = sample(); truth_points[0, 2] = 3.5
truth_poses = np.array([[.01, .02, 0., -.3, 0., 0.],
                        [-.02, .03, .01, -.6, .05, .02]])
def matrices(parameters):
    return [np.eye(4)]+[pose(row[:3], row[3:]) for row in parameters]
def projections(parameters, points):
    return np.array([project(points, T) for T in matrices(parameters)])
truth_pixels = projections(truth_poses, truth_points)
rng = np.random.default_rng(2026)
observed = truth_pixels+rng.normal(0, args.noise, truth_pixels.shape)
observed[2, 0] += [args.outlier, -args.outlier]
initial_poses = truth_poses+rng.normal(0, .025, truth_poses.shape)
initial_points = truth_points+rng.normal(0, .06, truth_points.shape)
initial_points[0, 2] = 3.5
# 首相机固定为I；首点Z=3.5作为已知深度锚。其余59个点分量仍参与优化。
mask = np.ones(truth_points.size, bool); mask[2] = False
def pack(parameters, points):
    return np.r_[parameters.ravel(), points.ravel()[mask]]
def unpack(x):
    points = np.empty(truth_points.size); points[mask] = x[12:]; points[2] = 3.5
    return x[:12].reshape(2, 6), points.reshape(-1, 3)
def error(x):
    parameters, points = unpack(x)
    return (observed-projections(parameters, points)).ravel()
x0 = pack(initial_poses, initial_points)
# 有限边界保证本演示全部候选点在正深度范围内，不能照搬到任意场景。
camera_lower = np.tile([-.2, -.2, -.2, -.8, -.8, -.8], 2)
camera_upper = -camera_lower
point_lower = np.tile([-1.5, -1.5, 2.], len(truth_points))[mask]
point_upper = np.tile([1.5, 1.5, 6.], len(truth_points))[mask]
solution = least_squares(error, x0, bounds=(np.r_[camera_lower, point_lower],
    np.r_[camera_upper, point_upper]), loss=args.loss, f_scale=2.,
    jac="3-point", max_nfev=100, ftol=1e-10, xtol=1e-10, gtol=1e-10)
if not solution.success: raise RuntimeError(solution.message)
parameters, points = unpack(solution.x); final = projections(parameters, points)
# 核对当前阻尼近似方程，不复现SciPy的边界信赖域步长。
J = solution.jac; H = J.T @ J+np.eye(len(x0))*1e-3
g = -solution.grad  # Huber时J已修正，不能再与原始fun直接配对。
schur = solve(H, g, 12); direct = np.linalg.solve(H, g)
difference = float(np.max(abs(schur-direct)))
assert difference < 1e-8
clean = np.ones(observed.shape[:2], bool); clean[2, 0] = False
result = {"synthetic": True, "variables": len(x0), "residuals": observed.size,
    "first_pose_fixed": True, "known_first_point_depth_m": 3.5,
    "initial_rms_pixel": float(np.sqrt(np.mean(np.sum(error(x0).reshape(3, -1, 2)**2, axis=2)))),
    "final_rms_pixel": float(np.sqrt(np.mean(np.sum((observed-final)**2, axis=2)))),
    "clean_truth_rms_pixel": float(np.sqrt(np.mean(np.sum((final-truth_pixels)[clean]**2, axis=1)))),
    "point_rmse_m": float(np.sqrt(np.mean(np.sum((points-truth_points)**2, axis=1)))),
    "jacobian_rank": int(np.linalg.matrix_rank(J)), "schur_max_difference": difference,
    "evaluations": solution.nfev, "loss": args.loss}
args.output.mkdir(parents=True, exist_ok=True)
np.savez(args.output/"result.npz", observed=observed, initial=projections(initial_poses, initial_points),
    final=final, truth=truth_pixels, points=points, poses=parameters)
(args.output/"metrics.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result))
