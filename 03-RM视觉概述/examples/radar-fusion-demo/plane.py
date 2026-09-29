"""固定教学相机：把高处像素误当成地面点，会偏到哪里？"""
import argparse
import json
import math
import cv2
import numpy as np


def demonstrate(height):
    if not math.isfinite(height) or not 0 <= height < 5:
        raise ValueError("教学高度须满足 0 <= height < 5 m")
    ground = np.float32([[0, 0], [4, 0], [4, 3], [0, 3]])
    pixels = np.float32([[80, 420], [560, 420], [560, 60], [80, 60]])
    # 四个地面对应点确定图像到场地平面的单应矩阵。
    H = cv2.getPerspectiveTransform(pixels, ground)
    # 相机中心 (2, 1.5, 5)，向下看；焦距600像素，主点(320,240)。
    x, y = 3.0, 2.0
    uv = np.float32([[[320 + 600 * (x - 2) / (5 - height),
                       240 - 600 * (y - 1.5) / (5 - height)]]])
    mapped = cv2.perspectiveTransform(uv, H)[0, 0].tolist()
    return {"height_m": height, "pixel": uv[0, 0].tolist(),
            "ground_mapping_m": mapped, "true_ground_projection_m": [x, y],
            "error_m": math.dist(mapped, [x, y])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--height", type=float, default=1.0)
    a = p.parse_args()
    try:
        print(json.dumps(demonstrate(a.height), allow_nan=False))
    except ValueError as error:
        p.error(str(error))


if __name__ == "__main__":
    main()
