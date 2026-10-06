# 图像、中间件与内存路径

对应卷二 ROS2 章。正文先介绍组件所有权、借出条件和共享内存工具，再统一比较三种中间件的普通 Image 与 FixedImage。Ubuntu 22.04 / ROS2 Humble 为主线。

普通 Image 的动态数组和字符串不满足本章的原始样本借出条件。FixedImage 使用内嵌定长数组，更改尺寸需要重新生成接口，转成标准 Image 时需要复制像素并补元数据。定长布局还要由 RMW 和配置提供借出支持；本章的 Zenoh 实现对两类消息都不提供应用层借出。

## 构建并运行小图像

在 Ubuntu/Humble 的 Bash 终端，从独立工作空间构建。`BOOK` 改为实际教材目录，已有同名工作空间时另选目录。

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

rosdep 尚未初始化时，先执行一次 `sudo rosdep init`，普通用户执行 `rosdep update`。Zsh 加载对应的 setup.zsh。先停止同域旧实验与额外订阅者。

| mode | 进程布局 | 进程内通信 |
| --- | --- | --- |
| separate | 两个单线程组件容器 | 关闭 |
| same | 一个容器、两个组件 | 关闭 |
| intra | 一个容器、两个组件 | 两端开启 |

默认 64×48 BGR8、25 Hz、100 帧。intra 的前三条 POINTER 应显示同一进程及对应像素地址一致。出现 SOURCE_DONE 100 后 Ctrl+C，默认应收到 100 帧、bad_frames=0、pointer_matches=100。源码为 `src/components.cpp`，Frame 在标准 Image 外增加单机测量信息。

## 统一比较普通与定长图像

`src/image_benchmark.cpp` 的模板收发节点用同一份实现处理两种类型，固定为 1440×1080 BGR8。动态类型使用 Frame 中的标准 Image，定长类型使用 FixedImage。两端独立进程、best_effort、KeepLast(5)，接收端统一采用回调内 const 引用。

```bash
sudo apt update
sudo apt install ros-humble-rmw-zenoh-cpp ros-humble-iceoryx-posh
python3 src/image_path_demo/compare_images.py \
  --output /tmp/image-types-bgr250 --include-loan \
  --rate 250 --frames 1000 --repeat 3
```

输出目录须尚不存在，重复运行换名字。每轮分别运行三种 RMW、两类消息，以及 default/shared 两种配置。default 均采用普通发布，shared 配置如下：

| RMW | shared 的作用 | 定长消息借出 |
| --- | --- | --- |
| Fast DDS | 载入 fastdds-loan.xml，启用 Data Sharing | 查询两端能力后追加 loan 发布 |
| Cyclone DDS | 载入 cyclone-iceoryx.xml，由 RouDi 提供共享池 | 查询两端能力后追加 loan 发布 |
| Zenoh | 开启序列化数据的 SHM 传输 | 本章实现不支持应用借出 |

`--include-loan` 只给实际两端支持的定长类型追加借出组，其他组合仍完整测试普通发布。记录器启动并关闭自己的两个节点、Zenoh 路由器和 RouDi，不接管已有管理进程；已有 RouDi 时先结束已有实验，或仅选择 default。

常用选择：`--rmws` 指定 RMW 子集，`--types dynamic fixed` 选择消息类型，`--profiles default shared` 选择配置，`--domain` 更换独立域。Zenoh 路由器默认监听 127.0.0.1:17876，端口被占用时用 `--zenoh-port` 指定新端口。

