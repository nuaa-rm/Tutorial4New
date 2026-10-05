# 发布、订阅、定时器与自定义接口

配合卷二第一章“使用 RCLCPP 接口”与“把节点与接口拼成完整工程”。my_msgs 定义带时间戳、装甲板编号、yaw（弧度）及检测状态的消息；my_package 的节点订阅 receive，回复 send，每秒发布 timer_ 和 my_msg。它还订阅自己的 my_msg，方便对照接口与实际消息。

依赖 ROS2 的 ament_cmake、rclcpp、std_msgs、rosidl_default_generators，及 colcon。使用 Ubuntu 22.04 + ROS2 Humble。

将 my_msgs、my_package 复制到自己的独立工作空间 src 下，避免覆盖同名包。以下命令在工作空间根目录运行：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-up-to my_package
source install/setup.bash
ros2 interface show my_msgs/msg/My
ros2 run my_package my_node
```

接口应包含 header、id、yaw、detect_success；节点每秒记录 timer count，收到自己的消息后记录 id=1、yaw=0.25、detect_success=1。不要用回调计数冒充经过的秒数。

另一终端加载同一系统与工作空间环境后执行：

```bash
ros2 topic echo /my_msg --once
ros2 topic echo /timer_ --once
ros2 topic echo /send
```

再开一终端同样加载环境并发布：

```bash
ros2 topic pub --once /receive std_msgs/msg/String '{data: hello}'
```

send 应收到 `I can hear:hello`。各进程按 Ctrl+C 停止。修改消息字段后重新构建消息包；要在节点中访问新字段，还需重建依赖它的节点包。将定时器改为500毫秒并重建、重启后，频率约2 Hz，计数增加一仍表示一次回调。
