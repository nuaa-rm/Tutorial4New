"""读取实际保存的地图、路径和Nav2轨迹，不重新模拟控制。"""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
from scipy.ndimage import distance_transform_edt

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--map", type=Path, required=True)
cli.add_argument("--nav2", type=Path, required=True)
cli.add_argument("--output", type=Path, required=True)
cli.add_argument("--font", type=Path,
    default=Path("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"))
args = cli.parse_args()
font = FontProperties(fname=str(args.font), size=12)
plt.rcParams.update({"axes.unicode_minus": False, "pdf.compression": 0,
    "font.size": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "pdf.fonttype": 3 if args.font.suffix.lower()==".otf" else 42})
occupied = np.load(args.map/"grid.npz")["occupied"]
paths = json.loads((args.map/"paths.json").read_text())
nav = np.load(args.nav2/"nav2.npz")
fig, axes = plt.subplots(1, 2, figsize=(9, 4.7), constrained_layout=True)
for ax in axes:
    ax.pcolormesh(np.arange(61)*.1, np.arange(41)*.1, occupied,
                  cmap="Greys", vmin=0, vmax=1, shading="flat", rasterized=False)
    ax.set(xlim=(0, 6), ylim=(0, 4), aspect="equal", xlabel="x / m", ylabel="y / m")
    ax.grid(alpha=.15)
for name, color in [("dijkstra", "#7e91a4"), ("astar", "#0091a0")]:
    xy=(np.array(paths[name][0])+.5)*.1
    axes[0].plot(*xy.T, color=color, label=name)
axes[0].contour((np.arange(60)+.5)*.1, (np.arange(40)+.5)*.1,
    distance_transform_edt(~occupied)*.1, levels=[.35], colors=["#dd8b45"])
axes[0].set_title("四邻接离线路线\n橙线：0.35 m格心距离边界", fontproperties=font)
axes[1].plot(*nav["path"].T, color="#dd8b45", label="Navfn path")
axes[1].plot(*nav["trajectory"].T, color="#0091a0", label="RPP + software model")
axes[1].set_title("实际Nav2路径\n与软件里程计轨迹", fontproperties=font)
for ax in axes:
    ax.scatter([.55, 5.05], [.55, 3.05], c="#0091a0", s=28)
    ax.legend(fontsize=11, loc="upper left")
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output); plt.close(fig)
print(json.dumps({"output":str(args.output), "path_poses":len(nav["path"]),
                  "trajectory_samples":len(nav["trajectory"])}))
