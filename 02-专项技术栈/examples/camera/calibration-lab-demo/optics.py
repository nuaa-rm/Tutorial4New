"""单位固定为 mm、ms、pixel/s；只做声明的薄透镜近似。"""
import argparse
import json
import math

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--f", type=float, default=16.)
cli.add_argument("--aperture", type=float, default=4.)
cli.add_argument("--circle", type=float, default=.01)
cli.add_argument("--distance", type=float, default=2000.)
cli.add_argument("--speed", type=float, default=800.)
cli.add_argument("--exposure", type=float, default=2.)
cli.add_argument("--budget", type=float, default=1.)
args = cli.parse_args()
if not all(math.isfinite(v) and v > 0 for v in vars(args).values()):
    cli.error("参数须为正有限数")
f, N, c, s = args.f, args.aperture, args.circle, args.distance
if s <= f:
    cli.error("此估算要求物距大于焦距")
h = f*f/(N*c)
near = h*s/(h+s-f)
far = h*s/(h-s+f) if h-s+f > 0 else None
fx, fy, cx, cy, u0, v0, sx, sy = 800., 800., 640., 480., 100., 50., .5, .5
print(json.dumps({"f_number": N, "hyperfocal_mm": h+f,
                  "near_mm": near, "far_mm": far,
                  "blur_px": args.speed*args.exposure/1000,
                  "max_exposure_ms": args.budget/args.speed*1000,
                  "f4_to_f56_ratio": (5.6/4)**2,
                  "width_8_to_12_px": 20*12/8,
                  "crop_K": [[sx*fx, 0., sx*(cx-u0)],
                             [0., sy*fy, sy*(cy-v0)], [0., 0., 1.]],
                  "stereo_baseline_m": -(-96)/800,
                  "sync_error_m": 3*.008, "hdr_shift_px": 1000*.010}))
