"""仅读取保存数组，比较响应与实际闭环，不重新求解。"""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--kind", choices=["response", "control"], required=True)
cli.add_argument("--input", type=Path, required=True)
cli.add_argument("--compare", type=Path, required=True)
cli.add_argument("--compare-label", default="N=1")
cli.add_argument("--output", type=Path, required=True)
cli.add_argument("--font", type=Path,
    default=Path(__file__).resolve().parents[4]/"fonts/站酷高端黑.ttf")
args = cli.parse_args(); font_manager.fontManager.addfont(str(args.font))
plt.rcParams.update({"font.family": font_manager.FontProperties(fname=str(args.font)).get_name(),
    "font.size": 13, "axes.unicode_minus": False, "axes.spines.top": False,
    "axes.spines.right": False, "pdf.fonttype": 3 if args.font.suffix == ".otf" else 42})
data = np.load(args.input); other = np.load(args.compare)
if args.kind == "response":
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    axes[0].plot(data["k"][:31], data["step"][:31], color="#0091a0", label="a=0.8")
    axes[0].plot(other["k"][:31], other["step"][:31], color="#666666", linestyle="--", label="a=0.5")
    axes[0].axhline(.9, color="#aaaaaa", linewidth=.8)
    axes[0].set(xlabel="离散步数 k", ylabel="阶跃输出 y[k]")
    select = data["t"] <= 1
    for key, label, style in [("reference", "两频率输入", "-"), ("delayed", "仅延时20ms", "--"),
                              ("filtered", "一阶稳态输出", ":")]:
        axes[1].plot(data["t"][select], data[key][select], style, label=label)
    axes[1].set(xlabel="时间 / s", ylabel="信号值（归一化）")
else:
    fig, grid = plt.subplots(2, 2, figsize=(10, 6.5), layout="constrained")
    axes = grid.ravel()
    for arrays, label, color, style in [(data, "N=15", "#0091a0", "-"), (other, args.compare_label, "#666666", "--")]:
        dt = float(arrays["dt"])
        t = np.arange(len(arrays["states"]))*dt
        axes[0].plot(t, arrays["states"][:, 0],
                     color=color, linestyle=style, label=label)
        axes[1].plot(t, arrays["states"][:, 1], color=color, linestyle=style, label=label)
        axes[2].step(np.arange(len(arrays["controls"]))*dt, arrays["controls"], where="post",
                     color=color, linestyle=style, label=label)
        axes[3].plot(t, float(arrays["reference"])-arrays["states"][:, 0],
                     color=color, linestyle=style, label=label)
    axes[0].axhline(float(data["reference"]), color="#aaaaaa", linewidth=.8, label="参考角度")
    for sign in (-1, 1):
        axes[1].axhline(sign*float(data["vmax"]), color="#aaaaaa", linewidth=.8)
        axes[2].axhline(sign*float(data["amax"]), color="#aaaaaa", linewidth=.8)
    axes[0].set(xlabel="模拟时间 / s", ylabel="角度 / rad")
    axes[1].set(xlabel="模拟时间 / s", ylabel="角速度 / rad/s")
    axes[2].set(xlabel="模拟时间 / s", ylabel=r"实际输入 / rad/s$^2$")
    axes[3].set(xlabel="模拟时间 / s", ylabel="参考减实际 / rad")
for ax in axes: ax.legend(fontsize=11); ax.grid(alpha=.2)
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output); plt.close(fig); print(args.output)
