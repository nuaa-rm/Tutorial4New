# 接口卡为什么要写清楚

这个项目只演示接收端怎样解释一条教学消息，不连接 ROS、串口或云台。
需要 Python 3.10 及以上，仅用标准库；Ubuntu 24.04 的 Python 3.12 可以直接运行。

从卷三目录进入：

```bash
cd examples/interface-card-demo
python3 receiver.py
python3 receiver.py --unit deg
python3 receiver.py --age-ms 101
python3 receiver.py --invalid
python3 receiver.py --delta -0.1
```

默认是相对当前云台的水平增量，左转为正，单位 rad。
发送方与接收方使用同一教学时钟：采样20ms，接收100ms，年龄80ms。
默认打印 accept、80ms 和约5.7296度。unit改为deg会打印hold/unit mismatch；
101ms超过含边界100ms的阈值，会打印hold/time invalid；
无效观测同样hold；负增量显示约−5.7296度。
frame、version和clock必须一致；未来时间、非有限数也不接收。

card.json的contract是双方约定，message是一次观测。
receiver.py先核对含义，再判断数值/时效/有效性，最后解释角度。
hold表示本程序不给出新的目标增量，并不证明实车已经停转。
真实接收端还需处理丢包、解析异常、序号、限幅、看门狗和协议校验，
具体字段及失效动作必须由视觉与电控共同确认。这张卡不是裁判协议。
