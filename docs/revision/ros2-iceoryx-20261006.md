# Cyclone DDS / iceoryx 固定图像实测与教材补充

本轮将此前默认配置的 Cyclone DDS 对照扩展为显式 iceoryx 实测，并新增 `FixedImage.msg`。教材按“为什么需要固定布局 → 定义接口 → 配置共享池 → 两端借出 → 对照读数”展开，机器版本、失败过程与原始日志集中在本记录中。此前十行 RMW 数值完整保留。

## 已完成的修改

- `02-专项技术栈/chapters/A_ros2_image_path.tex` 新增“固定图像：用 iceoryx 交接共享样本”。正文展示完整固定接口、收发源码、Cyclone XML 和 RouDi 池配置，提供手动和自动运行步骤，以及接口差异表和五组参考数据。
- 复用 `examples/ros2/image-path-demo`，新增 `msg/FixedImage.msg`、`src/fixed_image.cpp`、`config/cyclone-iceoryx.xml`、`config/roudi.toml` 和 `compare_fixed.py`。CMake 同时生成 Frame/FixedImage，安装新程序与配置。
- `compare.py` 新增可选 `--cyclone-config`，默认对照继续清除隐式 DDS 配置。指定配置只影响本轮子进程。
- README、借出随堂练习与参考答案、章末小结和现场验收同步更新。旧结果页明确区分默认 Cyclone DDS 和新增 iceoryx 对照。
- 没有移动、重命名文件或修改共享模板。独立于本轮前已有工作区修改的完整差异见 [iceoryx.diff](evidence/ros2-iceoryx-20261006/iceoryx.diff)。

## 消息与交付路径的区别

| 项 | Frame 中的标准 Image | 本例 FixedImage |
| --- | --- | --- |
| 像素 | `std::vector<uint8_t>`，动态数组 | `std::array<uint8_t, 4665600>`，内嵌定长数组 |
| 其他字段 | Header、encoding 字符串、每帧宽高及步长；包装层带测量信息 | 两个 uint64 测量字段，宽高与通道数为类型常量 |
| 尺寸与格式 | 运行时可改变 | 1440×1080 BGR8，紧密排列，更改时重新生成接口 |
| 普通发布 + iceoryx | 序列化到共享块，接收端恢复动态消息 | 将应用端固定结构复制进共享块，接收端借读原始样本 |
| 借出发布 + iceoryx | 本轮 Image 发布能力为 false | 发布端直接填充共享样本，订阅端回调内借读 |
| 工具与时间语义 | 标准图像工具可接收，保留 ROS 时间戳与坐标系 | 需适配成标准 Image 并复制、补元数据；sent_ns 是单机单调测量时刻 |

固定长度是类型属性。反复用同一分辨率填充动态 Image，不会把它变成固定长度消息。给动态序列设容量上限也不等于内嵌固定数组。

