# 雷达站平面映射与选源演示

这里用人工坐标观察地面映射和失效回退，不接相机、SDR、裁判串口，也不代表赛季规则允许某种可选功能。质量标志由上游给出，本项目不会替你检查真实识别质量或射频校验。选源是教学优先级，并非统计加权融合。

从本目录执行，Python 3.10+；choose.py只用标准库。plane.py需要NumPy、OpenCV，Ubuntu可用 `sudo apt install python3-numpy python3-opencv`。本书实测环境是Distrobox ubuntu2404 / Python 3.12 / OpenCV 4.6。

```bash
python3 plane.py --height 0
python3 plane.py --height 1
python3 choose.py
python3 choose.py --radio-age 50 --vision-age 40
python3 choose.py --radio-age 120 --vision-age 40
python3 choose.py --radio-age 50 --vision-age 40 --radio-invalid
python3 choose.py --radio-age 120 --vision-age 160
python3 choose.py --radio-age 100
python3 choose.py --radio-age 50 --radio-frame camera
```

高度0时，未参与拟合的(3,2)m地面点映射误差为0；高度1时同一竖线上像素(470,165)被地面单应映射到(3.25,2.125)m，偏差约0.280m。相机是固定理想模型，无畸变；这些值不是现场标定精度。height必须有限且0≤height<5m。

默认无线电/视觉年龄150/50ms，选择vision。随后四个情景依次输出radio、vision、vision、无效；无线电年龄恰100ms仍在边界内；坐标系camera的无线电不合格，即使只有50ms也回退vision。checks给出每源被拒绝的原因，失效输出valid=false、source=null、xy_m=null。

sources.json的target/frame/unit/clock是公共约定，now_ms和采样时刻都来自人工demo_clock。limits_ms的100/150ms是教学值。真实机器须统一时间与坐标，再按运动、链路与规则验证阈值。收到旧消息不会更新采样时刻；断开的源须显式失效或到时过期。程序假定配置可信，校验收到的两条消息。

容量与协议工程复用卷二examples/communication/stream-link-demo；这里不再写一套TCP、串口或射频接收器。真实高台相机、地形高度、帧率与裁判发送限制仍需设备和适用版本资料验证。
