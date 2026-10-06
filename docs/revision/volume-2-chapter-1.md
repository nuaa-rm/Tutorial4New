# 卷二第一章：ROS2 开发与工程实践修订记录

本章保留原来的“先建节点，再解释通信，最后整理工程”讲解线。语言参照原 11/12/13.tex，用连贯段落带着读者操作，随步骤解释环境、名字和结果，不把正文改成检查清单。20 项中 19 项通过，第 19 项仍有真实环境验证缺口；本章及全书尚未全部验收。

## 内容、项目与题解

- 默认环境改为 Ubuntu 24.04 / Jazzy，同时给出 Humble 22.04 的包名、环境脚本与发现范围差异。说明 Distrobox 中共享源码与容器内工具链的关系；不把 Jazzy 实测写成 Humble 实测。
- 把原附录完整工程移到节点和接口旁边，形成 `examples/ros2/basic-interfaces-demo` 的两个完整包。正文直接引入消息、头文件、实现、入口、清单与构建文件，并解释句柄存活、执行器、时间戳、接口生成和依赖顺序。
- 复用 `examples/ros2/training_tools`，完整展示构建、测试、参数、两份 Launch、日志和调试。新增独立 `cmake/Auto.cmake` 用于比较 ament_auto；没有更改卷一引用的主 CMakeLists.txt。
- 补充 QoS 不兼容与恢复实验、真实 rqt 插件观察、带字段变体的接口重建、安装产物与独立 IDE 构建的区别。纠正 QoS 保证、Vector3/Point、组件/执行器和计数等于时间等容易误解的表达。
- 13 道随堂练习与 10 道章末题均有标签、引用题解和可观察的判断标准。补测后新增一题核对头文件解析参数，不重复原 IDE 产物题。保留章首、阶段归纳、章末知识地图和操作验收。

