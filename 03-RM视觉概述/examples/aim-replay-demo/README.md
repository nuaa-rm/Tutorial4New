# 看中间量，而不是只看最后抖没抖

仅用Python3.10以上标准库。在卷三目录：

```bash
cd examples/aim-replay-demo
python3 replay.py
python3 replay.py --state-at control
python3 replay.py --delay-ms 25 --flight-ms 60
python3 replay.py --pixel-threshold 150
```

默认：采样10ms，控制45ms，命中110ms；采样状态预测100ms，x_hit=4.2m。
状态改为control后，状态先从4m移到4.07m，只需预测65ms，同样4.2m；
wrong_repeat_delay_x_m=4.27m是故意计算的重复补偿反例，不可用作指令。
25/60变式：控制35ms、命中95ms、采样状态预测85ms。

frames.csv是人工构造的五帧数据，不是真实机器人日志，也不是各算法实际计算结果。
默认相邻变化阈值为50px/0.5m/0.5m/10deg，首个超阈值帧为120/120/121/122。
把像素阈值改为150后，该列没有超阈值，不意味着图像一定正常。
这个检查只是告诉你去哪里先看原始证据，不能证明误检、遮挡或标定等根因。
换自己的CSV时使用相同字段/单位，先确认各列对应同一目标、同一帧及时刻；
真实异步链路应保留实际时间戳，不能仅按行号认定因果关系。

匀速预测没有旋转装甲、弹道迭代、云台动态或丢失时效处理；
完整实现回卷二几何、滤波、MPC项目。本项目不连接执行器，不发射弹丸。
