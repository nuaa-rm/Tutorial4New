# 串口字节与读取超时

依赖 Python 3 和 pySerial。Ubuntu 可用 `sudo apt install python3-serial` 安装；使用 `/usr/bin/python3`，避免 Conda 的 Python 读不到系统包。

从本目录运行：

```bash
/usr/bin/python3 serial_loop.py
```

依次输出 `RX: b'hello\n'`、`HEX: 68 65 6c 6c 6f 0a`，等待约一秒后输出 `EMPTY: b''`。软件回环不检查真实 USB 驱动、设备权限、接线或板端协议。

将 payload 改为 `bytes([0x00, 0x41, 0xFF, 0x0A])` 后，HEX 应为 `00 41 ff 0a`。修改后运行一次，再恢复原文件。