## 20 项检查

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main.tex 第一章 introduction 包含可操作目标、基础约一周与工程 2–3 天学时、卷一前置和卷三集成边界。 |
| 2 核心示例 | 通过 | A_ros2、project、engineering 的环境/图、发布订阅/QoS、定时器/接口/服务、完整工程/rqt、依赖/Launch/日志/调试与头文件参数补充示例有前提、操作与判断。 |
| 3 复杂概念项目 | 通过 | basic-interfaces-demo 与复用的 training_tools 均有完整源码、构建文件、清单、配置和 README；新增 header_flags.py 复用其真实数据库，不另造框架或工程。 |
| 4 正文展示项目 | 通过 | 两个工程的目录、完整核心代码和行为配置直接引入；按执行顺序讲接口生成、收发回调、安装、参数覆盖、命名空间/重映射与进程事件。header_flags.py 的45行完整分为1–22和23–45行展示，讲清提取、路径转换和限定片段的作用。 |
| 5 语法与参数 | 通过 | ros2、colcon、rosdep、Launch 与日志命令有通用形式或参数解释，说明终端环境、工作目录、替换名字、两发行版条件与 GUI 前提。 |
| 6 随堂练习 | 通过 | 13 个 exercise 覆盖关系见下表，QoS、回复观察与头文件解析参数有独立任务，其余相邻知识合并但能力不遗漏。 |
| 7 难点归纳 | 通过 | 包/节点/话题、QoS、消息语义、域/发现范围/中间件、构建安装/Launch、IDE 产物均有 conclusion 或明确对比表。 |
| 8 易错提示 | 通过 | 混加载发行版、回调生命周期、参数类型、静态对端、旧进程/daemon、环境继承、遗漏安装、日志级别与工具接口查询问题均有说明；使用独立工作空间避免覆盖。 |
| 9 本章小结 | 通过 | A_ros2_review 用功能包、通信闭环、构建启动观察与排错串联知识，区分要练熟和按项目查询的内容。 |
| 10 章末习题 | 通过 | 10 题覆盖核心概念、环境、QoS、接口、服务、发现、Launch、日志与新旧产物，包含基础、提高、实际运行任务。 |
| 11 本章验收 | 通过 | 5 项现场操作检查不同输入、增加接口字段、图形观察、指定 Launch 参数与调试，区别于知识题。 |
| 12 答案定位 | 通过 | answers.tex 的 13+10 题解通过 ref 定位，按正文顺序排列；开放实践有命令、输出或判断依据。 |
| 13 作者语言习惯 | 通过 | 保留原来的你/我们、首先/然后/不过、操作中的解释与轻松提醒；修正技术错误，不照抄错字或单位错误。 |
| 14 图片实际检查 | 通过 | 实际查看原版本截图、软件分层图和节点图；重绘两张青色中文矢量图，rqt 和新增 CLion 回调截图来自真实窗口。原图与正文实际尺寸均查看，CLion 使用 Maple Mono NF CN。 |
| 15 图片标记与引用 | 通过 | 检查后使用 ros2_arch_revised.pdf、ros2_node_revised.pdf、ros2_rqt_revised.png 和 ros2_clion_revised.png，正文与生成脚本的发布路径一致；旧图保留。 |
| 16 文件组织 | 通过 | 原 appendix_ros2.tex 改为 A_ros2_project.tex 并移到节点讲解后；完整工程与工程机制两部分职责清楚，项目按消息包/节点包组织。 |
| 17 包含与引用 | 通过 | main→core→project→engineering→review 顺序明确；README、OpenCV 调用说明同步。当前结构检查 29 个包含文件、315 个标签、262 个被引用标签无失效/重复/循环。 |
| 18 源码与格式 | 通过 | 短命令和配置整体排版，长实现按函数边界展示全部内容；图注、表格、标题映射和行号沿用本卷，章末题解编号不再带列表尾点。 |
| 19 实际运行 | 未完成 | Jazzy 的构建、通信、变体、Launch、日志、测试、真实 rqt 插件及 GDB 回调断点均通过；CLion 实际构建/运行/回调断点、参数与默认值变体、colcon 安装对照、编译数据库导入/源码编译/头文件跳转完成。后续实际补齐选定外部头文件的解析参数，rclcpp.hpp 诊断15→0→15→0，保留node.hpp的10条unused-include警告，脚本与备份分支实测通过。真实第二主机上的发现范围/恢复仍未完成，Humble 未实测。不能用同机不同域替代第二主机。 |
| 20 编译与 PDF | 通过 | 从卷入口 XeLaTeX 编译至引用稳定，无缺文件、未定义引用、重复标签或越界。最初全卷179页与CLion图补测270页的检查保留，当前272页。新增代码/练习后实际查看物理页4–5、36–42、247–250；代码加行号后两次编译稳定，再看37–39页及完整38页。题解长路径越界已修正，没有修改共享模板。 |

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
| IDE 与产物 | ide：独立构建、断点、旧安装与重新构建/加载；CLI 与 CLion GUI 均实际验证；第二主机待补。 |
| 外部头文件参数 | header-context：include拼接、限定配置、错误源码路径拒绝输出；参数确实缺失时比较GUI前后诊断。 |

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

## CLion 图形补测（2026-09-29）

证据见 [clion-gui.json](evidence/volume-2-chapter-1-clion-gui.json)。使用与卷一相同的官方 CLion 2026.2.3 安装包和正常试用配置，在 ubuntu2404 内加载 Jazzy 与临时工作空间后启动；没有重置试用或修改个人 IDE 配置。测试源码为随书 training_tools 的临时副本。

