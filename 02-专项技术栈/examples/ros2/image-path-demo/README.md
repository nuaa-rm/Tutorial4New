# 大图像、中间件与组件布局实验

对应卷二 ROS2 章“大图像链路：中间件与内存”。环境为 Ubuntu 22.04 + ROS2 Humble。支持 Fast DDS、Cyclone DDS 和 Zenoh 三种 RMW，使用相同节点与 QoS 比较进程布局；另探测固定消息类型与 Image 的发布端借出能力。

默认生成 64×48、BGR8、25 Hz、100 帧，便于先检查操作。相机场景使用 1440×1080（宽×高）、目标 250 Hz：Bayer8 的紧密排列纯像素负载为 388.8 MB/s，BGR8 为 1166.4 MB/s。输入由内存生成，不连接相机、不运行 Bayer 转换或识别，不证明物理相机端到端达到 250 Hz。

在 Ubuntu/Humble 中打开 Bash，从独立的新工作空间构建。`BOOK` 改为实际教材目录；已有同名目录时另建工作空间，不覆盖自己的包。Zsh 使用对应的 setup.zsh。

```bash
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-rmw-cyclonedds-cpp \
  ros-humble-rclcpp-components ros-humble-rosidl-default-generators
BOOK="$HOME/Apps/Tutorial4New"
mkdir -p ~/image_path_ws/src
cp -r "$BOOK/02-专项技术栈/examples/ros2/image-path-demo" \
  ~/image_path_ws/src/image_path_demo
cd ~/image_path_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select image_path_demo \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
export ROS_DOMAIN_ID=87
export ROS_LOCALHOST_ONLY=1
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ros2 launch image_path_demo path.launch.py mode:=intra
```

rosdep 尚未初始化时，先执行一次 `sudo rosdep init`，普通用户执行 `rosdep update`；已初始化则跳过。先停止同域的旧实验与额外订阅者。

Source 和 Sink 共用 `Frame.msg`，其中测量序号、单调时钟与源像素地址包在正常 Image 外，保留 Image 的时间戳和坐标系。完整 Source/Sink 在 `src/components.cpp`；清单、构建规则、接口、Launch 和借出配置都在正文直接引入。

三种 mode：

| mode | 进程布局 | 进程内通信 |
|---|---|---|
| separate | 两个单线程组件容器进程 | 关闭 |
| same | 一个单线程容器、两个组件 | 关闭 |
| intra | 一个单线程容器、两个组件 | 两端开启 |

启动后前三条 `POINTER` 显示同一帧的源与接收像素地址。intra 应显示 same_process=1、对应地址一致；约四秒出现 `SOURCE_DONE 100`。按 Ctrl+C 正常退出，检查 SOURCE/SINK 汇总：默认应收到 100 帧，bad_frames=0，pointer_matches=100。像素检查只覆盖首尾字节，并非全帧哈希检查。跨进程地址不能比较；same 模式可能因分配器复用地址而出现相等，地址本身不能证明零拷贝。intra 的结论需要实际启用路径、UniquePtr 所有权条件与记录共同支持。

在相同环境、域和 RMW 的另一终端执行 `ros2 component list`，应看到 /image_box 内的两个组件。component_container 是单线程；换成 component_container_mt 时还要处理回调组与数据竞争。这个最小实验不引入并发。Distrobox 是系统运行环境；同一 Distrobox 中的不同进程仍是 separate 路径。

自动运行两种 RMW × 三种布局：

```bash
cd ~/image_path_ws
python3 src/image_path_demo/compare.py --output /tmp/image-path-small
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-bgr250 \
  --width 1440 --height 1080 --channels 3 \
  --rate 250 --frames 1000 --repeat 3
```

输出目录须尚不存在，再次运行换名字。需要 Python3 标准库、Linux /proc 和已加载的安装环境。`--channels 1` 生成 mono8，3 生成 bgr8；`--rmws`、`--modes` 可选择子集，`--domain` 更换独立域，`--depth` 改两端历史，`--reliable` 把两端改为可靠；`--work-ms` 模拟接收处理耗时。脚本只关闭自己启动的进程组，保留原始日志。查询所有选项用 `python3 src/image_path_demo/compare.py --help`。

Zenoh 是额外安装的非 DDS 中间件；保持 Ubuntu 22.04/Humble，在同一个组件工程中使用：

```bash
sudo apt update
sudo apt install ros-humble-rmw-zenoh-cpp
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-zenoh-small --rmws rmw_zenoh_cpp
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-zenoh-bgr250 --rmws rmw_zenoh_cpp \
  --width 1440 --height 1080 --channels 3 \
  --rate 250 --frames 1000 --repeat 3
```

