"""只含一维平移的位姿图，固定节点0，用方差白化相对约束。"""
import argparse
import json
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--loop", type=float, default=2.2)
args = cli.parse_args()
if not np.isfinite(args.loop): cli.error("闭环测量须有限")
# 相对位置约束 xj-xi=z；所有方差相同为0.01 m²。
edges = [(0, 1, 1.), (1, 2, 1.), (0, 2, args.loop)]
A, z = [], []
for i, j, measurement in edges:
    row = np.zeros(3); row[j] = 1.; row[i] = -1.
    A.append(row/.1); z.append(measurement/.1)
A, z = np.array(A), np.array(z)
# 固定x0=0，两个自由位置，使用lstsq而非显式逆正规矩阵。
free, _, rank, _ = np.linalg.lstsq(A[:, 1:], z, rcond=None)
positions = np.r_[0., free]
print(json.dumps({"positions_m": positions.tolist(), "rank_fixed": int(rank),
    "rank_unfixed": int(np.linalg.matrix_rank(A)),
    "weighted_residual_sum": float(np.sum((A @ positions-z)**2))}))