本例 Zenoh 池默认 6 MiB，适合复测书中参考条件。部署时根据单帧大小与在途帧数规划 `--zenoh-shm-pool-mib`，用 `df -h /dev/shm` 和 `ulimit -l` 检查共享空间与锁定内存额度。RouDi 使用 `config/roudi.toml` 的 32 个 5 MiB 图像块和小块池。Humble 的该 iceoryx 路径采用支持的 KeepLast、活性、deadline 等 QoS 组合，详见 [官方说明](https://github.com/ros2/rmw_cyclonedds/blob/humble/shared_memory_support.md)。

逐字节检查可以先用低频运行同一矩阵：

```bash
python3 src/image_path_demo/compare_images.py \
  --output /tmp/image-types-full --rate 10 --frames 20 --repeat 1 \
  --verify-full --include-loan
```

这组检查对所有已收到的帧逐字节验证，best_effort 的接收比例另行记录。高速对照检查像素数量及首尾值。统计延迟从填充完成、publish 前到回调入口，发送频率包含分配与填充成本。每轮结束留两秒排空，参数为 `--drain-seconds`。合成数据不包含物理相机、SDK、颜色转换或识别耗时。

输出 `environment.json`、`results.json`、收发日志、Zenoh 路由器日志和共享池退出记录。结果包含实际频率、接收比例、P95/P99、坏帧数、两端借出能力和退出状态。丢失帧不参加延迟统计。使用 `--help` 查看全部选项。

## 组件布局、借出探测与慢处理

`compare.py` 保留原组件布局对照，可改变图像尺寸、深度和模拟处理耗时：

```bash
python3 src/image_path_demo/compare.py --output /tmp/image-path-small
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-layouts --width 1440 --height 1080 --channels 3 \
  --rate 250 --frames 1000 --repeat 3 \
  --rmws rmw_fastrtps_cpp rmw_cyclonedds_cpp rmw_zenoh_cpp
python3 src/image_path_demo/compare.py \
  --output /tmp/image-path-slow-5 --rmws rmw_fastrtps_cpp --modes separate \
  --rate 250 --frames 500 --work-ms 8 --depth 5
```

用新目录和 depth 100 重跑慢处理，其余条件不变。加深队列会改变有限帧实验的交付与等待时间，持续 8 ms 串行处理的理想上限为 125 Hz。

`loan_probe` 直接比较标准 Image 和定长 FixedImage。两者都填充并发布 1440×1080 BGR8，所有像素字节均为 42。`LOAN` 按 `image`、`fixed_image` 的顺序输出发布端能力。Humble 的 Fast DDS 默认为 0/0，启用 Data Sharing 后为 0/1，显式禁用后为 0/0：

```bash
unset CYCLONEDDS_URI FASTRTPS_DEFAULT_PROFILES_FILE RMW_FASTRTPS_USE_QOS_FROM_XML
unset ROS_DISABLE_LOANED_MESSAGES
RMW_IMPLEMENTATION=rmw_fastrtps_cpp ros2 run image_path_demo loan_probe
PROFILE="$(ros2 pkg prefix --share image_path_demo)/config/fastdds-loan.xml"
RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  FASTRTPS_DEFAULT_PROFILES_FILE="$PROFILE" RMW_FASTRTPS_USE_QOS_FROM_XML=1 \
  ros2 run image_path_demo loan_probe
RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  FASTRTPS_DEFAULT_PROFILES_FILE="$PROFILE" RMW_FASTRTPS_USE_QOS_FROM_XML=1 \
  ROS_DISABLE_LOANED_MESSAGES=1 ros2 run image_path_demo loan_probe
```

普通 Image 使用本地分配器回退，FixedImage 在能力为 true 时直接填充中间件样本。`PUBLISHED` 表示两次发布调用均已完成。接收检查与性能统计使用前面的统一收发程序。发布后停止访问借出对象，回调返回后停止使用借读引用和像素视图。

原 `fixed_image` / `compare_fixed.py` 保留为共享文件偏移诊断工具，详细用途及已有实测见 [iceoryx 记录](../../../../docs/revision/ros2-iceoryx-20261006.md)。正文的两类消息比较统一使用 compare_images.py，数据与解释集中在 chapters/A_ros2_image_results.tex。

找不到程序时先检查构建、source install/setup.bash 和 ros2 pkg prefix。收不到消息时检查 RMW、域、QoS 和管理进程日志。结束手动实验后恢复日常的域、发现范围及 RMW。统一收发证据见 [统一比较记录](../../../../docs/revision/ros2-image-unified-20261006.md)，本次借出探测与逐项检查见 [两类图像探测记录](../../../../docs/revision/ros2-image-loan-probe-20261006.md)。
