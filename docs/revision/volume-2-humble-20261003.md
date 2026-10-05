# 卷二 ROS2 内容统一为 Humble（2026-10-03）

本次按用户要求，把卷二涉及 ROS2 的正文、命令、代码、答案和示例说明统一以 Ubuntu 22.04 / ROS2 Humble 为主，去掉正文与示例 README 中的 Jazzy 验证说明。既有原始运行证据保留在历史修订记录中，本次没有改写那些证据的环境或结果。

## 修改位置与接口核对

| 章节或文件 | 本次修改 |
| --- | --- |
| 第 1 章：A_ros2、A_ros2_project、A_ros2_engineering、main、answers | 安装与工作空间默认 Humble；本机通信使用 ROS_LOCALHOST_ONLY=1；恢复时取消该变量；去掉另一套发现范围变量和特定版本的查询工具问题；IDE 说明改为检查本机实际参数。 |
| 第 2 章：J_comm 与 stream-link-demo/README | ROS 桥接两终端加载 Humble；Distrobox 进入自己的 Ubuntu 22.04 容器。 |
| 第 4 章：B_opencv、B_opencv_review、两个 OpenCV 示例 README | Ubuntu 22.04 为默认环境；按本机查询版本；图像桥接的 roundtrip.cpp 与 bridge_node.cpp 均使用 cv_bridge/cv_bridge.h；包名与源码文档链接同步。 |
| 第 7 章：E_camera、E_calibration、calibration-lab-demo | 系统 Python 与 ROS 安装命令按 Humble；移除本项目不使用的 camera-info-manager-py 安装项；相机标定、消息定义链接指向 Humble；format_gamma.py 使用 OpenCV 4.5 可用的 COLOR_BayerBG2BGR，并在正文解释其与本例 RGGB 排列的关系；真实截图保持原像素，参考数值与实拍条件分别说明。 |
| 第 11 章：I_nav、I_nav_review、navigation-lab-demo、answers | Navfn 的插件标识改为 nav2_navfn_planner/NavfnPlanner；progress_checker_plugin 使用单个实例；移除 enable_stamped_cmd_vel；FollowPath 请求不设置 progress_checker_id；两个 action 结果不读取 error_code；用 action 状态与服务器日志判断结果。参数文件与客户端的正文引入范围同步，函数 finally 与清理语句保持同一代码段。 |
| 第 3、8、9、10 章的文字或 README | 删除不依赖 ROS 的数值项目中多余的 ROS 版本名，不改变其代码与数值实验。 |
| 根 README 与 7 个验证脚本 | README 明确 Humble 为教材基准；验证脚本使用 Humble 包路径、本机发现设置与 action 字段，并在需要 ROS 的入口检查 ROS_DISTRO。 |

涉及的 LaTeX 文件没有重命名或移动，没有修改共享模板。工作区原有的四方向、编者说明和封面改动保留；本次差异另从操作前副本生成，避免混入已有修改。

