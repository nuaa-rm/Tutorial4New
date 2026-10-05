# ROS2 图像编码与 Header

面向 Ubuntu 22.04 / ROS2 Humble 的完整 ament 包；依赖 rclcpp、cv_bridge、sensor_msgs、std_msgs 和 OpenCV。两个程序均使用 Humble 的 `cv_bridge/cv_bridge.h` 头文件。

在任意新工作空间创建src，把本目录复制为src/image_bridge_demo，或使用明确的源包路径：

```bash
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-cv-bridge libopencv-dev
mkdir -p /tmp/image-bridge-ws
cd /tmp/image-bridge-ws
colcon build --base-paths /教材绝对路径/02-专项技术栈/examples/opencv/image-bridge-demo
source install/setup.bash
ros2 run image_bridge_demo roundtrip
ros2 run image_bridge_demo bridge_node
```

把`/教材绝对路径`换成自己的仓库位置；Distrobox 用户先进入已安装 Humble 的 Ubuntu 22.04 容器后加载 ROS，两个终端用同一发行版/工作空间/发现范围。roundtrip不需要相机和后台节点，输出8 8，单通道灰度76，Header时间sec=12/nanosec=345、frame_id=camera_optical_frame保持一致；秒与纳秒字段分别打印。

bridge_node每0.5秒构造红色8×8 BGR教学图，发布/image_in，自身订阅回调转换为mono8并发布/image_out。输入输出Header保持相同，回调捕获cv_bridge异常，坏图不发布。这是完整接口示例，定时生成的戳是此教学输入的生成时刻；实相机应保留真实采集头，不能在处理结束时改成now。

第二终端检查：

```bash
source /opt/ros/humble/setup.bash
source /tmp/image-bridge-ws/install/setup.bash
ros2 topic echo /image_out sensor_msgs/msg/Image --once
```

应见height=8、width=8、encoding=mono8、step=8、data为64个76，frame_id为camera_optical_frame；输出戳对应输入。可用第一章rqt ImageView或`ros2 run image_tools showimage --ros-args -r image:=/image_out`显示，需要图形会话。最后Ctrl+C停止自己启动的节点。

toCvCopy(msg,"mono8")按输入encoding转换实际像素；只把bgr8字符串改成mono8而不改图像，会制造类型/编码不符。toCvCopy复制数据，toCvShare的共享生命周期与只读边界则需另查接口；不能通过通道数猜BGR/RGB。参考[cv_bridge](https://github.com/ros-perception/vision_opencv/tree/humble/cv_bridge)。
