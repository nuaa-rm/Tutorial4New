"""教学帧：命令、序号、毫米坐标和 CRC；不对应赛场协议。"""
import binascii
import struct
import numpy as np

PREAMBLE = np.array([1, 1, 1, 0, 1, 0, 0, 1,
                     0, 0, 0, 1, 0, 1, 1, 0], dtype=np.uint8)
FRAME_BYTES = 8


def make_frame(x_mm=1250, corrupt=False):
    body = struct.pack(">BBHH", 1, 7, x_mm, 2500)
    crc = binascii.crc_hqx(body, 0).to_bytes(2, "big")
    if corrupt:
        body = body[:2] + bytes([body[2] ^ 1]) + body[3:]
    return body + crc


def to_bits(frame):
    return np.unpackbits(np.frombuffer(frame, dtype=np.uint8))


def parse_frame(frame):
    if len(frame) != FRAME_BYTES:
        raise ValueError("帧长度错误")
    body, crc = frame[:-2], int.from_bytes(frame[-2:], "big")
    if binascii.crc_hqx(body, 0) != crc:
        raise ValueError("CRC 失败，不交付坐标")
    command, sequence, x_mm, y_mm = struct.unpack(">BBHH", body)
    if command != 1:
        raise ValueError("未知命令")
    return {"sequence": sequence, "x_m": x_mm / 1000,
            "y_m": y_mm / 1000}
