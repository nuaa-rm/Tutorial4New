# 用一组数据练习 ROS2 图形化观测

对应卷二 ROS2 基础的“把消息画出来”及其后的小节。Ubuntu 22.04 / ROS2 Humble，Python 3.10；合成图像与轨迹不需要相机，程序不控制机器人。

## 安装与启动

在运行 ROS 的 Ubuntu 环境里安装：

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install ros-humble-rqt ros-humble-rqt-graph \
  ros-humble-rqt-publisher ros-humble-rqt-topic \
  ros-humble-rqt-plot ros-humble-rqt-image-view \
  ros-humble-rviz2 ros-humble-foxglove-msgs \
  ros-humble-tf2-ros python3-pyqtgraph \
  ros-humble-foxglove-bridge ros-humble-rosbag2-storage-mcap
cd /实际教材路径/02-专项技术栈/examples/ros2/visualization-demo
python3 data_node.py
```

运行目录要换成自己的路径。几个模块一起放在该目录，无需构建功能包。打开其他终端时，加载同样的 Humble 环境，使用相同的 ROS_DOMAIN_ID、RMW_IMPLEMENTATION 和发现范围；本机实验可统一 `ROS_LOCALHOST_ONLY=1`。

每条启动命令各占一个终端，分别试：

```bash
source /opt/ros/humble/setup.bash
ros2 run rqt_graph rqt_graph
ros2 run rqt_plot rqt_plot /viz/signal/data /viz/pose/pose/position/x
ros2 run rqt_image_view rqt_image_view /viz/image
# 在本项目目录执行
rviz2 -d demo.rviz
```

Plot 应显示 sin(t) 和 cos(t)，Image View 显示深色背景上的绿色色块。RViz2 使用 map 为 Fixed Frame，显示运动目标、TF、最近 120 个位置及文字。`demo.rviz` 是配置示例，正文另给从空窗口手动添加显示的步骤。

```bash
# 先执行第一条并观察，再执行第二条
ros2 param set /viz_demo show_target false
ros2 param set /viz_demo show_target true
```

两条命令分别删除、恢复 id=0 的球，箭头和文字保留。停止节点后 Marker 与 SceneEntity 在 0.5 秒后过期，Image/Plot 可能保留最后的数据。

## Foxglove

查看电脑上的桌面端从 [官方下载页](https://foxglove.dev/download) 选 Linux x64/arm64 的 deb，在文件所在目录执行 `sudo apt install ./foxglove-studio-实际文件名.deb`。Windows/macOS 使用对应安装程序；网页端打开 [app.foxglove.dev](https://app.foxglove.dev/)。当前官方版本的直接 WebSocket 连接需要 Developer 席位或相应许可，参见 [连接说明](https://docs.foxglove.dev/docs/visualization/connecting/live)。

另一个加载 Humble 的终端启动桥接：

```bash
ros2 launch foxglove_bridge foxglove_bridge_launch.xml \
  address:=127.0.0.1 port:=8765
```

Open connection → Foxglove WebSocket → `ws://localhost:8765`。跨机器时按正文调整监听地址、实际 IP 和可信网络条件，不把查看电脑的 localhost 当成机器人的地址。

添加 Raw Messages、Plot、Image、3D，保存布局并导出 JSON。常用路径：

```text
/viz/signal.data
/viz/pose.pose.position.x
/viz/pose.pose.orientation.@rpy.yaw.@degrees
/viz/twist.twist.linear.@norm
/viz/path.poses.@length
/viz/pose.pose.position.x.@derivative
/viz/pose.pose.position.x.@timedelta
/viz/markers.markers[:]{id==0}.pose.position.x
```

时间序列函数使用 Timestamp 横轴。消息有有效的 `header.stamp` 时优先选择 Header stamp（中文界面“ROS 头时间戳”），按采集或生成时间对齐；本例 pose/twist/path 使用它，Float64 的 signal 没有 header，使用 Log time。求导和相邻消息时间差也按所选时间计算。比较对象应使用同一种时钟，先检查零时间戳和停更问题。

Inspection 工具选两点读 Δx/Δy；XY 图用位置 x/y 和 1:1 尺度，可以测空间距离。Image 选 `/viz/image`，启用 `/viz/annotations` 和 Sync timestamps。应显示黄色框、红色中心和标签，关闭标注时原图色块保留。检测结果沿用输入图像的 `header.stamp`，处理完成时的当前时间不能替代它；原图和标注必须精确匹配。本次把标注偏移 50 ms 后，网页客户端显示“等待同步消息”，恢复原图时间后继续更新。

