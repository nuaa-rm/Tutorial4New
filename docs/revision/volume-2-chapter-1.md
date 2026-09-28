# 卷二第一章：ROS2 基础修订记录

本章保留原来的“先建节点，再解释通信，最后整理工程”讲解线。语言参照原 11/12/13.tex，用连贯段落带着读者操作，随步骤解释环境、名字和结果，不把正文改成检查清单。20 项中 19 项通过，第 19 项仍有真实环境验证缺口；本章及全书尚未全部验收。

## 内容、项目与题解

- 默认环境改为 Ubuntu 24.04 / Jazzy，同时给出 Humble 22.04 的包名、环境脚本与发现范围差异。说明 Distrobox 中共享源码与容器内工具链的关系；不把 Jazzy 实测写成 Humble 实测。
- 把原附录完整工程移到节点和接口旁边，形成 `examples/ros2/basic-interfaces-demo` 的两个完整包。正文直接引入消息、头文件、实现、入口、清单与构建文件，并解释句柄存活、执行器、时间戳、接口生成和依赖顺序。
- 复用 `examples/ros2/training_tools`，完整展示构建、测试、参数、两份 Launch、日志和调试。新增独立 `cmake/Auto.cmake` 用于比较 ament_auto；没有更改卷一引用的主 CMakeLists.txt。
- 补充 QoS 不兼容与恢复实验、真实 rqt 插件观察、带字段变体的接口重建、安装产物与独立 IDE 构建的区别。纠正 QoS 保证、Vector3/Point、组件/执行器和计数等于时间等容易误解的表达。
- 12 道随堂练习与 10 道章末题均有标签、引用题解和可观察的判断标准。保留章首、阶段归纳、章末知识地图和操作验收。

## 20 项检查

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main.tex 第一章 introduction 包含可操作目标、基础约一周与工程 2–3 天学时、卷一前置和卷三集成边界。 |
| 2 核心示例 | 通过 | A_ros2、project、engineering 的环境/图、发布订阅/QoS、定时器/接口/服务、完整工程/rqt、依赖/Launch/日志/调试示例有前提、操作与判断。 |
| 3 复杂概念项目 | 通过 | basic-interfaces-demo 与复用的 training_tools 均有完整源码、构建文件、清单、配置和 README；不再依赖正文之外的缺失工程。 |
| 4 正文展示项目 | 通过 | 两个工程的目录、完整核心代码和行为配置直接引入；按执行顺序讲接口生成、收发回调、安装、参数覆盖、命名空间/重映射与进程事件。 |
| 5 语法与参数 | 通过 | ros2、colcon、rosdep、Launch 与日志命令有通用形式或参数解释，说明终端环境、工作目录、替换名字、两发行版条件与 GUI 前提。 |
| 6 随堂练习 | 通过 | 12 个 exercise 覆盖关系见下表，QoS 与回复观察新增独立任务，其余相邻知识合并但能力不遗漏。 |
| 7 难点归纳 | 通过 | 包/节点/话题、QoS、消息语义、域/发现范围/中间件、构建安装/Launch、IDE 产物均有 conclusion 或明确对比表。 |
| 8 易错提示 | 通过 | 混加载发行版、回调生命周期、参数类型、静态对端、旧进程/daemon、环境继承、遗漏安装、日志级别与工具接口查询问题均有说明；使用独立工作空间避免覆盖。 |
| 9 本章小结 | 通过 | A_ros2_review 用功能包、通信闭环、构建启动观察与排错串联知识，区分要练熟和按项目查询的内容。 |
| 10 章末习题 | 通过 | 10 题覆盖核心概念、环境、QoS、接口、服务、发现、Launch、日志与新旧产物，包含基础、提高、实际运行任务。 |
| 11 本章验收 | 通过 | 5 项现场操作检查不同输入、增加接口字段、图形观察、指定 Launch 参数与调试，区别于知识题。 |
| 12 答案定位 | 通过 | answers.tex 的 12+10 题解通过 ref 定位，按正文顺序排列；开放实践有命令、输出或判断依据。 |
| 13 作者语言习惯 | 通过 | 保留原来的你/我们、首先/然后/不过、操作中的解释与轻松提醒；修正技术错误，不照抄错字或单位错误。 |
| 14 图片实际检查 | 通过 | 实际查看原版本截图、软件分层图和节点图；重绘两张青色中文矢量图，新 rqt 截图来自真实插件运行。独立图和正文尺寸均实际查看。 |
| 15 图片标记与引用 | 通过 | 检查后使用 ros2_arch_revised.pdf、ros2_node_revised.pdf、ros2_rqt_revised.png，正文与生成脚本的发布路径一致；旧图保留。 |
| 16 文件组织 | 通过 | 原 appendix_ros2.tex 改为 A_ros2_project.tex 并移到节点讲解后；完整工程与工程机制两部分职责清楚，项目按消息包/节点包组织。 |
| 17 包含与引用 | 通过 | main→core→project→engineering→review 顺序明确；README、OpenCV 调用说明同步。结构检查 29 个包含文件、91 个标签、45 个被引用标签无失效/重复/循环。 |
| 18 源码与格式 | 通过 | 短命令和配置整体排版，长实现按函数边界展示全部内容；图注、表格、标题映射和行号沿用本卷，章末题解编号不再带列表尾点。 |
| 19 实际运行 | 未完成 | Jazzy 的构建、通信、变体、Launch、日志、测试、真实 rqt 插件及 GDB 回调断点均通过；尚缺 CLion 图形断点和真实第二主机上的发现范围/恢复测试。Humble 未实测，只有版本文档核对。不能用同机不同域或 GDB 替代这两项。 |
| 20 编译与 PDF | 通过 | 从卷入口 XeLaTeX 编译至引用稳定，无缺文件、未定义引用、重复标签或越界。最终 179 页；实际检查目录物理页 4–5、正文 7–37、题解 162–165 及相邻章入口。没有修改共享模板。 |

