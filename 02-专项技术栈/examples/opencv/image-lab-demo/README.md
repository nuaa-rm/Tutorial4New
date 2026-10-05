# OpenCV 图像实验

每个 `_demo` 是一个独立程序，便于一次只改一个概念；CMake 共用配置，不要求把十几个 main.cpp 互相覆盖。最后用 sample→pipeline 串起颜色、形态学、轮廓与绘图。仅需要 C++17、CMake 和 OpenCV 4.x；本章使用 Ubuntu 22.04 的 libopencv-dev，先用 version_demo 核对实际版本；ROS 图像接口在旁边独立包，不混进普通图像目标。

进入本卷 `examples/opencv/image-lab-demo`（Distrobox 用户先 `distrobox enter ubuntu2404`），执行：

```bash
sudo apt install libopencv-dev
cmake -S . -B build
cmake --build build --parallel 2
./build/version_demo
./build/mat_demo
./build/io_demo
./build/hsv_demo
./build/threshold_demo
./build/filter_demo
./build/morphology_demo
./build/contour_demo
./build/resize_demo
./build/features_demo
./build/sample_demo
./build/pipeline_demo scene.png
./build/viewer_demo annotated.png
./build/video_demo scene.avi
```

生成的图片/视频写入运行时当前目录；这里是项目目录。它们会覆盖同名生成文件，自己的实验数据另存目录。普通程序不需要加载 ROS 环境。没有图形会话时，数值和文件处理目标仍可运行；viewer/video 需要可用的显示后端，不能把缺 DISPLAY 当作算法失败。

预期结果：版本为本机 OpenCV；mat 为 `9 1`；io 为 `32 48`；hsv 为 `2`；threshold 首行为 `0 0 255`，Otsu 双峰样本为阈值50/400前景；filter 首行0，均值/高斯/双边中心为28/64/255；morphology 为`26 25`；contour 为`1 171 200`；resize 为`40 20`；features 为匹配数量，全部距离为0（数量随版本变化）。程序成功返回0，io写图失败1/读图失败2，viewer无参数1/读图失败2/保存失败3。

sample 生成 160×120 的 scene.png 和20帧MJPG scene.avi：两个红色块分别从 HSV 色环两端生成、一个小孔、一个孤立红点和一个蓝圆。pipeline 保存 mask/opened/closed/edges/annotated 五个中间结果，固定教学面积阈值100、长宽比下限1.5。正常像素数3600→3599→3600，两个外轮廓/保留2个，每个连续面积1711、长宽比约2.03448。它从实心掩膜提轮廓；Canny边缘只用于对照，不把空心边缘当作同一掩膜。每个保留矩形输出连续面积与长宽比，数值以实际运行记录为准。真实图像需重调阈值，不是装甲板识别器。

viewer 通用形式 `viewer_demo image_path`，按 s 保存 saved.png，其余按键退出。video 为 `video_demo video_path` 或 `video_demo --camera ID`；默认不打开硬件，ID用数字设备编号。文件结束或Esc退出，waitKey(30)用于处理窗口事件/等待，不能当作精确视频时钟。VideoCapture成功打开和cap.set返回值都不能证明实际分辨率/帧率已生效；实机需读回属性和图像形状检查。本环境没有摄像头，物理相机未验证。

处理练习时修改对应 src 文件，再执行 `cmake --build build --target NAME_demo`。当练习更改目标名称，也须同步 CMake 创建、属性和链接的目标。缩放后绘图坐标属于新图；旋转输出尺寸不变，边缘可能被裁掉。ORB使用默认WTA_K=2的二进制描述子和Hamming距离，纹理相同不保证几何关系，需进一步校验。
