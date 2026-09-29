"""已知对应的刚体拟合，及实际迭代更新最近邻的ICP。"""
import argparse
import json
import numpy as np
from scipy.spatial import cKDTree
from model import pose, transform
from dlt import rotation_projection

def rigid(source, target):
    a, b = source.mean(axis=0), target.mean(axis=0)
    X, Y = source-a, target-b
    if np.linalg.matrix_rank(X)<2 or np.linalg.matrix_rank(Y)<2:
        raise ValueError("共线或重复点不能唯一约束三维旋转")
    R = rotation_projection(Y.T @ X)
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = b-R @ a
    return T

def icp(source, target, initial, iterations=30):
    tree = cKDTree(target); T = initial.copy(); history = []
    for _ in range(iterations):
        moved = transform(source, T)
        distance, indices = tree.query(moved)
        value = float(np.mean(distance**2)); history.append(value)
        delta = rigid(moved, target[indices])
        T = delta @ T
        if np.linalg.norm(delta-np.eye(4))<1e-10: break
    history.append(float(np.mean(tree.query(transform(source, T))[0]**2)))
    return T, history

if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--initial-shift", type=float, default=0.)
    args = cli.parse_args()
    if not np.isfinite(args.initial_shift): cli.error("初始偏移须有限")
    source = np.random.default_rng(2026).uniform(-1, 1, (40, 3))
    truth = pose([.05, .02, -.03], [.07, -.04, .03])
    target = transform(source, truth)
    known = rigid(source, target)
    estimated, history = icp(source, target, pose([0., 0., 0.], [args.initial_shift, 0., 0.]))
    assert np.allclose(known, truth)
    print(json.dumps({"known_max_error": float(np.max(abs(known-truth))),
        "icp_nearest_rms": float(np.sqrt(history[-1])),
        "icp_known_pair_rms": float(np.sqrt(np.mean(np.sum((transform(source, estimated)-target)**2, axis=1)))),
        "icp_transform_max_error": float(np.max(abs(estimated-truth))),
        "nearest_cost_nonincreasing": bool(np.all(np.diff(history)<=1e-12)),
        "iterations": len(history)-1, "history": history}))