共享内存传输和应用消息借出要分开判断。本轮实际证明标准动态图像能通过 iceoryx 共享块交付，同时它不能走本例的消息借出接口。[Humble 的 rmw_cyclonedds 说明](https://github.com/ros2/rmw_cyclonedds/blob/humble/shared_memory_support.md)给出固定/动态类型的处理区别和 QoS 条件；本例 QoS 是 best_effort、KeepLast(5)、volatile、automatic liveliness、默认无限 deadline。

接收端使用 `const FixedImage &`，只在回调内访问。为这两个独立实验进程局部设置 `ROS_DISABLE_LOANED_MESSAGES=0`，遵循 [Humble rclcpp 的订阅端实现说明](https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/subscription_base.cpp)。不把引用或 cv::Mat 视图保留到回调外。

## 实测环境与构建

实际环境是 Ubuntu 22.04 / ROS 2 Humble 的 `ubuntu2204` Distrobox，网络、IPC 和 PID 与宿主共享。宿主为 Arch Linux；本轮使用临时工作空间 `/tmp/tutorial4new-iceoryx-20261006-ws`，没有改原有 ROS 工作空间或个人 DDS 配置。

| 包 | 实际安装版本 |
| --- | --- |
| ros-humble-cyclonedds | 0.10.5-2jammy.20260226.013234 |
| ros-humble-rmw-cyclonedds-cpp | 1.3.5-1jammy.20260907.205235 |
| ros-humble-iceoryx-binding-c | 2.0.5-1jammy.20260226.012512 |
| ros-humble-iceoryx-posh | 2.0.5-1jammy.20260226.011738 |
| ros-humble-rclcpp | 16.0.21-1jammy.20260907.213403 |

`libddsc.so` 实际链接 iceoryx binding、posh、hoofs 和 platform，`iox-roudi` 已安装。本轮未安装系统软件。环境与默认探测见 [environment-and-default-probe.log](evidence/ros2-iceoryx-20261006/environment-and-default-probe.log)。

源码复制到独立工作空间，使用 Release 构建。新增消息生成及可执行程序编译通过，最终增量构建用时 5.76 s，见 [build.log](evidence/ros2-iceoryx-20261006/build.log)。安装后的消息查询见 [interface-and-processes.log](evidence/ros2-iceoryx-20261006/interface-and-processes.log)。固定对象 sizeof 为 4,665,616 字节，像素为 4,665,600 字节。

RouDi 分配约 65.7 MB 管理段与 167.9 MB 数据段，图像池为 32×5 MiB，小块另计。`/dev/shm` 约 32 GiB，memlock 为 8192 KiB。本轮 RouDi 在该额度下正常创建池，不能套用此前 Zenoh 共享池的锁定内存行为。实际池创建见 [roudi-matrix.log](evidence/ros2-iceoryx-20261006/roudi-matrix.log)。

## 运行结果

默认发布端探测 Float64/Image 为 0/0，启用 XML 并启动 RouDi 后为 1/0。显式启用的输出见 [loan-probe-iceoryx.log](evidence/ros2-iceoryx-20261006/loan-probe-iceoryx.log)。固定接口的发布和订阅能力为 1/1。

低频完整检查：10 Hz、20 帧，逐字节确认每帧像素都等于序号对 256 取模的值，接收 20/20、bad_frames=0。两个进程前三帧对应同一共享对象 `/dev/shm/mijiao` 的相同设备、inode 与偏移，虚拟地址不同。证据见 [fixed-full-check/results.json](evidence/ros2-iceoryx-20261006/fixed-full-check/results.json)。

随后五组各重复三轮。共同条件为 1440×1080 BGR8、250 Hz 目标、每轮 1000 帧、best_effort、深度 5、两个进程、无算法工作与额外订阅者，发布完成后留两秒排空。每轮延迟从填充完成后、调用 publish 前计到接收回调入口；发送频率包含填充与分配成本。表中各项分别取三轮中位数，不合并不同轮次的延迟样本。

| 接口与路径 | 发送 / Hz | 接收 / Hz | 接收比例 | P95 / ms | P99 / ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| 标准 Image，默认 DDS | 250.002 | 249.132 | 99.4% | 3.735 | 4.611 |
| 标准 Image，普通发布 + iceoryx | 250.036 | 250.213 | 100.0% | 1.668 | 2.242 |
| 固定图像，默认 DDS | 250.008 | 249.646 | 99.8% | 3.292 | 3.938 |
| 固定图像，普通发布 + iceoryx | 250.027 | 250.059 | 100.0% | 0.505 | 0.670 |
| 固定图像，借出发布 + iceoryx | 250.061 | 250.051 | 100.0% | 0.334 | 0.376 |

全部 15 轮 bad_frames=0，高速时检查首尾像素。固定借出组每轮接收 1000 帧，各轮前三帧共 9 对共享位置全部匹配；固定普通发布组的源像素在应用分配的内存中，与借读端的共享位置不同。原始数据分别位于 `dynamic-default/`、`dynamic-shm/`、`fixed-default/`、`fixed-shm-regular/` 和 `fixed-shm-loan/`，汇总见 [summary.json](evidence/ros2-iceoryx-20261006/summary.json)。

只在相同接口内比较默认/iceoryx 与普通/借出接口。标准 Image 使用原组件容器，固定消息使用独立执行程序，两个类型的元数据也不同，不能将跨类型的所有差值都归于某一次复制。记录顺序固定，每组重复三轮。本轮是同机合成通信实验，未接入物理相机，也没有把计时扩展至采集、Bayer 转换或识别。

## 直接跟踪共享块

除了能力输出与应用像素位置，还做了独立 10 Hz / 20 帧路径诊断。诊断库拦截当前安装版本实际调用的 `iox_pub_publish_chunk` / `iox_sub_take_chunk`，读取 Cyclone 的 `iceoryx_header`，记录共享对象、偏移、长度、状态和全负载 FNV-1a 校验值。声明依据是当前安装的 `/opt/ros/humble/include/dds/ddsi/ddsi_shm_transport.h` 与 iceoryx 2.0.5 C 头文件。

| 类型 | 发布 / 接收共享块 | 逐块相同位置与校验值 | Cyclone 数据状态 | 共享负载字节 |
| --- | --- | --- | --- | ---: |
| Frame（标准 Image） | 20 / 20 | 20 / 20 | 2：IOX_CHUNK_CONTAINS_SERIALIZED_DATA | 4,665,696 |
| FixedImage 借出 | 20 / 20 | 20 / 20 | 1：IOX_CHUNK_CONTAINS_RAW_DATA | 4,665,616 |

该诊断证明了标准 Image 实际使用 iceoryx 序列化共享块，也证明了固定图像原始样本交付。诊断逐字节计算校验值，会增加延迟，未混入性能表。源码见 [trace_iceoryx.c](evidence/ros2-iceoryx-20261006/trace_iceoryx.c)，匹配记录见 [trace-summary.json](evidence/ros2-iceoryx-20261006/trace-summary.json)，原始日志见 `trace-dynamic-shm/` 与 `trace-fixed-shm-loan/`。

## 手动命令、负例与清理

- 使用正文的已安装包路径、`ros2 run` 收发命令实际运行，低频完整检查为 20/20、bad_frames=0，两端正常退出。见 [manual-summary.json](evidence/ros2-iceoryx-20261006/manual-summary.json)。
- 同一共享内存配置下，`ROS_DISABLE_LOANED_MESSAGES=1` 让固定发布能力变为 0，程序明确退出 2。随后重新启用，正常完成完整图像检查。见 [fixed-disable-loan.log](evidence/ros2-iceoryx-20261006/fixed-disable-loan.log)。
- 首次配置 URI 使用 Path.as_uri 将中文编码成 `%E4...`，Cyclone 无法打开文件。改用 `file://` 加实际未转义路径后通过，两个记录器已修正。失败记录保存在 `uri-encoded-failure/`。
- 首次独立诊断从预加载库用 RTLD_NEXT 解析局部加载插件的符号失败，改成读取实际已加载库句柄后通过。失败记录保存在 `trace-local-symbol-failure/`，性能实验没有加载这个诊断库。
- 首次手动命令写 `rate:=10`，与声明的 double 类型不符。正文和 README 改为 `rate:=10.0`，重跑成功，失败记录保存在 `manual-integer-rate-failure/`。
- 各控制器只清理自己启动的进程组。RouDi 正常退出，初始、性能对照与诊断后的共享对象列表均与实验前相同，未删除已有 Fast DDS / Podman 共享对象。见 `shm-after-*.json`。
- 以实际 cgroup 检查容器，结束时仅剩入口与它的 sleep 子进程，见 `container-processes-before-stop.json`。容器从测试前的 exited(143) 启动，现已恢复 exited(143)。没有停止宿主机其他任务。

## 完整章节检查清单

沿用第一章现有基础、工程实践、图像链路、小结与验收，逐项复核。新增示例已实际完成构建和运行。完整章节的相机、跨主机以及其他未重跑示例仍按各自旧记录与设备验收处理，不能因此宣称全章现场运行验收全部完成。

| 项 | 状态 | 当前依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main.tex 第一章 introduction 包含目标、学时、Humble 主线及卷三边界，物理第 7 页已查看。 |
| 2 核心示例 | 通过 | 保留全章基础/工程示例，新增固定消息包含前提、完整源码、配置、运行步骤和结果判断。 |
| 3 复杂概念项目 | 通过 | 复用本卷 image-path-demo，新增固定接口及最小收发程序，构建与手动/自动运行均通过。 |
| 4 项目正文讲解 | 通过 | 正文新增文件职责、完整 FixedImage/fixed_image 源码、XML/TOML，与 CMake 实际安装对应。 |
| 5 命令与参数 | 通过 | 新命令说明 role、rate、publish-mode、verify-full 与配置；手动浮点参数已实际修正、验证。31 个 tbash 块语法检查通过。 |
| 6 随堂练习 | 通过 | 全章 23 道，借出题增加固定接口对照、像素、共享偏移、兼容性和有效期，覆盖新核心能力。 |
| 7 难点归纳 | 通过 | 固定/动态接口对比表、普通/借出发布五组表、内存路径阶段小结均保留，归纳各自边界。 |
| 8 易错提示 | 通过 | 类型属性、回调内 const 引用有效期、两端借出开关和跨进程地址转换在操作附近说明。 |
| 9 本章小结 | 通过 | review 将固定共享样本及接口代价纳入知识地图，物理第 77 页已查看。 |
| 10 章末习题 | 通过 | 原 14 题覆盖基础、提高与实践，借出和类型结论题继续对应新示例，物理第 77–78 页已查看。 |
| 11 本章验收 | 通过 | 原 8 项现场任务保留，第 7 项扩展固定图像全像素检查、两端能力、共享位置与接口区别，第 78 页已查看。 |
| 12 参考答案 | 通过 | 23+14 题均有可定位答案，借出题同步补充新机制、预期输出与生命周期，第 289–290 页已查看。 |
| 13 作者语言习惯 | 通过 | 从 Image 动态字段导入固定接口，连续讲类型、池、填充与借读、比较读数；版本与失败过程留在本记录中。 |
| 14 图片与图文 | 通过 | 沿用已标记数据路径图，原共享样本行与新增示例对应。本轮未修改图片。 |
| 15 图片标记及引用 | 通过 | 沿用 _revised 资产，无新增待整理图片；结构与资源引用检查通过。 |
| 16 文件组织 | 通过 | 新代码复用原示例目录，正文负责讲解，results 负责旧数据解读，review/answers 同步，详细证据在 docs。 |
| 17 包含与交叉引用 | 通过 | 32 个文件、339 个标签、282 个引用标签，未重复、失效或循环包含；新增小节/表标签可定位。 |
| 18 源码与版面格式 | 通过 | 全部核心源码引入与实测一致，关键配置完整；长标识符已可换行，短安装引导保持在同页。 |
| 19 示例实际构建运行 | 未完成 | 新增 iceoryx 示例及五组共 15 轮、低频直接诊断、手动/禁用恢复均通过；完整章的真实相机与其他未重跑项目仍未在本轮全部运行。 |
| 20 编译与 PDF | 通过 | 最终修改后连续两遍 XeLaTeX，313 页，交叉引用稳定；目录、引入文件、固定示例、两组数据表、小结验收与题解已查看。 |

检查结果为 19 项通过、1 项未完成。缺口属于完整章节的硬件/网络现场验收，新固定图像 iceoryx 实测已完成。

编译使用卷二 main.tex 的多文件项目入口，无缺文件、未定义引用、重复标签、缺字或重跑提示。目标新增的两处长标识符越界已消除。工程章节原有 2.87 pt 越界位于未改动的 408–409 行，字体替代提示沿用。本轮没有新增文献引用，系统未提供 Biber；未重新运行独立文献工具流程。

最终 PDF 与版面证据见 [pdf-check.json](evidence/ros2-iceoryx-20261006/pdf-check.json)、`pdf-contact-*.png`，源码静态结果见 [static-checks.json](evidence/ros2-iceoryx-20261006/static-checks.json)。