- 实际 GUI 设置 Debug、独立 cmake-build-debug 和 `-DBUILD_TESTING=OFF`，缓存与界面相符，Build 完成。运行参数 `--ros-args -p text:=from_ide`；调试在 heartbeat.cpp 第 16 行发布回调暂停，text 与展开后的 msg.data 均为 from_ide。取消断点并继续后，独立 DDS 订阅收到三条 from_ide。
- GUI 清除参数覆盖，把默认 ready 改为 from_debug，保存、构建和运行后收到三条 from_debug；旧安装程序仍发三条 ready。随后 colcon 重建，实际 ros2 run 发三条 from_debug。GUI 恢复源码后与仓库字节一致，IDE 和重建后的安装程序都发 ready。每一阶段停止上一发布者。
- File → Open 实际选择 colcon 的 compile_commands.json，再点击 Open as Project；Build 显示 successfully imported。Ctrl+B 从源码跳转至 `/opt/ros/jazzy/include/rclcpp/rclcpp/rclcpp.hpp`，源码 Recompile 完成。JSON 中包含真实 Jazzy 的 rclcpp/std_msgs 等 include 路径。
- **初次补测的索引限制**：外部 rclcpp.hpp 中出现15条clangd的子头文件file not found诊断，源码本身只有一条警告、实际编译成功。重新载入数据库、改变工程根目录、关闭重开头文件均未消除。临时XDG中只指定clangd数据库的配置也无界面效果，随后停用；初次记录没有禁用诊断或把成功编译当作索引正常。下面的后续补测通过实际解析命令找到缺失参数，并完成选定头文件的修复，初次失败证据仍保留。
- 截图控制器最初把以连字符开头的 CMake 参数当作 xdotool 选项而退出；增加 `--` 后恢复同一 IDE 配置并完成测试。File chooser 的逐键路径输入触发树搜索，改用自身 Xvfb 剪贴板一次粘贴后正确选中文件。首版订阅器只停止 ros2 run 包装进程，发现残留的临时 heartbeat 后核对 exe 并终止；修正为停止自身进程组，后续恢复测试无残留。失败与恢复均保存在证据中。
- 读取已配置的 SSH 别名 orin，以 BatchMode 和 5 秒超时尝试只读检查，退出 255：nvidia 主机名无法解析。没有获得第二台物理主机的 ROS 验证结果，没有运行机器人或扫描未知地址。

新增真实图 `images/ros2_clion_candidate.png` → `images/ros2_clion_revised.png`：编辑器与控制台为 Maple Mono NF CN，原始像素不改写，只以 LaTeX trim 聚焦回调与变量。先实际查看候选图及 PDF 页 35–38、246–247，再改为 revised；改名后的目录、正文、相邻章与题解再次查看。没有改名或移动任何 tex 文件、项目源码或共享模板。

补测结束后实际退出 IDE 并停止自身 Xvfb；核对临时安装目录的 IDE/clangd、临时工作空间 heartbeat 和本次 Xvfb 匹配进程为空。

## 外部头文件解析参数补测（2026-09-29）

证据见 [clangd-context.json](evidence/volume-2-chapter-1-clangd-context.json) 和 [实际解析命令](evidence/volume-2-chapter-1-clangd-commands.txt)。继续使用同一正常试用配置与独立Xvfb，没有重置试用、修改个人IDE配置或系统ROS头文件。

- GUI重启后复现rclcpp.hpp的15条错误。临时启用clangd详细日志，实际ASTWorker命令中heartbeat.cpp带27个ROS include路径，外部rclcpp.hpp却只带系统头文件路径。底部显示源码上下文不等于这些参数真正传入clangd。
- 把选定源码的include路径和宏作为限定的CompileFlags.Add片段后，rclcpp.hpp实际变为0错误；停用后重开标签为15，恢复随书脚本生成的片段后又为0。Problems截图分别保存，诊断一直开启，原始像素未修改。
- 多头文件片段只匹配rclcpp.hpp和node.hpp。实际从前者的子include跳转到后者，后者0错误、10条Possibly unused #include directive警告；保留这些警告，未宣称任意库的全部头文件都正常。
- header_flags.py实际读取真实Jazzy数据库，单/双头文件片段一致；不存在的源码退出2且标准输出为空。备份并追加已有配置的分支实际执行，备份与原文件字节一致、追加后保留原前缀。arguments形式、相对源码路径与含空格的相对include路径也实际通过，见6条运行/核对记录。
- 独立clangd对照先遇到安装包默认resource目录缺少stddef.h，返回3和2错误；仅query-driver仍不足。指定GCC标准头文件resource目录后为0错误。这个对照不代替GUI修复，GUI另有实际命令和画面。
- 本次Ctrl+W实际扩展选区，没有关闭标签；之后用标签关闭按钮，日志确认fileClosed/fileOpened。Registry第一次单击/F2仍进入搜索而未改变0，改为双击Value后实际设2，采集结束恢复0并清除临时trace分类。源码仍与仓库字节一致，实际退出IDE后核对自身测试进程无残留。

