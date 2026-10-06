# 卷二 ROS2 图形化观测补充

在完整基础工程之后、构建启动与排障之前，加入 `A_ros2_visualization.tex`，形成 1.1.6–1.1.12 七个小节。它承接已经收到的消息，让读者把同一组数据放到曲线、原图、二维标注和三维场景中对照，再保存布局与录制回放。原有 1.4 本章小结编号保留，并接入图形化观测的回顾；章首目标、学时、验收与题解同步更新。

完整文字与示例修改见 [visualization.diff](evidence/ros2-visualization-20261006/visualization.diff)，可运行项目见 [visualization-demo](../../02-专项技术栈/examples/ros2/visualization-demo/README.md)。原有 ROS 工程、Launch 和图像链路修订保留；本次没有重命名或移动 tex 文件，也没有修改共享模板。

## 新增内容

- rqt：Node Graph、数值字段路径、两条曲线、PyQtGraph、图像 raw/compressed、保存画面、停止后的显示与空白排查。
- RViz2：Fixed Frame、TF、Pose、Path、Image、QoS、相机工具和配置恢复；完整 MarkerArray 代码，说明球/方块、箭头、线、点、文字、资源模型、颜色透明度、ns/id、寿命、删除与 frame_locked。
- Foxglove：Linux deb 安装、架构检查、桌面/网页与当前账号许可条件、桥接安装及本机/跨机连接、Raw Messages 与布局保存。
- Plot：`.@rpy`/`.@ypr`、角度单位、常数换算、绝对值、向量模长、数组长度/筛选、差分/求导/时间间隔；Header stamp/Log time、两点检查、XY 距离、1:1 尺度、缩放和 CSV。
- 标注：ImageAnnotations 的框、圆、文字、像素坐标、透明度、完全相同时间戳同步；另外说明 `_foxglove_enum` 状态名标注及两份完整消息定义。
- 3D 与回放：SceneUpdate/SceneEntity 的方块和文字、实体删除与寿命、地面测量与 Alt/Option 吸附、MCAP 录制、检查及本地回放。

新增 6 道随堂题、2 道章末题及全部对应题解。安装与连接的操作由后续 Plot、Image、3D 和回放练习共同验收，不另设只重复按钮操作的习题。全章现为 30 道随堂题和 16 道章末题；原有 14 道章末题仍覆盖工程与大图像链路，本次增加显示排障与表达式/单位自测。

## 实际验证与边界

在已有 Ubuntu 22.04.5 / Humble 容器中安装缺少的图形化依赖，实测 rqt_plot 1.1.5、rqt_image_view 1.2.0、RViz2 11.2.29、foxglove_bridge/foxglove_msgs 3.5.0、MCAP 插件 0.15.17、PyQtGraph 0.12.4。主机不作为 ROS 运行环境。测试使用独立通信域和 Xvfb，不操作用户的桌面窗口。

[运行结论](evidence/ros2-visualization-20261006/runtime.json) 中，九个话题各收到至少 20 条消息；单位四元数、1 m 圆、1 m/s 速度、TF、20 组原图/标注时间与中心像素、Marker 删除恢复和 SceneEntity 内容均通过。桥接的九路 CDR 消息实际接收并解码；新版桥接支持 `foxglove.sdk.v1`，验证脚本兼容旧协议，客户端操作仍使用官方 Foxglove。正常退出见 [bridge.txt](evidence/ros2-visualization-20261006/bridge.txt)。

MCAP 数据跨度 11.993 秒，各话题录下 120–121 条消息。停止实时发布、等待发布者消失并排空订阅队列后，重新执行 ROS 回放，各话题收到 120–121 条，避免把旧实时帧误计入回放；见 [录制](evidence/ros2-visualization-20261006/record.txt)、[元数据](evidence/ros2-visualization-20261006/metadata.yaml) 与 [回放](evidence/ros2-visualization-20261006/play.txt)。录制文件位于本次临时验证目录，不把约 80 MB 的测试数据加入教材仓库，读者可用项目重录。

