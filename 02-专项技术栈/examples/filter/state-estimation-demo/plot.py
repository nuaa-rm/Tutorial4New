"""读取实际运行数组画图；滤波不在绘图时重新计算。"""
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
    "axes.spines.right": False, "pdf.fonttype": 3 if args.font.suffix == ".otf" else 42})
data = np.load(args.input)
cyan, gray, orange = "#0091a0", "#777777", "#bf6b22"
fig, axes = plt.subplots(2, 1, figsize=(10, 6), layout="constrained")
if "low" in data:
    t = np.arange(len(data["truth"]))
    for key, color, label in (("truth", gray, "真值"), ("observed", "#aaaaaa", "观测"),
                             ("low", cyan, "低通"), ("average", orange, "尾部均值")):
        axes[0].plot(t, data[key], color=color, label=label, linewidth=1.4)
    axes[1].plot(t, data["low"]-data["truth"], color=cyan, label="低通误差")
    axes[1].plot(t, data["average"]-data["truth"], color=orange, label="均值误差")
    axes[0].set_ylabel("幅值"); axes[1].set(xlabel="样本编号", ylabel="估计 - 真值")
else:
    t = np.arange(1, len(data["truth"])+1)*float(data["dt"])
    axes[0].plot(t, data["truth"][:, 0], color=gray, label="位置真值")
    axes[0].plot(t, data["estimate"][:, 0], color=cyan, label="KF / EKF")
    axes[0].plot(t, data["ukf"][:, 0], "--", color=orange, label="UKF")
    axes[1].plot(t, data["innovations"], color=cyan, label="创新量")
    axes[1].plot(t, data["estimate"][:, 0]-data["truth"][:, 0], color=gray, label="位置误差")
    axes[0].set_ylabel("位置 / m"); axes[1].set(xlabel="时间 / s", ylabel="残差 / m")
for ax in axes:
    ax.grid(alpha=.2); ax.legend(loc="upper left", fontsize=12)
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output); plt.close(fig)
print(args.output)
