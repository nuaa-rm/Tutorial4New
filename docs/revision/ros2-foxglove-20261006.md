# Foxglove 登录后实测、截图与时间戳补充

用户完成登录后，在官方网页客户端接入 Ubuntu 22.04.5 / ROS 2 Humble 的合成数据，逐项验证此前缺少客户端证据的操作。日期为 2026-10-06。章节结构沿用 [图形化观测修订](ros2-visualization-20261006.md)，1.4 小结编号与连贯段落保留；本轮没有改动原有 ROS 数据源、Marker、图像标注或 SceneEntity 实现。

正文、题解与示例 README 明确：消息有有效、持续更新的 `header.stamp` 时，优先选择 Header stamp（中文界面“ROS 头时间戳”）；求导与相邻时间差也采用所选时间。pose/twist/yaw 的实际面板配置已使用它。Float64 signal 没有 Header，暂用 Log time 对照波形；精确比较信号与位姿相位时，应给自定义信号增加 Header，并在同一次采样填写相同时间。检测结果沿用输入图像的时间，不换成处理结束时的当前时间。PDF 复查还修正了数组筛选路径中被排印出来的多余反斜线，正文现在与客户端实测的 `{id==0}` 写法一致。

## 客户端验收

以下为手动 UI 实测记录，不把接口连通或文档核对代替客户端操作。结构化结果见 [runtime.json](evidence/ros2-foxglove-20261006/runtime.json)。

| 项目 | 状态 | 结果与证据 |
| --- | --- | --- |
| 登录后的实时连接 | 通过 | 本账号接入 `ws://127.0.0.1:8765`，九路合成话题及消息定义可用；桥接版本 3.5.0。许可条件仍按正文说明，不推断其他账号也能直连。 |
| 时间来源 | 通过 | 位姿、速度模长及 rpy/ypr yaw 使用 Header stamp；两条 yaw 的界面实际显示“ROS 头时间戳”，见 [UI 字段](evidence/ros2-foxglove-20261006/header-stamp-ui.txt) 与面板 JSON。 |
| FoxQL 数值变换 | 通过 | 实测 rpy/ypr yaw 转 degrees、abs/negative、mul/div/add/sub、norm/length、sqrt/log10、sin/cos、delta/derivative/timedelta、数组按 id 筛选。速度模长为 1，采样间隔约 0.100047 s；见 [实际值](evidence/ros2-foxglove-20261006/foxql-values.txt)。rpy/ypr 重合仅对应本例绕 z 轴旋转，不能据此推断任意姿态。 |
| Plot 两点检查 | 通过 | P1=(5.051888, 0.998573)，P2=(8.951682, −0.761737)，Δx=3.899794 s、Δy=1.760310；见 [面板截图](evidence/ros2-foxglove-20261006/plot-measure-panel.jpg)。 |
| XY 距离 | 通过 | position.x/y 使用全时段、1:1 尺度，两端点距离 1.999565 m，符合 1 m 半径圆的直径；见 [面板截图](evidence/ros2-foxglove-20261006/xy-measure-panel.jpg)。 |
| 图像与标注同步 | 通过 | 原图绿色色块与黄色框、红色中心、文字同时显示。临时把顶层及每个标注元素的时间统一加 50 ms，开启同步后出现“等待同步消息”；恢复原话题后立即更新。失败、恢复截图及 [偏移夹具](evidence/ros2-foxglove-20261006/shift_annotations.py) 保留。 |
| ROS 与原生三维图形 | 通过 | map 中显示 TF、Pose、Path、MarkerArray，并单独显示 SceneEntity 方块与文字。Measure 在地面选择两点显示距离，见两张 3D 测量截图；任意点击距离不作为已知尺寸标定。 |
| 枚举状态名 | 通过 | 在 Humble 构建 [两份完整接口](evidence/ros2-foxglove-20261006/enum-fixture/)，重新加载安装环境并重启桥接，发布 `mode=1` 后 Raw Messages 显示 `1 (TRACKING)`，见 [截图](evidence/ros2-foxglove-20261006/enum-tracking.jpg) 和构建日志。State Transitions 面板未另行实测。 |
| MCAP 播放、暂停与定位 | 通过 | 官方客户端实际读取 ROS 录制文件，从头播放至尾并暂停；点击时间线定位到 14:27:50.860，点击曲线定位到 14:27:48.571，图像和三维场景同步跳转。见 [时间线](evidence/ros2-foxglove-20261006/timeline-seek.txt)、[曲线](evidence/ros2-foxglove-20261006/plot-seek.txt)。 |
| 布局保存与面板恢复 | 通过 | 本轮创建的“Tutorial4New ROS2 图形化观测”布局保存、刷新后恢复；五份面板 JSON 实际导入并应用，暂时替换的面板已恢复，其他用户布局未改动。 |
| 桌面全新安装与部分导出操作 | 未完成 | Linux deb 全新安装/启动、3D Alt 表面吸附、CSV 文件下载、完整布局文件下载未完成。本地文件选择器未成功，本次 MCAP 使用本机 HTTP Range 的 remote-file 路径读入；不把这项视作本地选择器通过。 |

