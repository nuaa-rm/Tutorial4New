"""固定随机种子的小模型，不把加噪图当传感器实测。"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--photons", type=float, default=900.)
cli.add_argument("--output", type=Path, default=Path("out/noise"))
args = cli.parse_args()
if not np.isfinite(args.photons) or args.photons <= 0:
    cli.error("光子期望数须为正有限数")
rng = np.random.default_rng(2026)
counts = rng.poisson(args.photons, 100000)
base = np.tile(np.linspace(20, 220, 256), (128, 1))
images = {"raw": base, "gaussian": base+rng.normal(0, 15, base.shape),
          "poisson": rng.poisson(base), "multiplicative": base*(1+rng.normal(0, .2, base.shape))}
salt = base.copy()
choices = rng.random(base.shape)
salt[choices < .03] = 0; salt[choices > .97] = 255
images["salt"] = salt
args.output.mkdir(parents=True, exist_ok=True)
for name, image in images.items():
    assert cv2.imwrite(str(args.output / f"{name}.png"), np.clip(image, 0, 255).astype(np.uint8))
print(json.dumps({"photons": args.photons, "expected_std": float(np.sqrt(args.photons)),
                  "relative_std": float(1/np.sqrt(args.photons)),
                  "sample_mean": float(counts.mean()), "sample_std": float(counts.std()),
                  "salt_count": int(np.count_nonzero((choices<.03)|(choices>.97)))}))
