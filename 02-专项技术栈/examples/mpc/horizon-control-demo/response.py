"""分开观察一阶阶跃、稳态频响、纯延时和几何半角。"""
import argparse
import json
from pathlib import Path
import numpy as np

def analyze(a=.8, delay=.02, distance=5.):
    if not np.isfinite([a, delay, distance]).all() or not 0 <= a < 1:
        raise ValueError("a须在[0,1)，参数须有限")
    if delay < 0 or distance <= 0:
        raise ValueError("延时非负、距离为正")
    # u[k]=1，y[0]=0；输出序列包含初始值。
    k = np.arange(201); y = 1-a**k
    dt = .01; t = np.arange(501)*dt
    reference = np.sin(2*np.pi*t)+.3*np.sin(20*np.pi*t)
    delayed = np.sin(2*np.pi*(t-delay))+.3*np.sin(20*np.pi*(t-delay))
    # y[k+1]=a*y[k]+(1-a)*u[k]的离散稳态响应。
    frequency = np.array([1., 10.])
    H = (1-a)/(np.exp(2j*np.pi*frequency*dt)-a)
    filtered = sum(amp*abs(h)*np.sin(2*np.pi*f*t+np.angle(h))
                   for amp, f, h in zip([1., .3], frequency, H))
    result = {"first_three": y[1:4].tolist(),
              "steps_90": int(np.flatnonzero(y >= .9)[0]),
              "steps_98": int(np.flatnonzero(y >= .98)[0]),
              "phase_delay_rad": (-2*np.pi*frequency*delay).tolist(),
              "steady_gain": abs(H).tolist(), "steady_phase": np.angle(H).tolist(),
              "epsilon_rad": float(np.arctan(.1/(2*distance)))}
    return result, dict(k=k, step=y, t=t, reference=reference,
                        delayed=delayed, filtered=filtered)

if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--a", type=float, default=.8)
    cli.add_argument("--delay", type=float, default=.02)
    cli.add_argument("--distance", type=float, default=5.)
    cli.add_argument("--output", type=Path, default=Path("out/response"))
    args = cli.parse_args()
    try: result, arrays = analyze(args.a, args.delay, args.distance)
    except ValueError as error: cli.error(str(error))
    args.output.mkdir(parents=True, exist_ok=True)
    np.savez(args.output/"result.npz", **arrays)
    print(json.dumps(result, ensure_ascii=False))