录制文件约 80 MB，保留在临时验证目录，未加入仓库。客户端本次显示的数据范围是 14:27:44.833–14:27:56.630（CST），不要与首轮 ROS 回放的另一份录制跨度混淆。合成色块、固定置信度和圆轨迹不代表相机、标定或识别算法；既有真实相机与第二台物理主机缺口保留。完整章节清单仍为 **19 项通过、1 项未完成**。

## 图片与可恢复配置

五张新增书内图片均来自实际客户端截图，先查看候选图及书页，再采用 `_revised` 命名。裁剪仅聚焦面板，未改写数据、控件或截图内容；原始全窗口截图保留在证据目录。对应关系与哈希见 [image-manifest.json](evidence/ros2-foxglove-20261006/image-manifest.json)。

| 书内图片 | 实际来源 |
| --- | --- |
| `ros2_foxglove_enum_revised.jpg` | `enum-tracking.jpg` |
| `ros2_foxglove_plot_measure_revised.jpg` | `plot-measure-panel.jpg`，原窗口 `plot-measure.jpg` 保留 |
| `ros2_foxglove_xy_measure_revised.jpg` | `xy-measure-panel.jpg`，原窗口 `xy-measure.jpg` 保留 |
| `ros2_foxglove_image_sync_revised.jpg` | `image-sync-detail.jpg`，另有同步及失败/恢复截图 |
| `ros2_foxglove_replay_revised.jpg` | `overview-playback.jpg` |

[随书面板配置](../../02-专项技术栈/examples/ros2/visualization-demo/foxglove-panels/) 包含 threeD、image、plot、yaw、xy；正文和 README 写明实际“导入/导出设置”与“保存更改”操作。它们是单面板配置，整份布局文件的下载仍另列待验证。

## 编译、复查与收尾

卷二最终 **328 页**。干净隔离输出中三遍 XeLaTeX 编译，新增七个观测小节在书内第 19–36 页，1.4 小结仍在第 83 页。实际检查目录、Foxglove 全部新增截图与相邻正文、工程衔接、小结/验收和新增题解；结果见 [PDF 检查](evidence/ros2-foxglove-20261006/pdf-check.json) 与 [结构检查](evidence/ros2-foxglove-20261006/static-checks.json)。没有新增溢出、缺字、缺文件、未定义引用或重复标签；工程部分既有 408–409 行 2.8734 pt 越界和模板 Fandol 斜体替代提示保留。

本轮改动相对开始时备份见 [foxglove.diff](evidence/ros2-foxglove-20261006/foxglove.diff)，来源哈希见 [source-hashes.json](evidence/ros2-foxglove-20261006/source-hashes.json)。更早的工程、Launch、图像链路等工作区修改保留，没有合并进本轮补丁或批量提交。

实时合成发布端、两次桥接、偏移标注节点与枚举发布端均已停止。ubuntu2204 在本轮开始时已经运行，因此保持运行。本机 `127.0.0.1:8766` 的临时录制文件服务保留，供已打开的客户端继续回放；只服务本机文件并允许官方网页来源读取。网页已保存最终四面板布局，暂停在 14:27:48.571，见 [最终画面](evidence/ros2-foxglove-20261006/final-layout.jpg)。

时间语义与操作依据仍为官方 [Plot](https://docs.foxglove.dev/docs/visualization/panels/plot)、[FoxQL](https://docs.foxglove.dev/docs/visualization/foxql) 与 [Image](https://docs.foxglove.dev/docs/visualization/panels/image) 文档；本记录的通过项另有上述实际 UI、构建和截图证据。
