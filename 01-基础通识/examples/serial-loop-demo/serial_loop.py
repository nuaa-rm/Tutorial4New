import serial

with serial.serial_for_url(
    "loop://", baudrate=115200, bytesize=8, parity="N",
    stopbits=1, timeout=1, write_timeout=1,
    xonxoff=False, rtscts=False, dsrdtr=False
) as port:
    payload = b"hello\n"
    port.write(payload)
    received = port.read(len(payload))
    print("RX:", repr(received))
    print("HEX:", received.hex(" "))
    assert received == payload
    # 没有后续数据时，有限超时让读取返回空字节串。
    print("EMPTY:", repr(port.read(1)))