接口核对直接使用上游 Humble 分支：[安装基准](https://github.com/ros2/ros2_documentation/blob/humble/source/Installation/Ubuntu-Install-Debs.rst)、[Nav2 配置](https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/params/nav2_params.yaml)、[FollowPath](https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/FollowPath.action)、[ComputePathToPose](https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/ComputePathToPose.action)、[cv_bridge 头文件](https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/include/cv_bridge/cv_bridge.h)、[image_proc Launch](https://github.com/ros-perception/image_pipeline/blob/humble/image_proc/launch/image_proc.launch.py)、[标定器采样规则](https://github.com/ros-perception/image_pipeline/blob/humble/camera_calibration/src/camera_calibration/calibrator.py)。

## Ubuntu 22.04 实际运行

随后按用户要求创建了带 NVIDIA 支持的 ubuntu2204 Distrobox，安装 ROS2 Humble Desktop、ros-dev-tools、Cyclone DDS、OpenCV、相机标定/image_proc、Nav2、PCL 和数值计算依赖。官方 ros2-apt-source 1.3.0 配置 Jammy 软件源，rosdep 已初始化并更新。实际系统为 Ubuntu 22.04.5、Python 3.10.12、OpenCV 4.5.4、PCL 1.12.1、Nav2 1.1.20，完整包版本见 [环境记录](evidence/volume-2-humble-20261003-runtime/environment.json)。

直接执行 `distrobox enter ubuntu2204` 即可进入，Zsh 和 Bash 登录环境均自动加载 Humble。共享 Zsh 配置按容器名选择环境；原配置备份为 /home/mijiao/.zshrc.bak-ubuntu2204-20261003。新容器使用 Humble 默认 Fast DDS，并补齐 Qt 5 的 GTK 主题、Wayland 和图标支持；正常环境的按钮图标已恢复。

| 实测项目 | 结果与证据 |
| --- | --- |
| NVIDIA 驱动与设备 | RTX 3070 Ti Laptop，驱动 615.71.09；CUDA 驱动 API 实际创建上下文、分配显存并完成 1024 字节写入/读回。[GPU 记录](evidence/volume-2-humble-20261003-runtime/gpu.json) |
| NVIDIA OpenGL | 通过容器访问桌面显示，direct rendering 为 Yes，渲染器为 RTX 3070 Ti，OpenGL 4.6.0 NVIDIA 615.71.09。[输出](evidence/volume-2-humble-20261003-runtime/nvidia-opengl.txt) |
| ROS 基础与工程 | 76 条记录通过：colcon 构建/测试、自定义消息变更、频率、QoS、不同域、Cyclone DDS、服务、Launch、日志、GDB、安装目录与自动构建规则。[原始记录](evidence/volume-2-humble-20261003-runtime/ros.json) |
| 通信项目 | 30 条记录通过：真实 TCP、PTY、分片/粘包、长度/CRC 边界、迟到清理、故障恢复及 ROS 桥接。[原始记录](evidence/volume-2-humble-20261003-runtime/communication.json) |
| OpenCV 与 cv_bridge | 64 条记录通过：C++ 编译、数组与算法、变式、错误输入、图片保存、视频结束/退出、实际 ROS 图像字段、编码拒绝与图像窗口。[原始记录](evidence/volume-2-humble-20261003-runtime/opencv.json) |
| 相机软件项目 | 34 项通过：固定种子图片求解、独立照片验证、单位尺度、Bayer/Gamma、噪声/曝光、双目几何、CameraInfo、SetCameraInfo 持久化/重启与真实 image_proc 逐像素比较。[原始记录](evidence/volume-2-humble-20261003-runtime/camera.json) |
| 导航软件项目 | 40 项通过：栅格/PGM、最短路、BT、tf2、PCL、实际 Nav2 规划和控制。规划与跟随状态均为 4，123 个路径位姿、241 个速度样本，目标误差约 0.09963 m；不可达目标被拒绝。[原始记录](evidence/volume-2-humble-20261003-runtime/navigation.json) |
| rqt、标定 GUI 与 CLI | rqt 发布/监视与节点重启恢复通过；单/双目标定器完成 CALIBRATE、SAVE、COMMIT。双目保存的两侧 K/D/R/P 与消息一致，模拟基线约 0.11986 m；正文单/双目命令与校正图查看器均启动并实际显示图像。截图和结果见 [汇总](evidence/volume-2-humble-20261003-runtime/summary.json)。 |
| RViz | 实际启动、创建 OpenGL 上下文并显示网格，已查看截图。此项使用独立 Xvfb 软件渲染，NVIDIA 硬件 OpenGL 由上面一项单独验证；未接入机器人 TF。[窗口](evidence/volume-2-humble-20261003-runtime/rviz.png) |

五组软件验证共 244 条记录通过，另外完成 GUI、CLI、显卡与环境检查。相机输入是本项目生成的棋盘格图片，Nav2 使用简化底盘软件模型；第二主机、真实相机、底盘和传感器的现场验收仍未进行。

实际运行还修正了验证脚本的三个问题：OpenCV 版本改为核对本机系统库；独立显示明确设置 GTK 的 GDK_BACKEND=x11 并取消 WAYLAND_DISPLAY，按键先聚焦窗口；标定 SAVE 必须等压缩存档完整可读再复制，避免较大双目存档的写入竞态。修正前的失败日志单独保留，最终重测均通过。

## 逐项检查

检查覆盖第 1、2、3、4、7、8、9、10、11 章的完整教学结构。各章既有核心小节覆盖表和项目说明见对应的 volume-2-chapter-N.md；本次保留其示例、练习、归纳、题解和验收范围，只调整版本与必要的接口差异。下表每项对这些章节均适用，缺少运行条件的项目不记为通过。

| 检查项 | 状态 | 本次依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main.tex 保留各章可检查目标、学时、卷边界；第 1、11 章目标和基准同步为 Humble。 |
| 2 核心小节示例 | 通过 | 沿用各章完整例题与操作示例覆盖；修改的安装、环境、桥接、标定和导航示例仍包含前提、操作与结果判断。 |
| 3 复杂概念项目 | 通过 | 原 examples 项目继续使用；消息包、节点包、图像桥接、标定回放及 Nav2 软件模型的必要文件均保留。 |
| 4 正文项目讲解 | 通过 | 正文直接引入源码与配置；Nav2 参数文件及 client.py 的引入行范围随接口修改同步，核心代码无遗漏。 |
| 5 命令与参数 | 通过 | ROS 安装包、环境脚本、通信范围与可替换容器名统一；Humble action 的状态判断和日志定位明确。 |
| 6 随堂练习 | 通过 | 各章 exercise 保留；结构检查分别找到 13、8、8、12、13、10、14、11、11 道，全部有可定位答案。 |
| 7 难点归纳 | 通过 | 各章 conclusion 与对比表保留；环境加载、发现、图像编码、标定存档及导航接口的区别同步。 |
| 8 易错提示 | 通过 | 保留环境混用、解释器、软件源、文件覆盖、服务缺失、模拟与硬件条件等提示；取消让读者只替换版本名的说明。 |
| 9 本章小结 | 通过 | 各章 *_review.tex 的知识地图保留；导航小结使用 Humble。 |
| 10 章末习题 | 通过 | 各章 problemset 保留；章末题数量分别为 10、9、9、10、10、10、10、10、10，道题目与题解互相定位。 |
| 11 本章验收 | 通过 | 各章操作能力验收保留；OpenCV 与导航现场任务改为 Humble，仍要求真实输入输出和失败处理。 |
| 12 参考答案 | 通过 | answers.tex 的环境路径、发现恢复、头文件参数和 Nav2 状态说明同步；9 章题解覆盖检查通过。 |
| 13 作者语言习惯 | 通过 | 保留原操作顺序与连贯讲解；依读者当前环境说明操作，不反复插入维护环境的版本声明。 |
| 14 图片检查 | 通过 | 原图片已带 _revised，按技能跳过未变化的图；修改图注的 CLion 与单/双目标定截图另行查看原图和 PDF，未发现接口或图文矛盾。 |
| 15 图片标记与引用 | 通过 | 没有修改图片像素或重绘，沿用原标记和有效路径；实际截图未篡改。 |
| 16 文件命名与组织 | 通过 | 各章入口、正文/项目/工程/小结、examples 和 answers 的既有职责保留，无移动或重复项目。 |
| 17 包含与交叉引用 | 通过 | 实际入口包含 30 个文件，315 个唯一标签、262 个被引用标签；9 章检查均通过，PDF 无未定义引用。 |
| 18 源码与排版 | 通过 | Python 语法、YAML 与差异空白检查通过；代码引入与配置一致，已查看命令、源码、图注和题解页。 |
| 19 示例实际构建与运行 | 未完成 | 本次涉及的 Humble 软件项目已实际构建和运行：五组共 244 条记录通过，另完成 rqt、RViz、单/双目标定 GUI 与正文 CLI；grid.py 已在 SciPy 1.8.0 中运行。需要第二主机、真实相机、底盘和传感器的现场验收仍未进行，继续记为未完成；同机进程、模拟图片与软件底盘不外推为实机结果。 |
| 20 编译与 PDF | 通过 | 使用项目导出脚本的编译函数，在不含旧辅助文件的临时源码副本中编译到目录与引用稳定；最终 272 页，无缺图、未定义引用、重复标签或 overfull。此前 40 个物理页已查看，本轮实际复核变化的第 138、139 页；其余 270 页提取文字与上轮一致。 |

本次不新增结构要素、题目或教材插图，已有教学闭环继续保留。共 19 项通过、1 项未完成；本机 Humble 软件运行已完成，条目 19 保留的未完成部分是现场设备验收。新的窗口截图属于修订证据，没有替换教材原图。

## 验证证据与成品

最初阶段的静态接口、结构、离线检查及 PDF 结果保留于 [静态证据](evidence/volume-2-humble-20261003-static.json)，其中的待运行描述是安装容器前的状态。随后实际运行的结果、环境、源码散列、截图和最终 PDF 散列见 [运行汇总](evidence/volume-2-humble-20261003-runtime/summary.json)。Python 语法检查覆盖 111 个文件，差异空白检查通过。

编译使用临时源码副本，保留了仓库原有辅助文件，避免读取旧状态；副本中沿用本项目的模板、封面资源和字体。最终 PDF 更新到卷二 main.pdf，该生成物按原 .gitignore 忽略。完整的本次差异保存在 /tmp/tutorial4new-humble-20261003/humble-only.patch；新一轮安装日志、临时工作空间、回放数据、标定存档与 PDF 在 /tmp/tutorial4new-humble-runtime-20261003。原始历史修订证据的环境和结果没有改写。