## 核心能力覆盖

| 正文内容 | 随堂练习标签（省略 ex:v2-ros-）与判断 |
| --- | --- |
| 发行版、环境和命令 | setup：确认环境与 talker 包名，用帮助查启动语法。 |
| 架构与图 | graph：类型/发布者数、停止与重查；节点与话题关系。 |
| 发布订阅与 QoS | qos：反向可靠性组合，核对端点并解释能否收包。 |
| 接口生成 | message：新增 distance，重建依赖并查询定义。 |
| 定时器与标准消息 | timer：500 ms、频率约 2 Hz，区分计数、时间戳和坐标系标识。 |
| 服务 | service：查看请求/响应类型与服务端，说明同步请求的适用场景。 |
| 完整收发与图形观察 | reply：armor_found 的对应回复、停止/恢复发布端，说明旧显示不代表持续收包。 |
| 环境、域、发现与中间件 | domain：同机两域隔离、Cyclone 通信及恢复；第二主机部分仍待补。 |
| ament/colcon/rosdep | ament：修改测试阈值，检查依赖、测试结果与安装资源。 |
| Launch | launch：blue 与条件观察进程，修正固定 red 路径，解释参数和完整话题。 |
| 日志 | log：1 秒限流与 5 Hz 消息、WARN 下日志减少、独立日志目录。 |
| IDE 与产物 | ide：独立构建、断点、旧安装与重新构建/加载；CLI 已验证，CLion GUI 待补。 |

## 运行证据与环境边界

验证环境为 Distrobox ubuntu2404：Ubuntu 24.04.5、Jazzy、GCC 13.3.0、CMake 3.28.3、rclcpp 28.1.22、Fast DDS RMW 8.4.4、Cyclone RMW 2.2.4、rqt_publisher 1.7.3 与 rqt_topic 1.7.5。本章需要的软件已安装；初始化/更新原先未配置的 rosdep，安装检查未再需要额外 ROS 包。没有把缺少真实设备记作“不适用”。

