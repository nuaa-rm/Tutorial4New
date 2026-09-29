"""生成理想移动竖条，观察行间时序与曝光期间平均；不是实拍。"""
import argparse
from pathlib import Path
import cv2
import numpy as np


def render(exposure_ms, row_span_ms):
    x = np.arange(160)[None, :]
    row_start = np.linspace(0, row_span_ms, 64)[:, None]
    image = np.zeros((64, 160), dtype=float)
    for fraction in (np.arange(32) + 0.5) / 32:
        left = 30 + 4 * (row_start + fraction * exposure_ms)
        image += (x >= left) & (x < left + 8)
    # 对曝光采样取平均，固定亮度尺度；不模拟长曝光的光子数量。
    return np.rint(20 + 200 * image / 32).astype(np.uint8)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("out"))
    a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    for name, exposure, row_span in [("global_short", 1, 0),
                                    ("rolling_short", 1, 8),
                                    ("global_long", 6, 0)]:
        assert cv2.imwrite(str(a.output / (name + ".png")), render(exposure, row_span))
    print(a.output.resolve())


if __name__ == "__main__":
    main()
