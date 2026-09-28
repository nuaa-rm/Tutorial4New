# 标定验证示例

`check_holdout.py` 与相机章“检查独立照片并生成去畸变图”逐行一致。

1. 在带 NumPy 和 OpenCV 的 Python 环境中，先运行教材原有离线棋盘格标定示例，得到 `calibration.npz`。
2. 使用 9×6 内角点、方格边长 0.025 m 的同一标定板。提供一张未参与标定的同分辨率照片，保存为 `validation.png`。
3. 在这两个输入文件所在目录执行 `python /实际路径/check_holdout.py`。

输出为验证 RMS、最大角点残差、`undistorted.png` 和 `rectified_model.npz`。后者保存校正图的新内参；图像未裁剪 ROI。验证照片的板位姿仍由这张照片估计，误差不能视作独立真值精度。

ROS2 实时标定、保存 YAML、驱动加载和 image_proc 校正流程见教材 `E_calibration.tex`。脚本已做语法检查；当前编辑主机没有 OpenCV、ROS2 或实际相机，真实数据实验需在目标环境执行。
