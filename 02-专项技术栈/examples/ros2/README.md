# ROS2 工程实践示例

对应卷二第一章“构建、启动与排障”，适用 Ubuntu 22.04 + ROS2 Humble。`training_tools` 与教材中手动 ament 版本逐文件一致，包含完整的节点、清单、构建规则、测试、参数文件及两份 Launch。

将 `training_tools` 目录复制到自己的 `~/ros2_ws/src/` 下，然后执行：

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select training_tools --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
colcon test --packages-select training_tools
colcon test-result --verbose
ros2 launch training_tools team.launch.py
```

rosdep 需先按 ROS2 安装教程初始化。预期 heartbeat 发布 `team ready`，一次性观测进程收到消息后退出，heartbeat 持续运行。按 Ctrl+C 停止。`watch:=false` 关闭观测进程。

`team.launch.py` 的观测话题有意保持为 `/red/health`，与教材随堂练习一致；变更 robot 参数后如何同步话题，见卷末随堂练习 1.8 的完整题解。heartbeat 的 text 参数仅在启动时读取，修改参数实验需重启节点。`test_interval` 是独立边界测试教学示例，未连接到 heartbeat 的固定周期逻辑。

这些文件已检查 Python 语法、XML/YAML 解析及与教材的一致性。当前编辑主机未安装 ROS2，C++ 编译、DDS 通信、Launch 行为与 CLion 断点仍需在上述目标环境验收。