记录器每轮启动并正常关闭自己的 Zenoh 路由器，默认只监听 127.0.0.1:17447；节点使用该端点连接，默认关闭 Zenoh SHM。每轮有额外的 `-router.log`、路由器退出状态与配置字段。端口已占用则退出，换未占用端口用 `--zenoh-port`。路由器计入 CPU/RSS，不连接或关闭已有路由器。脚本清除子进程继承的 `ZENOH_*` 与 `RMW_ZENOH_*` 调优变量，不改用户配置。

默认自动对照仍选两种 DDS；要一次比较三个实现，显式传入 `--rmws rmw_fastrtps_cpp rmw_cyclonedds_cpp rmw_zenoh_cpp`。在默认 Zenoh 大图像记录之后，只改共享内存配置，用 `--zenoh-shm` 和记录过的池容量做独立对照：

```bash
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-zenoh-shm \
  --rmws rmw_zenoh_cpp --modes separate --zenoh-shm \
  --zenoh-shm-pool-mib 6 \
  --width 1440 --height 1080 --channels 3 \
  --rate 250 --frames 1000 --repeat 3
```

这会显式为路由器与所有节点开启 `transport/shared_memory/enabled` 和 `transport/shared_memory/transport_optimization/enabled`。本轮默认 48 MiB 池超过容器 8 MiB 的 memlock 上限，出现 `Error creating lazy ShmProvider` / `OS error 12`，仍收到全部帧。这是回退记录，不能算作 SHM 验证通过。上面的新对照用 `--zenoh-shm-pool-mib 6` 设置每个会话的池；参数默认仍为 48 MiB。用 `ulimit -l`（KiB）与 `df -h /dev/shm` 同时检查。6 MiB 只足够容纳很少的 4.67 MB 在途大样本，真实部署按容量预算设置。

它优化序列化数据的传输；普通 Image 的应用对象仍有分配、填充与序列化/反序列化边界，不能据此声称相机到算法完整零拷贝。要核对 SHM 容量、锁定内存限制、版本与回退；本轮另用 20 帧低频诊断，记录 Source 创建 6291456 字节共享段、Sink 打开同一段；这支持共享池实际可用，但没有逐帧跟踪证明 250 Hz 的所有数据始终通过 SHM。诊断增加详细日志，不能混入性能表。

手动启动时使用两个加载 Humble 的终端。终端一执行 `ros2 run rmw_zenoh_cpp rmw_zenohd`；终端二加载本工程的 `install/setup.bash`、设置 `ROS_DOMAIN_ID=87`、`ROS_LOCALHOST_ONLY=1` 和 `RMW_IMPLEMENTATION=rmw_zenoh_cpp`，再运行同一条 Launch。默认路由器端口为 7447；默认节点通过它发现同机 peer，然后可直接交换数据。发布结束后先 Ctrl+C 正常关闭节点，再关闭自己的路由器。查询终端使用同一 RMW/域，可执行 `ros2 component list --no-daemon`，避免旧 RMW 的缓存。