- `scripts/verify_ros_examples.py` 在临时工程副本执行 76 条命令/后台结果记录，证据为 [runtime.json](evidence/volume-2-chapter-1-runtime.json)。三个包 Debug 构建成功，colcon 报告 3 个测试，无失败/跳过；产物和 compilation database 可用。
- 字符串回调输出 I can hear:armor_found；自定义消息含 camera_link、yaw 0.25 与成功标志。原定时器约 1 Hz，500 ms 变体约 2 Hz；新增 distance 3.5 后重新生成接口并收到字段。停止节点后无回复。
- best_effort→reliable 实际报告不兼容且没有消息；best_effort→best_effort 与 reliable→best_effort 收到 hello。同机域 76/77 隔离、同域恢复、Cyclone 通信与 AddTwoInts 两组和为 5 的调用通过。这里只测试了同机域隔离，没有测试物理第二主机。
- Launch 的 red/tracking、blue/字符串 true、条件观察进程、观察退出后心跳继续均有证据；临时修正 blue 的观察路径后收到对应消息。日志阈值不改变 5 Hz 发布，限流变体与独立目录有实际输出；测试阈值、ament_auto 独立构建和安装资源通过。
- 独立 CMake Debug 产物改为 from_debug 时旧安装仍为 ready，重新 colcon 构建/加载后恢复一致。最初运行记录中的 GDB 断点位于构造函数；另行补做的 [callback-gdb.txt](evidence/volume-2-chapter-1-callback-gdb.txt) 明确命中 pub_->publish 所在 lambda 回调，栈含 GenericTimer 与 Executor。脚本已改为回调断点并核对调用栈；没有将 CLI 调试当作 CLion 图形操作。
- `scripts/verify_ros_gui.py` 使用已安装的真实 rqt Publisher/Topic 插件，在独立 Xvfb 窗口中运行，操作插件控件并通过 DDS 收发。send 显示真实回复，my_msg 显示真实字段；停止发布端计数为 0，重启为 1，重新勾选监视后回复恢复。证据 [rqt.txt](evidence/volume-2-chapter-1-rqt.txt)、[真实截图](evidence/volume-2-chapter-1-rqt.png)。这是插件与图形窗口实测，没有声称是在用户 Niri 桌面点击了完整 rqt 菜单。
- 当前 ros2interface 0.32.12 的后缀匹配会把 Image 查询误指向 CompressedImage。实际检查安装源码、Image.msg 和 Python Image 字段，证据 [image-interface.txt](evidence/volume-2-chapter-1-image-interface.txt)。正文在查询旁给出直接读取对应消息文件的办法；实际消息类型没有改变。

版本与策略核对使用 ROS 官方源文档：[Jazzy/Noble 安装](https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Installation/Ubuntu-Install-Debs.rst)、[Humble/Jammy 安装](https://raw.githubusercontent.com/ros2/ros2_documentation/humble/source/Installation/Ubuntu-Install-Debs.rst)、[发现范围与静态对端](https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Tutorials/Advanced/Improved-Dynamic-Discovery.rst)、[QoS 与兼容性](https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst)。Jazzy 的 LOCALHOST 需同时考虑静态对端；旧 ROS_LOCALHOST_ONLY 说明只用于 Humble 路径，域编号不等于认证。

## 图片、引用和版面整理

| 原文件 | 正文文件 | 调整与检查 |
| --- | --- | --- |
| images/ros2_logo.png | 章首发行版表 | 原图是历史版本列表，实际查看后用本章两种环境的表格替代，旧资产保留。 |
| images/ros2_arch.png | images/ros2_arch_revised.pdf | 中文青色矢量分层，保留客户端与中间件关系，补 rcl/rmw 和本章两种 DDS；图是教学边界，并非全部 SDK 列表。 |
| images/ros2_node.png | images/ros2_node_revised.pdf | 明确一对多话题、服务请求和响应方向，补节点/执行器/组件的维度说明，箭头不穿过无关模块。 |
| 无（新增真实运行截图） | images/ros2_rqt_revised.png | 真实插件显示与消息内容；采集时增大原生字体，未修改输出字段。正文说明看 receive/send/my_msg，不凭截图的 unknown Hz 判定速率。 |

`chapters/appendix_ros2.tex` → `chapters/A_ros2_project.tex`，由章末移到节点和消息旁边。全部活动调用方已更新；OpenCV 中旧“附录”提示改成引用实际节。图生成脚本默认候选路径，实际查看后才发布 revised。短代码使用独立段落的整体代码块，长实现保留完整行号范围；没有以删代码或缩小到不可读的字号解决分页。

编译保留模板已有 Fandol 粗体/斜体替代提示，PDF 实际检查可读。卷一主 CMake 引用未变化，共享模板未变化；结构脚本补上 lstinputlisting 选项标签识别后，复查卷一第三章与卷二第一章路径和题解定位均通过。下一章继续按独立提交整理，未完成环境测试持续记录。
