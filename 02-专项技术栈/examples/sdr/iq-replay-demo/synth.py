"""固定种子合成矩形脉冲 BPSK，频偏是已知教学输入。"""
import numpy as np
from frame import PREAMBLE, make_frame, to_bits


def synthesize(x_mm=1250, phase=0.7, offset_hz=125,
               noise=0.03, prefix=19, corrupt=False):
    fs, sps = 8000, 8
    bits = np.concatenate([PREAMBLE, to_bits(make_frame(x_mm, corrupt))])
    symbols = 1.0 - 2.0 * bits
    base = np.concatenate([np.zeros(prefix), np.repeat(symbols, sps),
                           np.zeros(11)])
    n = np.arange(len(base))
    rotation = np.exp(1j * (phase + 2 * np.pi * offset_hz * n / fs))
    rng = np.random.default_rng(2026)
    disturbance = noise * (rng.standard_normal(len(base))
                           + 1j * rng.standard_normal(len(base)))
    iq = (base * rotation + disturbance).astype(np.complex64)
    metadata = {"sample_rate_hz": fs, "samples_per_symbol": sps,
                "known_offset_hz": offset_hz, "source": "synthetic-bpsk"}
    return iq, metadata
