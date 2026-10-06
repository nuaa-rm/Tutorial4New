# 图像接口、借出机制与统一中间件比较

本轮取消 iceoryx 独立小节，把工具作用与类型条件放回借出消息部分。所有图像性能实验的条件、数据与解读集中在 `02-专项技术栈/chapters/A_ros2_image_results.tex`，Fast DDS、Cyclone DDS 与 Zenoh 都测试普通 Image 和定长 FixedImage。

## 正文调整

- `A_ros2_image_path.tex` 保留五个小节。1.3.4 开头明确变长 Image 不能直接借出中间件原始样本，再讲能力查询、本地分配回退、共享工具、定长接口及 Float64/Image 探测。
- iceoryx 与 Data Sharing、Zenoh SHM 在同一处介绍各自共享什么、RouDi 的作用以及类型、配置条件。按用户要求删除后面的专门手动测试、完整 fixed_image 程序和逐帧共享位置流程，完整诊断工具与旧实测证据继续保留在项目和 docs 中。
- FixedImage 接口与标准 Image 的字段、布局、工具兼容性差异提前说明。定长是类型条件，所用 Zenoh 实现对定长类型也不提供应用借出。
- 1.3.5 只引入统一测量目标并包含 results 文件。results 保留普通 Image 三种布局的十行原始数值，增加三种 RMW × 两类消息的默认配置与共享配置表，再讲慢处理队列。
- 练习、答案、章末小结与验收同步。章末第 13 题答案明确 loan_probe 借出并发布的是 Float64，Image 只用于能力查询。
- 未移动、重命名文件，main.tex 包含结构与共享模板不变。完整增量见 [unified.diff](evidence/ros2-image-unified-20261006/unified.diff)。此前 Cyclone 专项五行数值继续保存在 [iceoryx 实测记录](ros2-iceoryx-20261006.md)，由新统一表承担正文比较。

## 统一实测

项目新增 `src/image_benchmark.cpp` 与 `compare_images.py`，CMake 安装统一收发程序。模板节点使用同一份收发实现处理 Frame 包装的标准 Image 和 FixedImage，差异集中在两类接口的图像字段准备。

共同条件：Ubuntu 22.04 / ROS2 Humble，1440×1080 BGR8，4,665,600 像素字节，两个独立进程，KeepLast(5)、best_effort、volatile、automatic liveliness、默认无限 deadline。每轮发送 1000 帧，目标 250 Hz，留两秒排空。延迟从填充完成、publish 前到接收回调入口，实际发送频率包含分配与填充。两种接收端统一在 const 引用回调中读取样本，返回后不保存引用。

默认配置组：三种 RMW、两类消息均普通发布。共享配置组：Fast DDS 载入含同步发布与 Data Sharing 的配置，Cyclone DDS 启用 iceoryx，Zenoh 启用序列化 SHM。再为两端实际支持借出的定长类型追加借出发布。每轮 14 个组合、共三轮 42 个高速运行。

- 构建通过，用时 11.1 秒，见 [build.log](evidence/ros2-image-unified-20261006/build.log)。
- 三轮 42 组均发布 1000 帧，所有收到的图像数量/首尾检查通过，节点正常退出，无 Zenoh 共享池创建错误。逐轮值见 [matrix/results.json](evidence/ros2-image-unified-20261006/matrix/results.json)，各指标分别取三轮中位数见 [summary.json](evidence/ros2-image-unified-20261006/summary.json)。
- 另跑 14 组低频逐字节检查。所有已收到的图像完整像素通过；best_effort 默认 DDS 仍有丢帧，接收比例单独记录，没有把它们记成全部收到。共享配置的定长普通/借出组均收到 20/20。见 [full-pixels/results.json](evidence/ros2-image-unified-20261006/full-pixels/results.json)。
- 所有变长图像组合两端能力为 0/0。定长图像默认为 0/0，共享配置下 Fast DDS/Cyclone DDS 为 1/1，Zenoh 为 0/0。工具不会把分配器回退当成真实借出组。
- Zenoh 每个会话使用 6 MiB 池，memlock 为 8192 KiB；RouDi 使用 32 个 5 MiB 图像块与小块池。实际包版本见 [environment.log](evidence/ros2-image-unified-20261006/environment.log)。
- 新运行源码与实际构建的临时工作空间逐文件校验一致。项目清单见 [project-sha256.json](evidence/ros2-image-unified-20261006/project-sha256.json)。

收发节点、路由器与 RouDi 只管理本次创建的进程。最终容器恢复实验前 exited(143)。Zenoh 留下的本次 32 字节控制标记确认无可见打开/映射引用后，由对应 rootless 所有者清理，原有共享对象完整保留。见 [shared-objects-final.json](evidence/ros2-image-unified-20261006/shared-objects-final.json) 与 [container-restored.log](evidence/ros2-image-unified-20261006/container-restored.log)。

