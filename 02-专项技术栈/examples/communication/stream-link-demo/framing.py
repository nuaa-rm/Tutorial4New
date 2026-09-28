"""两种教学帧；与裁判系统、无线电的真实帧定义无关。"""
import binascii


def encode_length(payload):
    if not 1 <= len(payload) <= 16:
        raise ValueError("载荷长度必须在 1 到 16 之间")
    return bytes([len(payload)]) + payload


class LengthParser:
    def __init__(self):
        self.buffer = bytearray()

    def feed(self, chunk):
        self.buffer.extend(chunk)
        frames = []
        while self.buffer:
            size = self.buffer[0]
            if not 1 <= size <= 16:
                self.buffer.clear()
                raise ValueError("非法长度：结束本次连接，不能猜测下一帧")
            if len(self.buffer) < size + 1:
                break
            frames.append(bytes(self.buffer[1:size + 1]))
            del self.buffer[:size + 1]
        return frames


def encode_crc(value):
    payload = bytes([value])
    crc = binascii.crc_hqx(payload, 0)
    return b"\xaa" + payload + crc.to_bytes(2, "big")


class CRCParser:
    def __init__(self):
        self.buffer = bytearray()
        self.bad_crc = 0
        self.noise = 0

    def feed(self, chunk):
        self.buffer.extend(chunk)
        values = []
        while self.buffer:
            if self.buffer[0] != 0xaa:
                del self.buffer[0]
                self.noise += 1
                continue
            if len(self.buffer) < 4:
                break
            crc = binascii.crc_hqx(bytes(self.buffer[1:2]), 0)
            if crc != int.from_bytes(self.buffer[2:4], "big"):
                self.bad_crc += 1
                del self.buffer[0]
                continue
            values.append(self.buffer[1])
            del self.buffer[:4]
        return values
