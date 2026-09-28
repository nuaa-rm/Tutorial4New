"""用对应图像求双目固定外参，检查校正后的纵坐标差。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from board import object_points, detect
from model_io import load_yaml, save_matrices

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--data", type=Path, default=Path("data"))
cli.add_argument("--model", type=Path, default=Path("out/front.yaml"))
cli.add_argument("--output", type=Path, default=Path("out/stereo"))
args = cli.parse_args()
K, D, _, _, size = load_yaml(args.model)
objects, lefts, rights = [], [], []
for path in sorted((args.data / "left").glob("*.png")):
    a = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(str(args.data / "right" / path.name), cv2.IMREAD_GRAYSCALE)
    if a is None or b is None or a.shape != (size[1], size[0]) or b.shape != a.shape:
        raise ValueError("双目图像缺失或模式不同")
    ca, cb = detect(a), detect(b)
    if ca is not None and cb is not None:
        objects.append(object_points()); lefts.append(ca); rights.append(cb)
if len(objects) < 10:
    raise ValueError("有效双目对不足")
rms, K1, D1, K2, D2, R, T, E, F = cv2.stereoCalibrate(
    objects, lefts, rights, K.copy(), D.copy(), K.copy(), D.copy(), size,
    flags=cv2.CALIB_FIX_INTRINSIC)
R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(K1, D1, K2, D2, size, R, T, alpha=0)
differences = []
for a, b in zip(lefts, rights):
    ca = cv2.undistortPoints(a, K1, D1, R=R1, P=P1).reshape(-1, 2)
    cb = cv2.undistortPoints(b, K2, D2, R=R2, P=P2).reshape(-1, 2)
    differences.extend((ca[:, 1]-cb[:, 1]).tolist())
args.output.mkdir(parents=True, exist_ok=True)
save_matrices(args.output/"left.yaml", K1, D1.reshape(-1), R1, P1, size, "front")
save_matrices(args.output/"right.yaml", K2, D2.reshape(-1), R2, P2, size, "front")
print(json.dumps({"pairs": len(objects), "rms_px": rms, "T_m": T.reshape(-1).tolist(),
                  "baseline_from_P_m": float(-P2[0, 3]/P2[0, 0]),
                  "epipolar_rms_px": float(np.sqrt(np.mean(np.square(differences))))}))