正文在原编译数据库示例旁展示完整45行脚本、生成片段与备份追加命令，解释为什么外部头文件使用用户配置、为什么只匹配指定文件、更新依赖后为何要重查；新增随堂练习与题解。没有新增或重绘教材正文图片、改名或移动tex文件。结构检查13道随堂练习、10道章末题，引用和题解定位通过；最终卷二272页，受影响代码与题解均实际查看，无越界或引用错误。第二台物理主机仍未就绪，本章第19项继续保留未完成。

## Humble 安装教程写入正文（2026-10-05）

按用户要求，把 `A_ros2.tex` 原来仅指向网站的安装段落展开成书内可操作的 Ubuntu 22.04 / Humble 教程。依次说明系统与架构检查、UTF-8、Universe、官方 ros2-apt-source 配置包、系统更新、desktop 与开发工具安装、环境加载和 C++ talker / Python listener 收发。安装命令依据官方 Humble 文档及其包含文件核对；长下载地址拆成变量，`jammy` 明确对应已检查的 Ubuntu 22.04。保留来源链接与核对日期，新增安装阶段小结，扩展原环境练习并同步 `answers.tex`。没有新增题号或演示项目。

完整章节检查沿用本记录及 [Zenoh 补充验收](ros2-zenoh-20261003.md) 的既有内容证据，重新核对当前入口、资源、练习与答案；本轮验证范围为安装段落、对应题解及其排版。仍为 19 项通过、1 项未完成，没有不适用项。

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | `main.tex` 第一章保留可验证目标、学时及 Ubuntu 22.04 / Humble 和卷三边界。 |
| 2 核心示例 | 通过 | 既有章节示例保留；安装新增连续操作步骤作为等效示例，交代终端、系统、权限和各阶段结果；环境示例包含双终端收发。 |
| 3 复杂概念项目 | 通过 | 复用本章 basic-interfaces-demo、training_tools、image-path-demo；安装验证使用官方随 desktop 安装的示例，无需另建项目。 |
| 4 正文项目讲解 | 通过 | 既有完整源码引入与工程讲解保留，本轮未改动项目文件；安装说明解释软件源包、开发工具和两端程序的作用。 |
| 5 语法与参数 | 通过 | 当前安装说明给出系统、架构、编码、同一终端变量、jammy 条件、环境脚本及 ROS2 命令形式。安装部分 9 个 Shell 代码块通过 `bash -n`，未执行其中安装命令。 |
| 6 随堂练习 | 通过 | 全章 18 题；`ex:v2-ros-setup` 增加发行版与实际收发记录，其余既有覆盖不变。 |
| 7 难点归纳 | 通过 | 新增安装阶段 conclusion，区分安装软件与加载当前终端环境；既有通信、工程及内存路径归纳保留。 |
| 8 易错提示 | 通过 | 安装前提示先更新 Ubuntu 22.04 系统包并阅读 apt 变更；说明容器边界、下载失败、UTF-8、多个发行版及 Bash/Zsh 配置。 |
| 9 本章小结 | 通过 | `A_ros2_review.tex` 保留功能包、通信闭环、工程排错与图像链路知识地图。 |
| 10 章末习题 | 通过 | 14 题保留基础、提高、实践及大图像链路任务，未改变题量与覆盖。 |
| 11 本章验收 | 通过 | 原工作空间、节点、接口、Launch、IDE、RMW、借出与真实相机现场任务保留。 |
| 12 答案定位 | 通过 | 18 道随堂练习和 14 道章末题均有引用题解；环境练习答案同步发行版、启动帮助与消息序号判断。 |
| 13 作者语言习惯 | 通过 | 以你/我们随操作解释原因和结果，官方命令按当前阅读顺序组织，保留章节原有讲解风格。 |
| 14 图片实际检查 | 通过 | 本章图片均已标记 `_revised`；内容和样式未修改，按技能规则跳过重复整理，复查安装段落之后的架构图位置。 |
| 15 图片标记与引用 | 通过 | 既有图片标记和生成路径未改，结构检查确认资源存在；本轮没有新图片。 |
| 16 文件组织 | 通过 | 安装教程仍在 `A_ros2.tex`，题解仍在卷末 `answers.tex`；没有重命名、移动或重复包含。 |
| 17 包含与引用 | 通过 | 当前入口 32 文件、332 标签、277 被引用标签；包含路径、资源、标签唯一性、引用和题解定位检查通过。 |
| 18 源码与格式 | 通过 | 沿用 tbash、minipage、example、exercise、conclusion；三处 Needspace 使安装步骤与命令、相邻节点查询示例的介绍与代码保持相邻。 |
| 19 实际运行 | 未完成 | 本轮未在全新 Ubuntu 22.04 环境执行安装或双终端收发；官方文档与 Bash 语法核对不能替代实测。既有真实相机和跨机器等验证缺口仍保留。 |
| 20 编译与 PDF | 通过 | 从卷二入口 XeLaTeX 编译至编号和引用稳定；实际检查安装正文、相邻架构页和环境练习题解，无新增越界、缺文件或未定义引用。最终页数与复查页见下面的编译结果。 |

