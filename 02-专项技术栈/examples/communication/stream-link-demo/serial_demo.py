"""Linux 伪终端配合真实 pySerial，展示字节流读取与 CRC。"""
import os
import pty
import time
import serial
from framing import CRCParser, encode_crc

master, slave = pty.openpty()
try:
    port = os.ttyname(slave)
    with serial.Serial(port, 115200, timeout=0.1, exclusive=True) as receiver:
        bad = bytearray(encode_crc(3))
        bad[-1] ^= 1
        stream = b"noise" + bad + encode_crc(7)
        parser, values = CRCParser(), []
        for start in range(0, len(stream), 3):
            chunk = stream[start:start + 3]
            assert os.write(master, chunk) == len(chunk)
            values.extend(parser.feed(receiver.read(3)))
        deadline = time.monotonic() + 2
        while not values and time.monotonic() < deadline:
            values.extend(parser.feed(receiver.read(3)))
        assert values == [7] and parser.bad_crc == 1
        print("pySerial 伪终端有效数据:", values, "坏 CRC:", parser.bad_crc)
        os.close(master)
        master = None
        try:
            receiver.read(1)
        except serial.SerialException:
            print("伪终端对端关闭，捕获读取异常")
        else:
            raise AssertionError("本环境未报告伪终端关闭")
finally:
    if master is not None:
        os.close(master)
    os.close(slave)
