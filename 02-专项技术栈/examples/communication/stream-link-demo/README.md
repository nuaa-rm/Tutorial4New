# 字节流、最新值与连接代次

这是卷二第二章的精简教学工程。长度前缀与 AA/数据/CRC 都是教学帧，不能发送给真实裁判系统或板端设备。

依赖 Python 3.10 及以上。TCP、解析、状态实验只用标准库；Linux 伪终端实验另需 pySerial。Ubuntu 可安装 `sudo apt install python3-serial`；在 Distrobox ubuntu2404 内运行时先 `distrobox enter ubuntu2404`。没有依赖 ROS 的 API，因此 Jazzy/Humble 不影响这些脚本。

从本目录运行：

```bash
python3 ping_demo.py
python3 parser_demo.py
python3 latest_demo.py
python3 event_demo.py
python3 fault_demo.py
python3 serial_demo.py
python3 bridge_demo.py
```

首先应打印ping，再得到 `[b'AB', b'XYZ']`、有效 CRC 数据 `[7]`；最新位置30优先于状态，迟到代次1清理不影响新代次2发送ok和位置42；A在模拟第2–4秒暂停，B仍输出100–105，A的旧值过期丢弃1次并在第5秒恢复15；pySerial收到7、拒收坏CRC并捕获伪终端关闭。

event_demo明确拒绝满队列中的第三事件；第1事件确认丢失后重发但只执行一次，第2事件也只执行一次。它只模拟本次两个有限事件的确认/去重，没有进程重启后的持久化承诺。bridge_demo输出 `(8, 1.25)`，载荷用大端两个uint16约定序号和毫米。

ROS变体需已安装并加载的rclpy和std_msgs。在Ubuntu容器两个终端都先加载同一发行版（Humble改脚本名）。终端一：

```bash
source /opt/ros/jazzy/setup.bash
python3 bridge_demo.py --ros
```

终端二：

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic echo /range_m std_msgs/msg/Float64 --once
```

应收到data: 1.25，Ctrl+C结束。使用相同域与发现范围；Float64本身不记录单位、源序号、采集时间或坐标系，真实接口要另行约定。这里每0.5秒重复固定样本用于观察，不是实物传感器读数。

TCP 使用两个终端，从相同目录执行。终端一：

```bash
python3 tcp_demo.py server --port 8765 --rounds 2
```

终端二，先等终端一输出“监听”，再逐次运行：

```bash
python3 tcp_demo.py client --port 8765
python3 tcp_demo.py client --port 8765
```

每次得到两帧回显；服务端输出代次1/2、断开与迟到清理的False，第二次仍回显。它在两次连接后正常退出，监听等候最多15秒，接收最多3秒；及时运行客户端。端口占用时同时替换两端端口。默认只监听127.0.0.1；两台教学机测试时，两端都加 `--host 服务端在实验网络中的IP`。服务端绑定的是自己的地址，客户端连接的是服务端地址。提前确认防火墙、可达性与访问范围；示例没有鉴权，不在公网使用，跨主机结果需在实际设备另测。

`framing.py` 保留不完整帧，不猜测TCP分片；非法长度清空缓存并由服务端结束该连接。CRC失败从下一字节搜索AA。正常调用每次输入固定小块，长度解析残留最多16字节、CRC解析残留最多3字节；不能把无限外部数据一次性喂入缓存。

`state.py` 只有position/status两个状态槽，覆盖旧值，按固定优先级消费；connect清空旧槽，put/take/disconnect在锁中核对代次。关闭句柄使用刚取出的旧对象，不能在锁外再读取“当前连接”去关闭。实际异步I/O持有本轮连接和本轮解析器，关闭/写入结果仍需核对归属。本例没有可靠事件通道、自动退避重连或生产级网络服务。

`serial_demo.py` 使用Linux PTY和真实pySerial接口；它验证读取分片、解析和异常路径，不验证电气连接、USB拔插、真实波特率或板端协议。物理设备路径、8N1及电平检查沿用卷一；项目不会打开用户的硬件串口。

练习在副本中修改：拆成单字节输入、损坏载荷、改优先级、改变过期阈值、记录迟到清理。答案和结果判断见本卷题解。自测输入只能代表本章指定行为，不能据此声称赛场通信或所有故障已验证。
