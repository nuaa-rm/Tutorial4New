# 从 IQ 录包到教学坐标帧

先合成一帧 BPSK，保存并重新读取 IQ，补偿已知频偏，用前导相关估计整样本起点和恒定相位，再按符号求均值、判决、组帧和 CRC。它演示的是单帧离线接收链，不是赛场解码器：频偏和每符号采样数已知，使用矩形脉冲、固定帧长、整数采样偏移，没有采样时钟漂移、多径、自动增益或连续流丢样恢复。

在第二卷 `examples/sdr/iq-replay-demo` 目录执行。离线依赖 Python 3.10+、NumPy（Ubuntu 24.04 验证为 Python 3.12 / NumPy 1.26.4）。在 Distrobox 中先 `distrobox enter ubuntu2404`；本章不需要加载 ROS。

```bash
sudo apt install python3-numpy
python3 tone_demo.py
python3 replay.py generate /tmp/sdr-good
python3 replay.py decode /tmp/sdr-good
python3 replay.py generate /tmp/sdr-bad --corrupt
python3 replay.py decode /tmp/sdr-bad
python3 state_demo.py
```

正、负 1000 Hz 的相位差为 ±0.785398 rad，幅值均为 1；9000 Hz 与 1000 Hz 离散样本相同。正常录包为 670 个复数样本；同步起点 19，帧十六进制 `010704e209c40584`，有效字段为序号 7、x_m=1.25、y_m=2.5。坏录包改变坐标字节却保留旧 CRC，解码以 ValueError 退出，不能交付坐标。

`generate folder [--x-mm N] [--phase RAD] [--offset-hz HZ] [--noise SCALE] [--corrupt]` 的选项只影响生成；`decode folder` 完全读取文件。生成会覆盖该目录的两个文件，换参数时推荐用新目录。`--noise` 是 I/Q 两路独立高斯噪声的标准差，不是以 dB 表示的信噪比。x_mm 是 uint16（0–65535），命令为 1、序号为 7、y_mm 为 2500；这些都是教学约定。

`iq.npy` 自带形状、dtype 与字节序头，不是裸二进制数组；`metadata.json` 保存采样率、每符号采样数、已知频偏、样本数、dtype（本机 `<c8`：小端 complex64）和文件 SHA-256。修改文件后哈希不符会报错。两文件一同变化时哈希不能证明真实性，也不能检测“采样率写错但文件未变”的情况。载入禁用 pickle，仅允许一维有限复数样本。

`state_demo.py` 的 profile 只包含模拟采样率和带宽。事件 ok2 在 level1 无效，ok1→level2，timeout 保持 level2，ok2→information，reset→level1；代次为 0、1、1、2、3。实机切换还要串行更改本振/滤波器、丢弃旧缓冲、等待稳定，用代次拒绝迟到结果。模拟只打印状态，不会替你完成这些硬件操作。源选择按 radio、vision 顺序检查同一逻辑时钟下 0–0.2 s 的年龄：10.0 s 选择 vision，11.0 s 为 None。

## 可选 Pluto 接收

只在设备已获准接入、接收中心频率已由实验负责人指定时运行；代码没有 tx 调用。Ubuntu 24.04 的依赖安装与 import 已核验如下，真实设备尚未验收。其他版本按 ADI 文档确认 libiio 与绑定兼容性。

```bash
sudo apt install libiio0 libiio-utils libad9361-0 python3-venv
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install pyadi-iio==0.0.21 pylibiio==0.25
.venv/bin/python -c 'import adi, iio; print(adi.__version__, iio.version)'
iio_info -S usb
.venv/bin/python capture_pluto.py --help
```

预期 import 显示 0.0.21 和 libiio 0.25。这里按安装版本的帮助用 `-S usb` 只扫描 USB；旧文档可能写 `-s`，先运行 `iio_info --help` 看本机参数。扫描全部后端时，容器缺 Avahi 可能报告 DNS-SD/扫描错误，这不等于 Python 包没装，也不能据此判断设备一定损坏。先检查 USB 是否暴露给容器，按部署文档从设备网络接口确定 IP，必要时 `iio_info -u ip:设备地址` 定向检查。不要为一次扫描随意改宿主机服务。

确认设备地址与接收频率后，调用 `capture_pluto.py --uri URI --lo-hz HZ folder`，将 URI/HZ/folder 换成自己的值。设备不可达、驱动不兼容或读取失败会报错；先按异常定位，不将空样本当成功。输出应有 4096 个样本及实际 dtype/本振读回；保存时转为 complex64。真实样本缺少教学前导、频偏与符号率约定，不能直接调用教学 decode；它们的解码器要按实际波形设计。

记录接收配置、增益模式、设备、天线与采集时间，有助于区别录包时间和样本时间。缓冲调用不是持续无丢样保证；高采样率、总线吞吐、容器设备权限和调谐稳定都需要实机检查。任何发射实验要另行确认频谱法规、赛场规则和场地许可，不能照搬网上的 tx 示例。

接口参考：[NumPy 存储与载入](https://numpy.org/doc/stable/reference/generated/numpy.load.html)、[NumPy 卷积](https://numpy.org/doc/stable/reference/generated/numpy.convolve.html)、[ADI pyadi-iio 环境](https://analogdevicesinc.github.io/pyadi-iio/guides/quick.html)、[ADI Pluto 接口](https://github.com/analogdevicesinc/pyadi-iio/blob/main/adi/ad936x.py)。