收不到消息时检查路由器、端口、两端 RMW/域及残留配置；不要把默认配置下缺少路由器的发现问题当成“Zenoh 不支持该消息”。两端均使用 Humble，Zenoh RMW 不自动互通 DDS 或 `zenoh-bridge-ros2dds`，跨发行版与桥接须另行核对。说明见 [Humble 分支](https://github.com/ros2/rmw_zenoh/blob/humble/README.md)与 [RMW 设计](https://github.com/ros2/rmw_zenoh/blob/humble/docs/design.md)。

每轮记录：

- `results.json`：实际发送/接收频率、接收帧数/发送帧数、已收到样本的 P50/P95/P99、像素地址检查及首尾内容检查。
- 每轮 `.log`：组件加载、前三帧地址、发布完成及正常退出统计。
- `environment.json`：合成输入与计时口径。

发送前先分配与填充像素；延迟从填充完成后、publish 前开始，到订阅回调入口结束。不含曝光、SDK、图像生成或识别耗时。Linux 单机 steady_clock/CLOCK_MONOTONIC 用于计算；多机不能直接相减未同步的时钟。发送频率根据首末发送时刻计算，接收频率根据首末回调入口计算，因此二者可能有小幅差异；接收比例更直接表达有限帧数的交付情况。丢掉的帧不进入延迟统计，低 P95 不能替代高接收比例。

CPU 秒包括存活的节点进程组及本实验 Zenoh 路由器在发现、加载、运行与排空阶段的累计用量；不等于稳态 CPU 百分比。RSS 是进程值相加，会重复计算共享页。跨布局还改变了执行器数量，不能把所有差值归因于某一次 DDS 复制。测量顺序固定，可重复并改顺序再验证。

默认对照会清除子进程的 DDS XML、发布模式与借出调优变量，不改个人配置。当前目录若有隐式 `DEFAULT_FASTRTPS_PROFILES.xml` 则拒绝继续；换到干净目录。不要在实验中加入 echo、GUI 或录制订阅者，它们会改变路径和负载。

慢处理对照，在上面的环境中运行：

```bash
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-slow-5 \
  --rmws rmw_fastrtps_cpp --modes separate \
  --rate 250 --frames 500 --work-ms 8 --depth 5
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-slow-100 \
  --rmws rmw_fastrtps_cpp --modes separate \
  --rate 250 --frames 500 --work-ms 8 --depth 100
```

两轮使用小图像，排除大负载。记录发送频率、接收比例、延迟与两秒排空条件。改 `--drain-seconds` 要同时记下新条件；有限帧数最后排空不代表 8 ms 串行阶段能长期处理 250 Hz。改成同进程单线程时，耗时回调还会拖慢 Source，不能把接收比例高当成输入仍为 250 Hz。

借出探测是独立程序，前三轮分别是默认 Fast DDS、显式 Data Sharing 和 Cyclone DDS，第四轮禁用借出：

```bash
source /opt/ros/humble/setup.bash
cd ~/image_path_ws
source install/setup.bash
export ROS_DOMAIN_ID=88
export ROS_LOCALHOST_ONLY=1
unset ROS_DISABLE_LOANED_MESSAGES
unset FASTRTPS_DEFAULT_PROFILES_FILE RMW_FASTRTPS_USE_QOS_FROM_XML
RMW_IMPLEMENTATION=rmw_fastrtps_cpp ros2 run image_path_demo loan_probe
PROFILE="$(ros2 pkg prefix --share image_path_demo)/config/fastdds-loan.xml"
RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  FASTRTPS_DEFAULT_PROFILES_FILE="$PROFILE" RMW_FASTRTPS_USE_QOS_FROM_XML=1 \
  ros2 run image_path_demo loan_probe
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp ros2 run image_path_demo loan_probe
RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  FASTRTPS_DEFAULT_PROFILES_FILE="$PROFILE" RMW_FASTRTPS_USE_QOS_FROM_XML=1 \
  ROS_DISABLE_LOANED_MESSAGES=1 ros2 run image_path_demo loan_probe
```

先排除隐式 XML 和其他遗留配置。本章验证版本下 float64/image 依次为 0/0、1/0、0/0、0/0。API 能回退到本地分配器，所以程序运行成功不能代替 can_loan_messages 判断。这里没有验证订阅端借出或跨进程图像零拷贝，不全局设置 ROS_DISABLE_LOANED_MESSAGES=0。普通 Image 的动态数组和字符串不符合本例固定布局借出条件；bounded 也不自动等于 plain。

Zenoh 的借出接口另测。先按上面的手动流程启动自己的路由器，再在加载了同一工程的第二个终端执行：

```bash
RMW_IMPLEMENTATION=rmw_zenoh_cpp ros2 run image_path_demo loan_probe
ZENOH_CONFIG_OVERRIDE='transport/shared_memory/enabled=true' \
  RMW_IMPLEMENTATION=rmw_zenoh_cpp ros2 run image_path_demo loan_probe
```

本轮 Zenoh 0.1.9 的两次 Float64/Image 输出均为 0/0，发布通过本地分配器回退；这个单发布端探测没有建立订阅端 SHM 数据交付，不能验证完整跨进程零拷贝。结束后正常停止自己的路由器。

共享内存传输、Data Sharing、Zenoh 传输优化、借出 API 与进程内所有权交接分别对应不同边界。实际相机还要测 SDK/DMA、颜色转换、OpenCV 视图或复制、CPU/GPU、识别和外部订阅者。图像传递结论仅覆盖本例无进程外订阅者的一对一 intra 路径；多 UniquePtr 接收者可能需要复制，多个只读接收者还需考虑共享生命周期。

找不到包时检查 source install/setup.bash 和 ros2 pkg prefix；组件找不到检查注册类名与 CMake；接收为零先查同域旧节点、RMW 与 QoS；缺少统计应正常 Ctrl+C，而不是强制终止。超时或帧检查失败保留日志，先回到小输入定位，不把失败记录填成零延迟。实验结束后停止手动节点，恢复或取消为本实验设置的域、发现范围与 RMW，再回到日常配置。

实测记录与逐项章节验收见 [本次修订记录](../../../../docs/revision/ros2-image-path-20261003.md)。
