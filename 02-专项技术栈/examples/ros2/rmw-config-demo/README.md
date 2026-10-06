# RMW 配置对照：Fast DDS、Cyclone DDS 与 Zenoh

对应正文 `chapters/A_ros2_image_path.tex` 的“中间件怎么选：先比较同一条链路”。用官方 talker/listener 复用同一份节点程序，只改变中间件及其配置，观察安装、选择实现、加载配置和发现节点分别在哪一步起作用。

## 环境与安装

在已配置官方 ROS 软件源的 Ubuntu 22.04 / ROS 2 Humble 环境中使用 Bash；Distrobox 用户在 Ubuntu 容器内安装和运行。项目只有配置文件，不需要 colcon 构建。

```bash
sudo apt update
sudo apt install ros-humble-demo-nodes-cpp \
  ros-humble-rmw-fastrtps-cpp ros-humble-rmw-cyclonedds-cpp
sudo apt install ros-humble-rmw-zenoh-cpp
```

若 Zenoh 包没有候选版本，先核对 Ubuntu/ROS 发行版与官方软件源并重新更新索引，再查 [rmw_zenoh 的 Humble 安装说明](https://github.com/ros2/rmw_zenoh/tree/humble#installation)。正文另给出了独立工作空间的源码安装步骤；不要安装其他发行版的二进制包。

## 准备 DDS 配置

在本卷目录（包含 `main.tex`、`chapters/`、`examples/`）执行一次：

```bash
cp -r examples/ros2/rmw-config-demo ~/ros2-rmw-demo
ip -br -4 addr
```

若目标目录已存在，先选一个新的目录并同步修改后续路径。编辑复制出的两份 XML，把 `192.168.10.20` 换成**当前机器**所选网卡的 IPv4 地址，去掉 `/24` 等前缀长度。第二台机器使用它自己的地址。示例使用支持组播的局域网；本机收发通过不代表第二台机器已通过。

每轮先 Ctrl+C 停止上一轮节点。在两个终端分别加载 Humble、设置相同的域，再选择下面的一套配置：

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42
unset ROS_LOCALHOST_ONLY ROS_DISCOVERY_SERVER
unset RMW_FASTRTPS_USE_QOS_FROM_XML
```

Fast DDS：

```bash
unset CYCLONEDDS_URI
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export FASTRTPS_DEFAULT_PROFILES_FILE="$HOME/ros2-rmw-demo/fastdds.xml"
ros2 daemon stop
```

Cyclone DDS：

```bash
unset FASTRTPS_DEFAULT_PROFILES_FILE
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI="file://$HOME/ros2-rmw-demo/cyclonedds.xml"
ros2 daemon stop
```

随后终端 A 执行 `ros2 run demo_nodes_cpp talker`，终端 B 执行 `ros2 run demo_nodes_cpp listener`。listener 应持续输出同一序号的 `Hello World`。两套配置均用于选择网卡；Fast DDS 额外关闭内建传输、显式使用 UDPv4，便于观察网络路径。没有启用借出消息或证明零拷贝。

Fast DDS 先定义 transport，再由默认 participant 引用它；Cyclone DDS 在 `Domain/General/Interfaces` 中直接选择网卡。`Domain Id="any"` 是配置匹配范围，实际域仍由 `ROS_DOMAIN_ID` 指定。两种 XML 的命名空间和标签不同，不能互换。

## Zenoh 本机收发

停止 DDS 节点。三个新终端分别执行：

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42
export RMW_IMPLEMENTATION=rmw_zenoh_cpp
unset ROS_LOCALHOST_ONLY ROS_DISCOVERY_SERVER
unset CYCLONEDDS_URI FASTRTPS_DEFAULT_PROFILES_FILE
unset ZENOH_SESSION_CONFIG_URI ZENOH_ROUTER_CONFIG_URI
unset ZENOH_CONFIG_OVERRIDE
ros2 daemon stop
```

终端 A 运行 `ros2 run rmw_zenoh_cpp rmw_zenohd` 并保持运行；终端 B 运行 talker；终端 C 运行 listener。默认节点会连接本机 TCP 7447 的 router 获取发现信息。应看到 listener 持续收包；仅仅有 talker 的发布日志不能证明连通。

## Zenoh JSON5 与跨机器连接

复制**已安装版本**自带的完整配置，不用正文的局部片段替代整个文件：

```bash
mkdir -p ~/ros2-rmw-demo/zenoh
zenoh_share="$(ros2 pkg prefix --share rmw_zenoh_cpp)"
cp "$zenoh_share/config/DEFAULT_RMW_ZENOH_SESSION_CONFIG.json5" \
  ~/ros2-rmw-demo/zenoh/session.json5
cp "$zenoh_share/config/DEFAULT_RMW_ZENOH_ROUTER_CONFIG.json5" \
  ~/ros2-rmw-demo/zenoh/router.json5
```

先按正文把 router 的 `listen.endpoints` 改为 `["tcp/127.0.0.1:7447"]`，session 的 `mode` 改为 `"client"`、`connect.endpoints` 改为 `["tcp/127.0.0.1:7447"]`。保持其他配置，勿重复追加已有键。

router 终端设置 `ZENOH_ROUTER_CONFIG_URI="$HOME/ros2-rmw-demo/zenoh/router.json5"` 后运行 rmw_zenohd；两个节点终端设置 `ZENOH_SESSION_CONFIG_URI="$HOME/ros2-rmw-demo/zenoh/session.json5"` 后运行 talker/listener。这些变量接收绝对文件路径，不加 `file://`。

跨机器时，假设 router 主机的实际地址为 `192.168.10.20`：把 router 的监听地址替换为 `tcp/192.168.10.20:7447`；两台节点机器的 session 均使用 `mode: "client"`，并连接 `tcp/192.168.10.20:7447`。两端加载各自的完整 session 文件、使用相同域并重新启动。先确认到该主机 TCP 7447 的路由和防火墙允许连接。`127.0.0.1` 只能到当前机器，不能指向远端 router。

这一拓扑把应用数据交给 router 转发。默认 peer 模式可建立节点直连，不能据此把 router 固定理解成“所有数据都必经的服务器”。Zenoh RMW 与 DDS RMW 无法直接互通；`zenoh-bridge-ros2dds` 是另一条桥接路线，也不能当成 rmw_zenohd 的直接替代品。

## 恢复与验证边界

先分别停止本次节点与 router，再在每个实验终端执行：

```bash
unset RMW_IMPLEMENTATION ROS_DOMAIN_ID ROS_LOCALHOST_ONLY
unset FASTRTPS_DEFAULT_PROFILES_FILE CYCLONEDDS_URI
unset ROS_DISCOVERY_SERVER RMW_FASTRTPS_USE_QOS_FROM_XML
unset ZENOH_SESSION_CONFIG_URI ZENOH_ROUTER_CONFIG_URI
unset ZENOH_CONFIG_OVERRIDE
ros2 daemon stop
```

实验开始前若已有自定义变量，应恢复原值；上述命令用于起初未设置这些变量的临时终端。实验不改 shell 启动文件。改变环境后必须重启进程。

验收看安装后的包位置、两端 RMW/域/配置路径、listener 实际消息和 router 日志。XML 能解析、正文能编译均不能证明实际收发或跨机器连通。2026-10-05 已在 Ubuntu 22.04 / Humble 容器完成六组本机收发：两种 DDS 的默认配置与 XML、Zenoh 默认发现与完整 JSON5 的 client/router 配置，每组都收到至少三条对应消息。验证使用临时域 97、独立话题，XML 地址换成当前网卡地址，JSON5 对照端口换成 17747；原始结果见 [运行记录](../../../../docs/revision/evidence/ros2-rmw-config-20261005/runtime.json)。未执行全新安装、源码构建或第二台机器的通信。

配置依据：[Fast DDS 2.6 网卡白名单](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/transport/whitelist.html)、[默认 participant profile](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/xml_configuration/domainparticipant.html)、[Humble rmw_fastrtps 配置优先级](https://github.com/ros2/rmw_fastrtps/tree/humble#full-qos-configuration)、[Cyclone DDS 0.10.2 配置定义](https://github.com/eclipse-cyclonedds/cyclonedds/blob/0.10.2/etc/cyclonedds.xsd)、[Humble rmw_zenoh](https://github.com/ros2/rmw_zenoh/tree/humble)。