技术条件依据 [rmw_fastrtps Humble 的借出与 Data Sharing 说明](https://github.com/ros2/rmw_fastrtps/blob/humble/README.md#enable-zero-copy-data-sharing)、[rmw_cyclonedds Humble 的共享内存说明](https://github.com/ros2/rmw_cyclonedds/blob/humble/shared_memory_support.md) 与 [rmw_zenoh Humble 的共享内存设计](https://github.com/ros2/rmw_zenoh/blob/humble/docs/design.md#shared-memory-optimization)。

## 完整章节检查清单

| 项 | 状态 | 依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main.tex 第一章保留目标、建议学时、Humble 主线与卷三边界。 |
| 2 核心示例 | 通过 | 基础、工程、组件、借出和统一图像比较示例保留前提、操作与结果判断。 |
| 3 复杂概念项目 | 通过 | image-path-demo 保留完整工程，新增统一模板收发与记录工具，实际构建及 56 组运行完成。 |
| 4 项目正文讲解 | 通过 | 正文保留完整组件/借出代码、构建配置和 FixedImage 接口；按用户要求 iceoryx 只讲工具作用，统一记录器在 results 中说明，完整源码及最短操作说明在 examples/README。 |
| 5 命令与参数 | 通过 | 21 个 tbash 块 Bash 语法通过，统一命令涵盖两类消息、配置、重复数与实际支持的借出。 |
| 6 随堂练习 | 通过 | 全章 24 题，借出题前置类型条件，统一图像题覆盖全部 RMW 与两类消息，慢处理题保留。 |
| 7 难点归纳 | 通过 | 类型差异表、通用机制小结、默认/共享两张统一表说明布局、传输与借出分别影响什么。 |
| 8 易错提示 | 通过 | 本地分配回退、变长字段、定长仍需实现支持、样本使用期限在操作附近说明。 |
| 9 本章小结 | 通过 | 按预算、组件、类型与工具、统一比较、实际相机串联。 |
| 10 章末习题 | 通过 | 原 14 题保留；第 13 题答案说明实际探测对象和共享样本验证条件。 |
| 11 本章验收 | 通过 | 原 8 项保留，第 7 项统一检查三种中间件的普通/定长图像与借出能力。 |
| 12 参考答案 | 通过 | 24+14 题都有可定位答案，顺序与正文一致。 |
| 13 作者语言习惯 | 通过 | 先明确类型条件，再解释工具作用，最后统一比较；取消独立 iceoryx 调试流程，避免分号式防御说明。 |
| 14 图片与图文 | 通过 | 沿用内存路径图，说明同步补上第三行的类型与配置条件，图文对应。 |
| 15 图片标记及引用 | 通过 | 沿用 ros2_image_paths_revised.pdf，无新图片，资源与引用检查通过。 |
| 16 文件组织 | 通过 | 机制在 path，全部图像实验条件、数据与解读在 results，review/answers/README 同步。 |
| 17 包含与交叉引用 | 通过 | 32 个包含文件、340 个标签、284 个被引用标签，唯一性、路径及题解定位通过。 |
| 18 源码与版面格式 | 通过 | 核心源码与配置保留，Launch 代码标题移到代码附近；两类消息表和题解分页已查看。 |
| 19 示例实际构建运行 | 未完成 | 本次统一收发构建、42 组高速与 14 组完整像素检查已完成；完整章的真实相机、跨主机和其他未重跑示例仍有现场验收缺口。 |
| 20 编译与 PDF | 通过 | 从 main.tex 编译至引用稳定，检查目录、类型/工具说明、统一结果、小结验收与题解。 |

19 项通过，1 项未完成。第 19 项指完整章的现场验收，统一图像比较与本轮编辑已经完成。静态与版面证据见 [static-checks.json](evidence/ros2-image-unified-20261006/static-checks.json)、[pdf-check.json](evidence/ros2-image-unified-20261006/pdf-check.json) 和对应 PDF 页面图。

工程章节原有 408–409 行 2.8734 pt 越界与 Fandol 斜体替代提示沿用，目标内容没有新增越界。本轮未新增文献引用，未重跑独立 Biber 流程。

最终 XeLaTeX 第 7、8 遍成功，aux、toc、out 三份文件哈希稳定。保存的第二册 PDF 共 307 页，已查看最终目录、内存路径图、组件/Launch、借出与类型说明、两张统一结果表、小结验收及对应答案，共 19 页。PDF SHA-256：`cb062c12042a7b065a1904ebfa30896bbba4eaba0861b6dbf10574cc0246c951`。
