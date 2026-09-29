# ROS2 工程实践示例

这两个小工程对应卷二第一章。命令以 Ubuntu 24.04 + ROS2 Jazzy 为主；Humble 22.04 把包名和环境路径中的 jazzy 换成 humble，发现范围配置按正文分别设置。本次运行验证使用 Distrobox `ubuntu2404` 中的 Jazzy，未把结果外推为 Humble 实测。

先用 `basic-interfaces-demo` 把自定义消息、定时器和字符串收发跑通，再用 `training_tools` 练习依赖、测试、参数、Launch 与日志。前一个项目自带 README，两个包需要一起复制到新工作空间的 src 中；已有同名包时另建工作空间。

`training_tools` 与正文的手动 ament 版本逐文件一致。复制到自己的 `~/ros2_ws/src/` 后，在容器内部或对应 Ubuntu 环境执行：

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select training_tools --cmake-args -DBUILD_TESTING=ON
source install/setup.bash
colcon test --packages-select training_tools
colcon test-result --verbose
ros2 launch training_tools team.launch.py
```

rosdep 尚未初始化时，先执行一次 `sudo rosdep init`，再用普通用户执行 `rosdep update`。已初始化就跳过 init。启动后应收到 `team ready`，一次性观测进程退出，heartbeat 持续运行；按 Ctrl+C 停止。`watch:=false` 关闭观测进程。

`team.launch.py` 有意把观测话题固定为 `/red/health`，用来练习把名字接到参数上；改变 robot 后同步话题的写法见对应随堂练习的卷末题解。heartbeat 在构造时读取 text 并捕获值，改变文本实验需重启节点。`test_interval` 是独立边界测试，未接入 heartbeat 的固定周期。

如果要试自动宏，把 `cmake/Auto.cmake` 复制为包根目录的 `CMakeLists.txt`，同时把清单的 buildtool_depend 改成 ament_cmake_auto，export 中仍保留 ament_cmake。然后重新运行 rosdep，并用 `colcon build --packages-select training_tools --cmake-clean-cache` 构建；两套构建规则二选一。

如果 CLion 的源码能编译，但跳转后的外部库头文件出现找不到子头文件的错误，先比较实际解析参数。正文的“源码不红，库头文件却红怎么办”给出完整操作，`header_flags.py` 是此例的辅助文件：只读选定源码的数据库条目，把 include 路径、宏和语言标准输出为仅匹配指定头文件的 clangd 配置片段，不执行数据库命令，也不修改数据库或个人配置。

在工作空间根目录执行，例如：

```bash
python3 /实际教材路径/02-专项技术栈/examples/ros2/header_flags.py \
  build/training_tools/compile_commands.json \
  src/training_tools/src/heartbeat.cpp \
  /opt/ros/jazzy/include/rclcpp/rclcpp/rclcpp.hpp \
  > /tmp/ros-header-flags.json
cat /tmp/ros-header-flags.json
```

仅需 Python 3 标准库和已生成的数据库。选择的源码必须唯一对应一条命令；多个配置的条目须先选择正确的数据库。本例处理 GCC/Clang 的 `-I`、`-isystem`、`-iquote`、`-D`、`-U` 和 `-std=`，相对 include 路径以数据库的 directory 为基准。包装编译器、响应文件或其他工具链选项需另行展开核对，不把这个小例子当作任意工程的通用转换器。更多需要同一解析上下文的头文件可作为额外参数，但不同上下文应分别生成。输出中应含当前 ROS 的实际 include 路径和宏；不存在的源码参数应退出，标准输出为空。

核对片段后，按正文的方法备份已有用户配置并追加。库头文件位于工程之外，所以工作空间的 `.clangd` 不会作用于它。IDE 与安装片段的终端须使用相同的 XDG_CONFIG_HOME。本次在隔离配置中确认 rclcpp.hpp 的 15 条错误消失，停用/恢复片段分别为 15/0；诊断未关闭。已生成的配置依赖当前数据库，更新依赖或发行版后需要重新核对。

运行核验覆盖两个基础包、字段与周期变体、三种 QoS 组合、域隔离、Cyclone DDS、服务、手动/自动 ament、边界测试、Launch 参数和条件事件、日志、独立 Debug 构建与安装版本差异。真实 rqt 插件已在独立 Xvfb 显示中验证收发、节点停止和恢复；GDB 和 CLion GUI 均已命中实际发布回调。CLion 实际构建、参数覆盖、默认值修改与安装产物对照、编译数据库导入、源码编译和头文件参数补充已完成；第二台物理机器上的发现范围仍未完成验证，详见 `../../../docs/revision/volume-2-chapter-1.md`。
