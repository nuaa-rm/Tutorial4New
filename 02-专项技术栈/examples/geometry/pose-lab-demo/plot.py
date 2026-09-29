"""仅读取实际投影数组，画优化前后的像素残差。"""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--input", type=Path, required=True)
cli.add_argument("--output", type=Path, required=True)
cli.add_argument("--font", type=Path,
    default=Path(__file__).resolve().parents[4]/"fonts/站酷高端黑.ttf")
args = cli.parse_args()
font_manager.fontManager.addfont(str(args.font))
plt.rcParams.update({"font.family": font_manager.FontProperties(fname=str(args.font)).get_name(),
    "font.size": 13, "axes.unicode_minus": False, "axes.spines.top": False,
    "axes.spines.right": False, "pdf.fonttype": 3 if args.font.suffix==".otf" else 42})
data = np.load(args.input)
fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), layout="constrained")
for ax, key, title in zip(axes, ("initial", "final"), ("优化前", "优化后")):
    error = (data[key]-data["observed"]).reshape(-1, 2)
    ax.scatter(error[:, 0], error[:, 1], color="#0091a0", s=20, label="实际观测残差")
    ax.axhline(0, color="#aaaaaa", linewidth=.8)
    ax.axvline(0, color="#aaaaaa", linewidth=.8)
    ax.set(title=title, xlabel="u残差 / pixel", ylabel="v残差 / pixel")
    ax.grid(alpha=.2); ax.set_aspect("equal", adjustable="box")
bound = max(.5, float(np.max(abs((data["initial"]-data["observed"]).ravel())))*1.05)
for ax in axes: ax.set_xlim(-bound, bound); ax.set_ylim(-bound, bound)
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output); plt.close(fig)
print(args.output)