rqt 的真实 Plot 插件收到并绘制两条各 120 样本的曲线；Image View 实际启动并显示原图。RViz2 加载随书配置，实际显示球、箭头、轨迹、文字、TF 和原图，工具栏也具备 Move Camera、Select、Focus Camera。初次实测修正了 MarkerArray 的 Topic 属性及相机工具缺失，最后截图使用修正配置。

首轮 Foxglove 网页停在登录页，未执行客户端交互。用户登录后已补测布局保存恢复、FoxQL 转换、Header stamp 设置、同步叠加及 50 ms 失败恢复、Plot/XY 两点测量、3D 地面测量、MCAP 播放/暂停/定位，并实际构建枚举包、显示 `1 (TRACKING)`。五张截图和可恢复面板 JSON 已加入教材，详见 [登录后实测记录](ros2-foxglove-20261006.md)。Linux 桌面全新安装、3D Alt 吸附、本地文件选择器、CSV 和完整布局文件下载仍未完成；MCAP 客户端回放实际走本机 HTTP remote-file 路径。合成色块、轨迹与固定置信度不代表相机、标定或识别算法；既有真实相机和第二台物理主机验收缺口继续保留。

## 图片与排版

首轮新增两张真实运行截图，先查看候选画面，再采用 `_revised` 文件名：

- 临时 `rqt_plot.png` → `images/ros2_rqt_plot_revised.png`：保留真实订阅值，截图前放大插件的字体与图例，方便书页内阅读。
- 临时 `rviz/screen.png` → `images/ros2_rviz_views_revised.png`：保留真实界面、话题显示与目标几何；提供完整可恢复的 `demo.rviz`。

登录后再补五张真实 Foxglove 截图：枚举名、Plot 两点检查、XY 距离、图像标注同步与回放总览。没有改写截图像素或合成界面。正文交叉引用同步，既有 `_revised` 图片内容未改变，按技能规则沿用原检查。消息类型在斜线边界分行，完整 Python 源码直接引入，调整局部字号与分页空间，避免类型名拆散或代码末行落单。

## 完整章节检查清单

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main.tex：加入三种查看器、标注、测量与回放目标及半天至一天的实践学时，先修和 Humble 边界保留。 |
| 2 核心示例 | 通过 | 既有示例保留；七个新增小节含完整来源、步骤、参数、预期画面及排障判断，安装与后续面板共用数据源。 |
| 3 复杂概念项目 | 通过 | 新增 visualization-demo，四份 Python 源文件、RViz 配置、合成输入及完整运行说明；既有工程保留。 |
| 4 正文项目讲解 | 通过 | 目录与四份完整源码直接引入；解释发布顺序、同一时间戳、像素数据、图元与对象更新；显示配置由表格和手动操作说明。 |
| 5 命令与参数 | 通过 | 包/程序/字段语法、安装、源目录、监听地址、架构与账号条件说明完整，7 个正文 Shell 块通过 bash 语法检查。 |
| 6 随堂练习 | 通过 | 全章 30 题；新增来源、rqt、Marker、Plot、图像标注、回放 6 题，安装与连接由后续练习共同覆盖。 |
| 7 难点归纳 | 通过 | Marker 与观测回放 conclusion，类型/用途和函数条件表；像素/世界坐标、更新/删除、两种时间及测量单位明确。 |
| 8 易错提示 | 通过 | 非零 alpha、合法四元数、TF/QoS、尺寸/编码、完全相同时间戳、角度绕回、监听与 localhost、录制目录和过期行为有解释。 |
| 9 本章小结 | 通过 | 1.4 仍用连贯段落回顾收发、图形化观测、工程排障和图像实验，继续衔接下一章。 |
| 10 章末习题 | 通过 | 16 题保留基础/提高/实践覆盖；新增显示排障与路径/单位 2 题，题量依据见上文。 |
| 11 本章验收 | 通过 | 第三项扩展实际曲线/图像/Marker、布局、同步、测量、录制回放与交付记录，权限不足时明确待补验。 |
| 12 参考答案 | 通过 | 30 道随堂题与 16 道章末题均有可定位答案，开放题明确输出与判断标准。 |
| 13 作者语言习惯 | 通过 | 从盯数字的问题接着讲，用你/我们带着连续操作，解释选择与结果；避免把官方字段定义直接堆成正文。 |
| 14 图片实际检查 | 通过 | 两张 rqt/RViz 与五张 Foxglove 候选截图及实际书页内显示已查看；既有已标记图未改动其机制与风格。 |
| 15 图片标记与引用 | 通过 | 七张新图使用 `_revised`，includegraphics 与标签、图注同步；原截图、对应关系和哈希可追溯。 |
| 16 文件组织 | 通过 | 新内容单独放入 A_ros2_visualization.tex，项目在本卷 examples/ros2；没有移动/重复创建答案文件。 |
| 17 包含与引用 | 通过 | 当前入口包含 33 文件；资源、标签唯一性、编译后交叉引用和题解定位检查通过，最新计数见登录后实测的 static-checks.json（含 lstinputlisting 选项标签）。 |
| 18 源码与格式 | 通过 | 沿用 example/exercise/note/conclusion、tbash、三线表和源码引入；局部字号、消息类型断行和分页空间帮助阅读。 |
| 19 示例实际运行 | 未完成 | ROS 数据、rqt/RViz、桥接、MCAP、登录后主要面板交互与枚举包构建显示通过；全新桌面安装、3D Alt 吸附、部分文件导出/选择器及既有相机/物理多机缺口保留。 |
| 20 编译与 PDF | 通过 | 卷二入口在干净隔离构建目录编译至目录/引用稳定，新增正文、题解、目录及小结/验收页面实际查看，具体结果见 pdf-check.json。 |

