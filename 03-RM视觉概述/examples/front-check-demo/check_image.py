"""记录实际文件和8位图像观测；不从图片猜相机曝光、序列号。"""
import argparse
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np


def inspect(path):
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError("文件打不开")
    if image.dtype != np.uint8 or image.ndim not in (2, 3):
        raise ValueError("本例仅检查8位灰度/BGR图")
    if image.ndim == 3 and image.shape[2] != 3:
        raise ValueError("本例不解释其他通道格式")
    near_max = image >= 250
    if image.ndim == 3:
        near_max = np.any(near_max, axis=2)
    return {"file": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "width": image.shape[1], "height": image.shape[0],
            "channels": 1 if image.ndim == 2 else 3,
            "near_max_fraction": float(near_max.mean()),
            "camera_serial": None, "exposure_us": None, "sample_clock": None}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("image", type=Path)
    a = p.parse_args()
    try:
        print(json.dumps(inspect(a.image), ensure_ascii=False))
    except ValueError as error:
        p.error(str(error))


if __name__ == "__main__":
    main()
