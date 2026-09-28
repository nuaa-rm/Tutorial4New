"""固定内参与畸变，检查一张未参与拟合的图。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from board import object_points, detect, PATTERN

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--model", type=Path, default=Path("out/model.npz"))
cli.add_argument("--image", type=Path, required=True)
cli.add_argument("--output", type=Path, default=Path("out/validation"))
args = cli.parse_args()
model = np.load(args.model)
K, D = model["K"], model["D"]
gray = cv2.imread(str(args.image), cv2.IMREAD_GRAYSCALE)
if gray is None or (gray.shape[1], gray.shape[0]) != tuple(model["size"]):
    raise ValueError("验证图缺失或分辨率不同")
corners = detect(gray)
if corners is None:
    raise ValueError("未找到完整角点")
obj = object_points(float(model["square"]))
ok, rvec, tvec = cv2.solvePnP(obj, corners, K, D)
if not ok:
    raise ValueError("位姿求解失败")
predicted, _ = cv2.projectPoints(obj, rvec, tvec, K, D)
errors = np.linalg.norm((predicted-corners).reshape(-1, 2), axis=1)
size = tuple(model["size"])
new_K, roi = cv2.getOptimalNewCameraMatrix(K, D, size, 0., size)
rectified = cv2.undistort(gray, K, D, None, new_K)
args.output.mkdir(parents=True, exist_ok=True)
marked = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
cv2.drawChessboardCorners(marked, PATTERN, corners, True)
for name, image in (("corners.png", marked), ("rectified.png", rectified), ("raw.png", gray)):
    assert cv2.imwrite(str(args.output / name), image)
np.savez(args.output / "rectified_model.npz", K=new_K, D=np.zeros(5), size=size, roi=roi)
print(json.dumps({"rms_px": float(np.sqrt(np.mean(errors**2))),
                  "max_px": float(errors.max()), "roi": list(roi),
                  "fixed_intrinsics": True, "pose_estimated_from_this_image": True}))