合计 19 项通过、1 项未完成、0 项不适用。未完成项是运行验证边界，正文没有留占位段落。

## 官方依据

安装与账号条件见 [Foxglove 下载](https://foxglove.dev/download)、[ROS2 连接](https://docs.foxglove.dev/docs/getting-started/frameworks/ros2)、[实时连接许可](https://docs.foxglove.dev/docs/visualization/connecting/live)。字段路径与测量见 [FoxQL](https://docs.foxglove.dev/docs/visualization/foxql)、[Plot](https://docs.foxglove.dev/docs/visualization/panels/plot)。标注与图形见 [Image](https://docs.foxglove.dev/docs/visualization/panels/image)、[ImageAnnotations](https://docs.foxglove.dev/docs/sdk/schemas/image-annotations)、[枚举标注](https://docs.foxglove.dev/docs/visualization/annotate-ros-enum-fields)、[SceneUpdate](https://docs.foxglove.dev/docs/sdk/schemas/scene-update)、[3D](https://docs.foxglove.dev/docs/visualization/panels/3d)。ROS Marker 依据 [Humble 官方源码](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials/Intermediate/RViz/Marker-Display-types/Marker-Display-types.rst)，当前桥接握手依据 [Foxglove SDK](https://github.com/foxglove/foxglove-sdk/blob/main/rust/foxglove/src/websocket/handshake.rs)。核对日期 2026-10-06。

首轮整卷 **325 页**，新增观测内容位于书内第 19–34 页；实际查看物理页 4、7、25–41、86–88、295–296、302，覆盖章首、目录、全部新增正文与两张截图、相邻工程页、1.4 小结/验收及新增题解。首轮 PDF SHA-256 为 `184a21220d20050c6bad5fc79ba8749f8260b815e1022cb51f3e739f21db6fda`。登录后补图与时间戳提醒的最新整卷为 **328 页**，新增观测内容扩展到书内第 19–36 页，最新页码、哈希与实际检查见 [补测记录](ros2-foxglove-20261006.md)。两轮目录、引用与编号均经过三遍编译稳定，没有新增溢出、缺文件、缺字、重复标签或未定义引用。工程部分原有 408–409 行 2.8734 pt 越界与模板 Fandol 斜体替代提示保留，不属于本次新增内容。

首轮测试进程均已退出；按容器自身 cgroup 核对只剩 Distrobox 入口及等待进程后，将首轮启动的 ubuntu2204 恢复为开始前的停止状态。登录后补测开始时容器已在运行，故补测结束后保留其运行状态；自身实时测试进程已停止，本机 MCAP 文件服务保留供客户端回放。软件包保留在该验证容器中，用户桌面配置未修改。
