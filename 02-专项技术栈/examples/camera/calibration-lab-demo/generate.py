"""生成已知针孔模型的棋盘格，不把模拟图当实拍。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from board import SQUARE, SIZE

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--output", type=Path, default=Path("data"))
args = cli.parse_args()
root = args.output
for group in ("train", "validation", "front", "left", "right"):
    (root / group).mkdir(parents=True, exist_ok=True)
K = np.array([[560., 0., 320.], [0., 565., 240.], [0., 0., 1.]])
D = np.array([-0.18, 0.04, 0.001, -0.001, 0.])
texture = np.kron((np.indices((7, 10)).sum(axis=0) % 2) * 255,
                  np.ones((64, 64))).astype(np.uint8)
outer = np.array([[-1, -1, 0], [9, -1, 0], [9, 6, 0], [-1, 6, 0]],
                 np.float32) * SQUARE
source = np.array([[0, 0], [640, 0], [640, 448], [0, 448]], np.float32)
pixels = np.stack(np.meshgrid(np.arange(640), np.arange(480)), -1)
maps = cv2.undistortPoints(pixels.astype(np.float32).reshape(-1, 1, 2), K, D, P=K)
maps = maps.reshape(480, 640, 2)


def render(rvec, tvec):
    corners, _ = cv2.projectPoints(outer, rvec, tvec, K, np.zeros(5))
    homography = cv2.getPerspectiveTransform(source, corners.reshape(4, 2))
    ideal = cv2.warpPerspective(texture, homography, SIZE, borderValue=127)
    return cv2.remap(ideal, maps[:, :, 0], maps[:, :, 1],
                     cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=127)


rng = np.random.default_rng(2026)
counts = dict.fromkeys(("train", "validation", "front", "left", "right"), 0)
poses = []
for i in range(100):
    rvec = rng.uniform([-0.65, -0.65, -0.2], [0.65, 0.65, 0.2])
    z = rng.uniform(0.48, 1.15)
    center = np.array([rng.uniform(-0.22, 0.22), rng.uniform(-0.15, 0.15), z])
    R, _ = cv2.Rodrigues(rvec)
    tvec = center - R @ np.array([0.1, 0.0625, 0.])
    projected, _ = cv2.projectPoints(outer, rvec, tvec, K, D)
    p = projected.reshape(-1, 2)
    if np.any(p < [8, 8]) or np.any(p > [632, 472]):
        continue
    group = "validation" if i % 7 == 0 else "train"
    name = f"{i:03}.png"
    assert cv2.imwrite(str(root / group / name), render(rvec, tvec))
    counts[group] += 1
    poses.append({"name": name, "group": group, "rvec": rvec.tolist(), "tvec": tvec.tolist()})
    right_t = tvec - np.array([0.12, 0., 0.])
    right, _ = cv2.projectPoints(outer, rvec, right_t, K, D)
    p = right.reshape(-1, 2)
    if np.all(p >= [8, 8]) and np.all(p <= [632, 472]):
        for side, t in (("left", tvec), ("right", right_t)):
            assert cv2.imwrite(str(root / side / name), render(rvec, t))
            counts[side] += 1
for i in range(12):
    rvec = np.zeros(3)
    tvec = np.array([-0.1 + (i % 4 - 1.5) * .035,
                     -0.0625 + (i // 4 - 1) * .03, .7 + (i % 3) * .05])
    assert cv2.imwrite(str(root / "front" / f"{i:03}.png"), render(rvec, tvec))
    counts["front"] += 1
(root / "truth.json").write_text(json.dumps(
    {"synthetic": True, "K": K.tolist(), "D": D.tolist(), "baseline_m": .12,
     "square_m": SQUARE, "counts": counts, "poses": poses}, indent=2))
print(json.dumps({"synthetic": True, "counts": counts}))
