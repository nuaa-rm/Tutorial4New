"""固定输入可以稳定复现拆帧，不依赖 TCP 本次如何分片。"""
import binascii
from framing import LengthParser, CRCParser, encode_crc

parser = LengthParser()
frames = []
for chunk in [b"\x02A", b"B\x03X", b"YZ"]:
    frames.extend(parser.feed(chunk))
assert frames == [b"AB", b"XYZ"]
assert not parser.buffer
print("完整载荷:", frames)

bad = bytearray(encode_crc(3))
bad[-1] ^= 1
stream = b"noise" + bad + encode_crc(7)
parser = CRCParser()
values = []
for start in range(0, len(stream), 2):
    values.extend(parser.feed(stream[start:start + 2]))
assert binascii.crc_hqx(b"123456789", 0) == 0x31c3
assert values == [7] and parser.bad_crc == 1
print("有效数据:", values, "坏 CRC:", parser.bad_crc)
