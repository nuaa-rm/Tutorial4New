"""从照片检测角点、拟合、保存；不读取生成器真值。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from board import object_points, detect, SQUARE
from model_io import save_yaml

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--images", type=Path, default=Path("data/train"))
cli.add_argument("--output", type=Path, default=Path("out"))
cli.add_argument("--square", type=float, default=SQUARE)
args = cli.parse_args()
if args.square <= 0 or not np.isfinite(args.square):
    cli.error("方格边长须为正有限数，单位米")
objects, images, used = [], [], []
size = None
for path in sorted(args.images.glob("*.png")):
    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise ValueError(f"读图失败：{path}")
    current = (gray.shape[1], gray.shape[0])
    if size is not None and size != current:
        raise ValueError("照片分辨率不一致")
    size = current
    corners = detect(gray)
    if corners is None:
        continue
    objects.append(object_points(args.square)); images.append(corners); used.append(path.name)
if len(used) < 10:
    raise ValueError("有效照片不足 10 张；这也不是质量保证的张数")
rms, K, D, rvecs, tvecs = cv2.calibrateCamera(
    objects, images, size, None, None, flags=cv2.CALIB_FIX_K3)
per_view = []
for obj, observed, r, t in zip(objects, images, rvecs, tvecs):
    predicted, _ = cv2.projectPoints(obj, r, t, K, D)
    per_view.append(float(np.sqrt(np.mean(np.sum((predicted-observed)**2, axis=2)))))
args.output.mkdir(parents=True, exist_ok=True)
np.savez(args.output / "model.npz", K=K, D=D, size=size, square=args.square, tvecs=tvecs)
save_yaml(args.output / "front.yaml", K, D, size)
metrics = {"count": len(used), "rms_px": rms, "files": used,
           "per_view_rms_px": per_view, "K": K.tolist(), "D": D.reshape(-1).tolist()}
(args.output / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics))
