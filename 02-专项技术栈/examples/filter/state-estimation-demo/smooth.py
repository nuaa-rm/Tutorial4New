"""因果低通、尾部均值和互补高通；不偷偷使用未来样本。"""
import argparse
import json
from pathlib import Path
import numpy as np


def low_pass(values, alpha):
    if not np.isfinite(alpha) or not 0 < alpha <= 1:
        raise ValueError("alpha 在 (0,1]")
    y = 0.; result = []
    for value in values:
        y = alpha*value+(1-alpha)*y
        result.append(y)
    return np.array(result)


def moving_average(values, width):
    if width < 1:
        raise ValueError("窗口长度必须为正整数")
    return np.array([np.mean(values[max(0, i-width+1):i+1]) for i in range(len(values))])


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--alpha", type=float, default=.2)
    cli.add_argument("--window", type=int, default=10)
    cli.add_argument("--output", type=Path, default=Path("out/smooth"))
    args = cli.parse_args()
    rng = np.random.default_rng(42)
    truth = np.r_[np.zeros(50), np.ones(100)]
    observed = truth+rng.normal(0, .2, len(truth))
    low = low_pass(observed, args.alpha)
    average = moving_average(observed, args.window)
    high = observed-low
    assert np.allclose(low+high, observed)
    step = low_pass(np.ones(100), args.alpha)
    crossings = np.flatnonzero(step >= .9)
    reach = int(crossings[0]+1) if len(crossings) else None
    args.output.mkdir(parents=True, exist_ok=True)
    np.savez(args.output/"series.npz", truth=truth, observed=observed,
             low=low, average=average, high=high)
    print(json.dumps({"alpha": args.alpha, "window": args.window, "step90_samples": reach,
        "rmse": {n: float(np.sqrt(np.mean((v-truth)**2))) for n, v in
                 (("raw", observed), ("low", low), ("average", average))}}))
