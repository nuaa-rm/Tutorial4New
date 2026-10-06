# ROS2 工程实践示例

这些小工程对应卷二第一章。命令、代码和配置以 Ubuntu 22.04 + ROS2 Humble 为主；DDS 本机通信实验使用 `ROS_LOCALHOST_ONLY=1`，Zenoh 的连接范围按 session/router 配置控制。

[rmw-config-demo](rmw-config-demo/README.md) 提供 Fast DDS / Cyclone DDS 的完整网卡 XML，以及 Zenoh 安装、JSON5、router 和跨机器连接步骤；无需编译，使用官方 talker/listener 对照。

先用 `basic-interfaces-demo` 把自定义消息、定时器和字符串收发跑通，再用 `training_tools` 练习依赖、测试、参数、Launch 与日志。前一个项目自带 README，两个包需要一起复制到新工作空间的 src 中；已有同名包时另建工作空间。

[visualization-demo](visualization-demo/README.md) 接在基础收发之后，提供共用的 10 Hz 曲线、RGB 图像、位姿、TF、Marker、ImageAnnotations 和 SceneUpdate。正文带着使用 rqt Plot/Image View、RViz2 与 Foxglove，包含安装桥接、字段换算、两点测量、时间同步、布局保存及 MCAP 录制回放；无需实际相机。

大图像链路接着使用 [image-path-demo](image-path-demo/README.md)：先用小输入确认 Fast DDS、Cyclone DDS、Zenoh 与三种组件布局，再把合成负载升到 1440×1080@250 Hz；另用借出探测区分 Fast DDS 的显式配置、普通 Image 和本地分配回退。它有独立工作空间和运行说明，合成数据测试不替代实际相机与算法验收。

`training_tools` 与正文的手动 ament 版本逐文件一致。复制到自己的 `~/ros2_ws/src/` 后，在容器内部或对应 Ubuntu 环境执行：

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

rosdep 尚未初始化时，先执行一次 `sudo rosdep init`，再用普通用户执行 `rosdep update`。已初始化就跳过 init。启动后应收到 `team ready`，一次性观测进程退出，heartbeat 持续运行；按 Ctrl+C 停止。`watch:=false` 关闭观测进程。

Launch 部分沿用同一个 `training_tools` 包，新增文件时重新构建并加载环境即可，CMake 会安装整个 `launch/` 与 `config/` 目录。下面的实验分别运行，结束一轮先按 Ctrl+C，再开始下一轮；查询命令放在加载相同环境的另一终端执行。

| 启动文件 | 演示什么 | 应观察到什么 |
| --- | --- | --- |
| `basic.launch.py` | 单节点、程序名与节点名 | `/heartbeat` 在 `/status` 发布 `ready`。 |
| `heartbeat.launch.py` | 启动参数、YAML、类型、命名空间、重映射 | `robot:=blue text:=true` 在 `/blue/health` 发布字符串 `true`。默认启动的 text 字典会覆盖 YAML。 |
| `team.launch.py` | Include、If/Unless 条件、环境、一次性观测与退出事件 | 默认收到一条 `team ready` 后观测退出，心跳持续运行；`watch:=false` 打印关闭观测的提示。 |
| `multi.launch.py` | 分组作用域与相对命名空间 | `/red/sensors/health` 与 `/blue/sensors/health` 分别收到 `red ready`、`blue ready`。 |
| `checked.launch.py` | OpaqueFunction 在执行阶段取值并检查文件 | 默认打印配置路径并发布 `checked ready`；不存在的文件在启动节点前报错。 |

例如，在工作空间根目录、已构建并加载环境后执行：

```bash
ros2 launch training_tools heartbeat.launch.py --show-args
ros2 launch training_tools heartbeat.launch.py robot:=blue text:=true
# 查询终端
ros2 param get /blue/heartbeat text
ros2 topic echo /blue/health std_msgs/msg/String --once
```

第二轮结束后可以试 `ros2 launch training_tools multi.launch.py`，分别查询上表中的两条话题。`ros2 launch training_tools checked.launch.py params_file:=/tmp/no-such-params.yaml` 是故意失败的例子：先确认该文件不存在，启动应报参数文件不存在，且不启动 heartbeat。普通心跳启动文件也支持 `params_file:=/实际路径/参数.yaml`；checked 会先检查这一路径，文件存在不代表 YAML 内容或设备状态已经通过检查。

`team.launch.py` 有意把观测话题固定为 `/red/health`，用来练习把名字接到参数上；改变 robot 后同步话题的写法见对应随堂练习的卷末题解。分组里的绝对话题名不会跟随外层命名空间；进程启动、退出或固定延时也不等于模块就绪。heartbeat 在构造时读取 text 并捕获值，改变文本实验需重启节点。`test_interval` 是独立边界测试，未接入 heartbeat 的固定周期。

如果要试自动宏，把 `cmake/Auto.cmake` 复制为包根目录的 `CMakeLists.txt`，同时把清单的 buildtool_depend 改成 ament_cmake_auto，export 中仍保留 ament_cmake。然后重新运行 rosdep，并用 `colcon build --packages-select training_tools --cmake-clean-cache` 构建；两套构建规则二选一。

如果 CLion 的源码能编译，但跳转后的外部库头文件出现找不到子头文件的错误，先比较实际解析参数。正文的“源码不红，库头文件却红怎么办”给出完整操作，`header_flags.py` 是此例的辅助文件：只读选定源码的数据库条目，把 include 路径、宏和语言标准输出为仅匹配指定头文件的 clangd 配置片段，不执行数据库命令，也不修改数据库或个人配置。

在工作空间根目录执行，例如：

```bash
python3 /实际教材路径/02-专项技术栈/examples/ros2/header_flags.py \
  build/training_tools/compile_commands.json \
  src/training_tools/src/heartbeat.cpp \
  /opt/ros/humble/include/rclcpp/rclcpp/rclcpp.hpp \
  > /tmp/ros-header-flags.json
cat /tmp/ros-header-flags.json
```

仅需 Python 3 标准库和已生成的数据库。选择的源码必须唯一对应一条命令；多个配置的条目须先选择正确的数据库。本例处理 GCC/Clang 的 `-I`、`-isystem`、`-iquote`、`-D`、`-U` 和 `-std=`，相对 include 路径以数据库的 directory 为基准。包装编译器、响应文件或其他工具链选项需另行展开核对，不把这个小例子当作任意工程的通用转换器。更多需要同一解析上下文的头文件可作为额外参数，但不同上下文应分别生成。输出中应含当前 ROS 的实际 include 路径和宏；不存在的源码参数应退出，标准输出为空。

核对片段后，按正文的方法备份已有用户配置并追加。库头文件位于工程之外，所以工作空间的 `.clangd` 不会作用于它。IDE 与安装片段的终端须使用相同的 XDG_CONFIG_HOME。保留诊断，比较启用、停用和恢复片段后的解析参数与错误信息。已生成的配置依赖当前数据库，更新依赖或发行版后需要重新核对。

自动核验入口为仓库根目录的 `scripts/verify_ros_examples.py --output /tmp/ros-runtime.json`，在加载 Humble 的终端运行。它检查基础包、字段与周期变体、QoS、域隔离、Cyclone DDS、服务、ament、测试、Launch、日志和 Debug 产物。GUI 和第二台物理机器的通信另按正文验收；修订检查见 `../../../docs/revision/volume-2-humble-20261003.md`。
