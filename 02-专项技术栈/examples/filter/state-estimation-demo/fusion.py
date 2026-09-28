"""两个无偏标量估计的融合；不忽略交叉协方差。"""
import argparse
import json
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--v1", type=float, default=1.)
cli.add_argument("--v2", type=float, default=3.)
cli.add_argument("--rho", type=float, default=0.)
args = cli.parse_args()
if (not all(np.isfinite(v) for v in vars(args).values()) or
        args.v1 <= 0 or args.v2 <= 0 or abs(args.rho) > 1):
    cli.error("方差为正有限数，相关系数在 [-1,1]")
c = args.rho*np.sqrt(args.v1*args.v2)
denominator = args.v1+args.v2-2*c
# 完全相同的噪声不能靠重复融合得到更小方差。
weight = .5 if abs(denominator) < 1e-12 else (args.v2-c)/denominator
variance = weight**2*args.v1+(1-weight)**2*args.v2+2*weight*(1-weight)*c
print(json.dumps({"weight1": weight, "mean": weight*2+(1-weight)*4,
                  "variance": variance, "cross_covariance": c}))