### 恢复面板设置

`foxglove-panels/` 提供从实际客户端面板导入/导出设置中保存并验证的 JSON：

| 文件 | 面板与内容 |
| --- | --- |
| `threeD.json` | 3D：map 坐标系、TF、ROS Marker/Pose/Path 与 SceneEntity、相机和网格。观察原生实体时关闭前三个 ROS 图形话题。 |
| `image.json` | Image：原图、ImageAnnotations 与时间戳同步。 |
| `plot.json` | Plot：正弦、位置 x 与速度模长；pose/twist 优先 Header stamp。 |
| `yaw.json` | Plot：rpy/ypr 的 yaw 角度，两条曲线均用 Header stamp。 |
| `xy.json` | Plot：position.x/y、全时段与 1:1 比例，适合测直径。 |

先添加对应类型的面板，打开该面板的设置页，点击设置页右上角“更多操作” → “导入/导出设置”，复制相应文件中的完整 JSON、粘贴并应用。这些文件只恢复各自的面板；自行调整排列后，在布局菜单中右键当前布局 → “保存更改”。整份布局需要另用“导出”保存。本次验证使用网页客户端；不同版本的控件译名可能略有差异。

3D 选 map，启用 `/tf`、`/viz/pose`、`/viz/path`、`/viz/markers`。再关闭 markers，开启 `/viz/scene` 对照原生方块实体。Measure 默认在地面放端点，Alt/Option 可吸附对象。显示与测量的完整操作在教材正文，当前官方界面参见 [Plot](https://docs.foxglove.dev/docs/visualization/panels/plot)、[Image](https://docs.foxglove.dev/docs/visualization/panels/image)、[3D](https://docs.foxglove.dev/docs/visualization/panels/3d)。

## 录制与回放

保持节点运行，用尚不存在的输出目录录制：

```bash
mkdir -p ~/ros_viz_recordings
cd ~/ros_viz_recordings
ros2 bag record -s mcap -o viz_demo_01 \
  /viz/signal /viz/pose /viz/twist /viz/path /viz/image \
  /viz/markers /viz/annotations /viz/scene /tf
```

至少十秒后 Ctrl+C 收尾，`ros2 bag info viz_demo_01` 查看消息数量。停止数据源，关闭实时连接，再在 Foxglove 打开目录中的 `.mcap`。若在 ROS 工具中回放，使用 `ros2 bag play viz_demo_01`，并保持原发布端已停止，避免两套数据混在一起。

## 文件与验证

- `data_node.py`：10 Hz 统一数据源与 TF，曲线、原图、位姿共享生成时刻。
- `markers.py`：MarkerArray 的对象更新、删除、尺寸、颜色和寿命。
- `annotations.py`：沿用原图时间的框、中心和文本，兼容有/无顶层 timestamp 的消息版本。
- `scene.py`：SceneUpdate 中的方块与文字实体。
- `demo.rviz`：完整可恢复的 RViz2 显示配置。

仓库的 `scripts/verify_ros_visualization.py` 在 Humble 环境检查实际 ROS 订阅、参数删除/恢复、WebSocket CDR 消息和 MCAP 读回；桌面窗口及 Foxglove 的账号和交互验证按修订记录分别说明。

维护者运行上述验证脚本时，还需要兼容 Python 3.10 的 WebSocket 客户端。本轮使用 `websockets==12.0`，Ubuntu 22.04 自带的 9.1 不适合这份异步测试；新版桥接使用 `foxglove.sdk.v1`，脚本同时声明旧协议兼容项。这只是验证脚本的依赖，使用 Foxglove 客户端时不需要安装 Python WebSocket 库。

下面从仓库根目录执行；输出目录请换成尚未录制过的新名字。临时虚拟环境保留系统 ROS Python 包：

```bash
source /opt/ros/humble/setup.bash
sudo apt install python3-venv
python3 -m venv --system-site-packages /tmp/ros-viz-check-venv
source /tmp/ros-viz-check-venv/bin/activate
python -m pip install 'websockets==12.0'
export ROS_DOMAIN_ID=91 ROS_LOCALHOST_ONLY=1
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
python scripts/verify_ros_visualization.py --output /tmp/ros-viz-check-01
```

这份测试会自行启动并关闭合成发布端、桥接和录制回放进程，保留日志、运行结论及 MCAP。它不代替 Foxglove 登录后对布局、表达式、标注叠加和测量工具的交互检查。
