"""单帧离线接收：已知频偏、整样本定时与固定 8 字节帧。"""
import numpy as np
from frame import FRAME_BYTES, PREAMBLE, parse_frame


def decode(iq, metadata):
    fs = metadata["sample_rate_hz"]
    sps = metadata["samples_per_symbol"]
    offset = metadata["known_offset_hz"]
    if not isinstance(sps, int) or sps < 1:
        raise ValueError("每符号采样数必须是正整数")
    count = (len(PREAMBLE) + FRAME_BYTES * 8) * sps
    if len(iq) < count:
        raise ValueError("录包不足一个完整帧")
    n = np.arange(len(iq))
    corrected = iq * np.exp(-2j * np.pi * offset * n / fs)
    template = np.repeat(1.0 - 2.0 * PREAMBLE, sps)
    correlation = np.convolve(corrected, template[::-1], mode="valid")
    # 仅搜索能够容纳完整帧的起点。
    start = int(np.argmax(np.abs(correlation[:len(iq) - count + 1])))
    score = abs(correlation[start]) / len(template)
    if score < 0.5:
        raise ValueError("前导相关太弱")
    phase = np.angle(correlation[start])
    aligned = corrected[start:start + count] * np.exp(-1j * phase)
    means = aligned.reshape(-1, sps).mean(axis=1)
    bits = (means.real < 0).astype(np.uint8)
    if not np.array_equal(bits[:len(PREAMBLE)], PREAMBLE):
        raise ValueError("前导判决失败")
    frame = np.packbits(bits[len(PREAMBLE):]).tobytes()
    fields = parse_frame(frame)
    details = {"start": start, "phase": float(phase), "score": float(score),
               "correlation": correlation, "means": means,
               "corrected": corrected, "frame_hex": frame.hex()}
    return fields, details
