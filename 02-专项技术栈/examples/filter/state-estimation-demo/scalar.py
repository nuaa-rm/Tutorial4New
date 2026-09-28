"""保留手算的一维随机游走，R 改变时观察实际权重。"""
import argparse
import json
import numpy as np
from linear import predict, update

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--r", type=float, default=.9)
args = cli.parse_args()
if not np.isfinite(args.r) or args.r <= 0:
    cli.error("R 必须是正有限方差")
x, P = predict(np.array([0.]), np.array([[1.]]), np.eye(1), np.array([[.1]]))
prior = float(P[0, 0])
x, P, residual, S = update(x, P, 2., np.eye(1), args.r)
print(json.dumps({"K": prior/float(S[0, 0]), "x": float(x[0]), "P": float(P[0, 0])}))
