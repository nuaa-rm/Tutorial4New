# 前端图像与时刻检查

从本目录执行，Python3.10+，NumPy与OpenCV；Ubuntu可安装python3-numpy/python3-opencv。三个程序分别生成可重复的教学图、记录本地图像事实、检查逐帧时刻。没有相机、厂商SDK或执行器依赖。

```bash
python3 make_frames.py --output out
python3 check_image.py out/global_short.png > out/image-record.json
python3 timing.py times.csv > out/time-record.json
```

三个64×160的8位灰度图都表示8像素宽竖条以4像素/ms移动。global_short曝光区间1ms、全行同时；rolling_short保持1ms，全行起始时刻跨度8ms，竖条倾斜；global_long保持全行同时、改6ms，竖条变宽模糊。32个时间样本取平均并固定图像亮度尺度，这只演示运动与时序，不模拟真实光子计数、增益、读出电路或相机全部噪声。不能用这些图证明某型号的性能。

check_image.py仅接受8位灰度或3通道BGR，输出路径/SHA/尺寸/通道。near_max_fraction是至少一个通道≥250的像素比例，只是排查线索，白色背景也可能达到该值，不能直接等同传感器过曝；相机身份、曝光和采样时钟没有来源时输出null。真实RAW、Bayer、16位、RGBA须先按对应格式解释，本例会拒绝。

times.csv是人工demo_clock下的帧号与时刻。采样每10ms一次，对应观察到100fps；结果延迟35ms，执行端到端延迟45ms。它们是教学算例，不是电脑或机器人测速。采样时刻须递增，帧身份不重复，时钟一致，采样≤结果≤执行；只有接收时刻的数据不能填成采样时刻。缺文件、列或时钟记录请保留原始证据，勿补猜数字。

把JSON和图像原件一起保存，再写观察区域、倾斜/拖影候选原因、未知设备元数据、下一步核对来源。不要只保存已压缩的聊天截图。真实设备的序列号、曝光/增益/触发读取、配置备份恢复、目标速度/光照对照与采样到执行测量仍须实机完成。SDK细节复用卷二相机章，不在本例另写通用设备适配器。
