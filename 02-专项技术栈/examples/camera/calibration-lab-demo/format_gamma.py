"""核对 Bayer/RGB 字节和 Gamma 查表；输入不是真实相机 RAW。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--gamma", type=float, default=2.2)
cli.add_argument("--output", type=Path, default=Path("out/format"))
args = cli.parse_args()
if not np.isfinite(args.gamma) or args.gamma <= 0:
    cli.error("gamma 须为正有限数")
bayer = np.empty((6, 8), np.uint8)
bayer[0::2, 0::2] = 200; bayer[0::2, 1::2] = 100
bayer[1::2, 0::2] = 100; bayer[1::2, 1::2] = 50
bgr = cv2.cvtColor(bayer, cv2.COLOR_BayerRGGB2BGR)
assert bgr[2, 2].tolist() == [50, 100, 200]
lut = np.array([round(255*(i/255)**(1/args.gamma)) for i in range(256)], np.uint8)
assert lut[0] == 0 and lut[255] == 255
ramp = np.tile(np.arange(256, dtype=np.uint8), (64, 1))
args.output.mkdir(parents=True, exist_ok=True)
for name, image in (("bgr.png", bgr), ("ramp.png", ramp), ("mapped.png", cv2.LUT(ramp, lut))):
    assert cv2.imwrite(str(args.output / name), image)
print(json.dumps({"bayer_bytes": bayer.nbytes, "bgr_bytes": bgr.nbytes,
                  "center_bgr": bgr[2, 2].tolist(), "gamma": args.gamma,
                  "lut_128": int(lut[128]), "identity": bool(np.array_equal(lut, np.arange(256)))}))