官方依据：[Humble 安装主文档](https://github.com/ros2/ros2_documentation/blob/humble/source/Installation/Ubuntu-Install-Debs.rst)、[UTF-8 设置](https://github.com/ros2/ros2_documentation/blob/humble/source/Installation/_Ubuntu-Set-Locale.rst)、[软件源配置](https://github.com/ros2/ros2_documentation/blob/humble/source/Installation/_Apt-Repositories.rst)、[系统更新](https://github.com/ros2/ros2_documentation/blob/humble/source/Installation/_Apt-Upgrade-Admonition.rst)。官方网页本轮返回访问错误，因此读取同一官方仓库的 Humble 文档源码和包含文件进行核对。

编译结果：整卷最终 **295 页**，已更新 `02-专项技术栈/main.pdf`。实际检查物理页 7–12 和 267，覆盖安装正文、相邻节点查询示例及环境练习题解；最后一遍目录与引用文件的 SHA-256 均与上一遍一致，所选正文页 7–10 和题解页 267 的像素与已查看版本一致。没有 Overfull、缺失资源、未定义引用、重复标签或重跑提示；沿用模板已有字体替代提示，没有新增文献调用。PDF SHA-256：`4c0afe6aeb7264fb08e029b0f7324c67fe4436c4f68c79ef98a79172e8507732`。本轮没有更改已有图片、共享模板或项目源码。

## RMW 安装与配置教程（2026-10-05）

进一步展开 engineering 中“切换中间件与进阶变量”：三种实现的安装和切换、两份完整 DDS 网卡 XML 与字段解释、Zenoh 默认发现和 JSON5 的 session/router、跨机器连接与恢复。新增同卷 `rmw-config-demo` 和两道随堂题及题解。详细的逐项验收、官方来源、正文补丁与运行日志见 [本次修订记录](ros2-rmw-config-20261005.md)。

现有 Ubuntu 22.04 / Humble 容器的六组本机收发均通过；完整章验收仍为 19 项通过、1 项未完成，保留安装/源码构建与物理第二主机等未测边界。整卷最终 **301 页**，引用与目录稳定；已实际检查物理页 26–33、274–275，无新增越界、缺字或引用问题，已更新 `02-专项技术栈/main.pdf`。

## Launch 详细讲解（2026-10-05）

按用户参考进一步展开 engineering 的 Launch 节，沿用原章口吻与 training_tools 心跳工程，补充单节点、配置/参数、组合/条件、分组命名空间、事件与真实就绪、OpaqueFunction 和排障。新增三份启动文件、三道练习及题解，扩展原组合启动练习，同步示例 README。详见 [本次修订记录与逐项检查](ros2-launch-20261005.md)。

现有 Ubuntu 22.04 / Humble 容器内 17 项核验通过（16 项 Launch 检查及构建/ament 测试），含练习变体与失败分支；测试仅修改临时副本，程序均已退出，容器恢复原停止状态。完整章验收仍为 19 项通过、1 项未完成，保留物理相机与第二主机等既有现场缺口。整卷最终 **308 页**，引用与目录稳定；实际检查物理页 37–48、281–283，已更新 `02-专项技术栈/main.pdf`。没有新增越界、缺字、未定义引用或重复标签，图片与共享模板未修改。

## RMW 安装与配置后移（2026-10-05）

环境小节现在仅简述 `RMW_IMPLEMENTATION` 的切换、重启和恢复；安装、DDS XML、Zenoh JSON5/router 与环境恢复移至大图像链路的中间件选型小节，再进入图像对照和零拷贝。两道配置题及题解按新顺序排列，示例 README 指向同步。结构、Shell 语法与题解顺序检查通过；整卷 307 页，已复查物理页 26–27、49–57、281–284 并更新 PDF。详见 [顺序调整记录](ros2-rmw-config-20261005.md#调整讲解顺序2026-10-05)。

## 图形化观测工具与完整演示（2026-10-06）

在基础工程之后补充 rqt Plot/Image View、RViz2 的 TF/位姿/轨迹/Marker，以及 Foxglove 的安装连接、字段路径函数、两点测量、二维与枚举标注、原生三维实体和 MCAP 回放。新增共用合成数据项目、两张真实截图、6 道随堂题和 2 道章末题及题解；1.4 小结编号保留。完整修改与逐项检查见 [本次记录](ros2-visualization-20261006.md)。

首轮 Humble 的九路消息、参数删除恢复、rqt/RViz 显示、桥接 CDR、约 12 秒 MCAP 的录制/读回及 ROS 回放通过。当时 Foxglove 安装与登录后的面板交互未实测，既有物理相机/多机缺口保留，完整章仍为 19 项通过、1 项未完成。首轮整卷 325 页，新增正文在书内第 19–34 页；目录、章首、新内容及对应题解、小结与验收均已实际检查。

## Foxglove 登录后实测与时间戳提醒（2026-10-06）

登录后实际验证 FoxQL、Header stamp、Plot/XY 测量、图像同步与 50 ms 偏移失败恢复、ROS/原生三维图形、枚举接口构建及 `1 (TRACKING)` 显示、布局保存恢复、MCAP 播放暂停和时间线/曲线定位。新增五张真实截图与五份可恢复面板 JSON。按用户提醒，在正文、题解及示例 README 中强调有效 `header.stamp` 优先，检测结果沿用输入图像时间，解释无 Header 信号与精确相位比较的区别。详见 [补测记录](ros2-foxglove-20261006.md)。

全新桌面安装、3D Alt 吸附、部分文件下载及本地文件选择器仍未完成；本次客户端 MCAP 回放实际使用本机 HTTP remote-file 路径。物理相机/多机缺口保留，完整章仍为 19 项通过、1 项未完成。最新整卷 **328 页**，新增正文在书内第 19–36 页，1.4 小结仍在第 83 页；三遍编译及受影响页面实际复查通过，PDF 已更新，具体哈希与检查结果在本轮证据中。

## 目录层级细分（2026-10-06）

按用户要求，ROS2 正文 `section` 从 3 组细分为 11 组，`subsubsection` 从 22 个细分为 52 个，分别组织入门、接口、完整工程、两组观测工具、构建、Launch、日志与 IDE、中间件、组件与借出、性能实验。本章小结与验收现编号为 1.12 和 1.13。纸面目录仍保持原显示深度，使用更具体的 section 定位内容。

正文顺序、代码、图片、实验数值及 30+16 道题目保留；长示例按新主题边界拆分，跨节指引、长名称换行及标题分页同步调整。完整增量、分组与 20 项验收见 [目录层级细分记录](ros2-subsections-20261006.md)。本轮只验证结构与 PDF，既有现场运行验收缺口继续保留。

## 章名与建议学时调整（2026-10-06）

章名改为“ROS2 开发与工程实践”，同步题解、章节地图和示例说明。章首学时改为每天 2–3 小时，首次学习约 1.5–2 周，补齐进阶实验后完整学习约 2–3 周，包含示例与练习。“大图像链路：中间件与内存”及其子节用 `*` 标为进阶选读，可先跳到本章小结，遇到传输和性能问题时再回来；章末题与验收注明分阶段补做，全部任务保留。先修与实车集成边界保留；详见 [本轮修改与逐项检查](ros2-introduction-20261006.md)。
