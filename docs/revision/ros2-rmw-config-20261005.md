# RMW 安装、DDS XML 与 Zenoh 配置补充（2026-10-05）

将卷二第一章 `chapters/A_ros2_engineering.tex` 的“切换中间件与进阶变量”展开成可跟着操作的教程，继续使用 Ubuntu 22.04 / ROS 2 Humble。保留本轮之前已有的未提交内容，只修订相关正文、题解与示例索引。没有移动或重命名原文件，没有修改共享模板或教材图片。

新增内容按“安装实现 → 默认收发 → 两份 XML 选择网卡 → Zenoh 默认发现 → 完整 JSON5 的 client/router 连接 → 恢复环境”推进：

- 给出 Fast DDS、Cyclone DDS、Zenoh 的安装包与 RMW 值，说明安装、选择实现和加载配置是三件事；切换需要重新启动节点与 daemon。
- 提供 `examples/ros2/rmw-config-demo/fastdds.xml`、`cyclonedds.xml` 和 README。正文直接引入两份完整 XML，解释默认 participant、传输定义与引用、内建传输开关、网卡地址、Domain 配置匹配与组播条件。
- 区分两种 XML 的根元素、命名空间、配置树和加载变量；明确本机网卡地址与对端地址、ROS QoS 与底层配置的区别。没有给简单网卡配置额外启用 `RMW_FASTRTPS_USE_QOS_FROM_XML`。
- Zenoh 包含二进制安装、独立工作空间源码安装分支、三终端 router/talker/listener、默认发现和 peer/client 数据路径区别。JSON5 从安装包复制完整配置，正文片段仅展示应修改的已有字段，区分 router 的 `listen.endpoints` 和 session 的 `connect.endpoints`，并说明跨机器地址与端口。
- 增加两道随堂练习及对应题解，题解按正文次序排列。原域隔离题与全章其余练习保留，现为 20 道随堂练习、14 道章末题。
- 补充临时变量恢复、Fast DDS 发现服务器与 Zenoh router 的区别，以及安全配置的学习边界。

正文补丁见 [lesson.patch](evidence/ros2-rmw-config-20261005/lesson.patch)，当前完整源文件见 [A_ros2_engineering.tex](../../02-专项技术栈/chapters/A_ros2_engineering.tex)。修订前正文、答案和 PDF 备份在 `/tmp/tutorial4new-rmw-20261005/before/`。

## 本轮验证

使用已有 Distrobox `ubuntu2204`，实际加载 Humble；没有执行教材中的 apt 安装、ROS 软件升级或 Zenoh 源码构建。安装版本为 `demo_nodes_cpp 0.20.10`、`rmw_fastrtps_cpp 6.2.10`、`rmw_cyclonedds_cpp 1.3.5`、`rmw_zenoh_cpp 0.1.9`，具体 Debian 版本在 [runtime.json](evidence/ros2-rmw-config-20261005/runtime.json)。

| 实验 | 结果与依据 |
| --- | --- |
| Fast DDS 默认配置 | 通过；本机 talker/listener 收到序号 1、2、3。 |
| Cyclone DDS 默认配置 | 通过；同样收到序号 1、2、3。 |
| Fast DDS 完整 XML | 通过；只将随书 XML 的占位 IP 换成当前网卡地址，原生加载配置后收到对应三条消息。 |
| Cyclone DDS 完整 XML | 通过；同样替换本机 IP，用 `file://` 加载后收到对应三条消息。 |
| Zenoh 默认发现 | 通过；先运行原生 `rmw_zenohd`，默认 TCP 7447 连接下收到对应三条消息。 |
| Zenoh 完整 JSON5 / client 模式 | 通过；复制当前安装版本的 session/router，修改 mode、connect/listen 端点，使用临时本机端口 17747 收到对应三条消息。 |
| 清理与恢复 | 通过；只向本次启动的进程组发送退出信号，复查无测试节点或 router 残留；容器恢复为测试前的停止状态。见 [cleanup.json](evidence/ros2-rmw-config-20261005/cleanup.json)。 |

测试采用域 97 和独立话题 `/tutorial4new_rmw_check_20261005/chatter`，不与正文练习的域 42 混用。两种 DDS 的 XML 使用当前机器真实拥有的网卡地址；此结果证明配置能够加载并完成本机收发，没有测试第二台主机。每组核对 listener 的接收序号确实属于该 talker 的发布序号。测试程序、逐进程日志和配置路径均在 [运行证据目录](evidence/ros2-rmw-config-20261005/)。

静态检查通过：15 个新增 Shell 代码块经 `bash -n` 检查，两个 XML 能解析；实际入口包含 32 文件、334 标签、280 被引用标签，20 道随堂练习和 14 道章末题的答案定位完整；`git diff --check` 通过。

整卷从卷二入口使用 XeLaTeX 编译，最终 **301 页**，已更新 `02-专项技术栈/main.pdf`。目录、编号与引用辅助文件稳定，没有 Overfull、缺字、未定义引用、重复标签或重跑提示；沿用模板已有 Fandol 字形替代提示，未新增文献调用。实际检查物理页 **26–33、274–275**，覆盖段落前后、完整配置、步骤、练习和答案；修正长变量越界与 XML 介绍文字分页后，重看 **27–29、274–275**，其余所选最终页面与已检查版本像素一致。预览、编译日志和 PDF SHA-256 在 [summary.json](evidence/ros2-rmw-config-20261005/summary.json)。

## 完整章节逐项检查

既有章节结构与项目依据沿用 [卷二第一章修订记录](volume-2-chapter-1.md) 和 [Zenoh 图像实验记录](ros2-zenoh-20261003.md)，本轮重新核对当前入口、资源、题解及受影响正文。20 项中 19 项通过、1 项未完成，没有不适用项；“实际运行”仍保留未测部分，不能据六组本机测试宣称完整章节验收完成。

| 项 | 状态 | 当前依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | `main.tex` 第一章保留可验证目标、学时、Humble 主线和卷三边界。 |
| 2 核心示例 | 通过 | 既有核心示例保留；新增默认 DDS、XML、Zenoh 默认配置与 JSON5 操作示例都有前提、终端分工和收包判断。 |
| 3 复杂概念项目 | 通过 | 既有完整项目保留；新增 rmw-config-demo 用官方示例节点，只提供解释配置所必需的两份 XML 和 README，无需构建。 |
| 4 正文展示项目 | 通过 | 给出目录、两份完整 XML 的直接引入、关键字段与加载步骤；Zenoh 从安装包复制完整文件，片段用途明确，实际运行使用完整副本。 |
| 5 语法与参数 | 通过 | 三种包名/RMW 值、文件路径与 URI 区别、source 顺序、网卡占位值、端点和域均解释；新增 15 个 Shell 块语法检查通过。 |
| 6 随堂练习 | 通过 | 新增 XML 对照和 Zenoh JSON5 两题，分别覆盖配置机制与连接角色；全章 20 题，不按标题机械增加题量。 |
| 7 难点归纳 | 通过 | 安装/RMW 表、XML 对照讲解、peer/client 区别和环境 conclusion 对应易混淆概念，原工程与图像归纳保留。 |
| 8 易错提示 | 通过 | 包与变量不匹配、旧节点/daemon、填写对端 IP、默认 profile、组播、XML QoS 开关、局部 JSON5、重复键、覆盖变量、远端回环地址与进程恢复均有说明。 |
| 9 本章小结 | 通过 | 原 `A_ros2_review.tex` 保留通信、构建排障及三种 RMW/路由器/内存路径知识地图，本轮没有改动。 |
| 10 章末习题 | 通过 | 原 14 题继续覆盖基础、提高与实践；新增配置能力使用两道随堂操作题，避免重复增加章末题。 |
| 11 本章验收 | 通过 | 既有域恢复、RMW/布局、Zenoh router、借出与真实相机的现场任务保留。 |
| 12 参考答案 | 通过 | `answers.tex` 新增对应两题，按正文次序整理；当前全部 20+14 题都可通过标签定位。 |
| 13 语言口吻 | 通过 | 从已经跑通的节点继续讲，随操作解释选择、文件和观察结果，使用你/我们，避免仅罗列变量名。 |
| 14 图片风格检查 | 通过 | 本章既有图片均已标记 `_revised`，内容/样式未变，符合技能跳过重复整理条件；本轮使用文本配置对照，无新增教材图。 |
| 15 图片标记与引用 | 通过 | 既有资源与生成路径保留，结构检查确认资源存在；PDF 预览属于验收证据。 |
| 16 文件组织 | 通过 | 教程留在 engineering，题解留在既有 answers，配置在同卷 examples/ros2；未重命名、移动或重复包含原文件。 |
| 17 包含与交叉引用 | 通过 | 当前入口、资源、标签唯一性、引用与题解定位检查通过：32 文件、334 标签、280 被引用标签。 |
| 18 源码与排版格式 | 通过 | 沿用代码框、example/exercise/conclusion 与三线表；完整 XML 和介绍保持相邻；长变量、URI 占位用户名及题解次序已修正。 |
| 19 示例实际运行 | 未完成 | 本轮六组 Humble 本机收发均通过；未执行全新 apt 安装、Zenoh 源码构建或第二主机通信；完整章节原有物理相机等验收缺口保留。 |
| 20 编译与 PDF | 通过 | 整卷 301 页，引用与目录稳定；实际检查上述 10 页，修订后复查布局或确认像素一致，没有新增越界、缺字或引用问题。 |

## 官方资料

核对日期为 2026-10-05，Zenoh 文件实际以当前安装版本为准。

- [Humble 多 RMW 使用说明](https://github.com/ros2/ros2_documentation/blob/humble/source/How-To-Guides/Working-with-multiple-RMW-implementations.rst)：安装与运行选择、daemon 缓存。
- [Fast DDS 2.6 网卡白名单](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/transport/whitelist.html)及[默认 participant 配置](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/xml_configuration/domainparticipant.html)：传输定义、引用与默认 profile。
- [Humble rmw_fastrtps](https://github.com/ros2/rmw_fastrtps/tree/humble#full-qos-configuration)：XML 路径、ROS QoS 与内存/发布模式优先级。
- [Cyclone DDS 0.10.2 配置定义](https://github.com/eclipse-cyclonedds/cyclonedds/blob/0.10.2/etc/cyclonedds.xsd)：Interfaces、NetworkInterface 与 Domain 匹配。
- [rmw_zenoh Humble 安装与配置](https://github.com/ros2/rmw_zenoh/tree/humble)、[设计说明](https://github.com/ros2/rmw_zenoh/blob/humble/docs/design.md)、[Humble 发行包索引](https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml)：二进制/源码安装、默认发现、JSON5 文件和连接拓扑。

## 调整讲解顺序（2026-10-05）

按用户要求，把安装、默认 DDS 收发、两份 XML 网卡配置、Zenoh 安装与 JSON5/client/router 实验、环境恢复及发现服务器说明，从 `A_ros2_engineering.tex` 移到 `A_ros2_image_path.tex` 的“中间件怎么选：先比较同一条链路”。现在读者先在环境小节认识 `RMW_IMPLEMENTATION`，学完构建、启动和排障后，再从图像带宽预算进入中间件安装与配置，最后比较大图像并学习内存路径。

前面的环境小节只保留选择已安装实现、重启节点/daemon、恢复默认值和指向第 1.3.2 节的简短说明。合并后面的两张实现概览表，删去重复的切换与 Zenoh 介绍；安装、完整 XML/JSON5 教程和官方资料保留。两道配置练习随正文移动，标签不变，`answers.tex` 题解按新正文顺序排列，`rmw-config-demo/README.md` 指向新的正文位置。

| 检查 | 状态 | 依据 |
| --- | --- | --- |
| 内容与操作保留 | 通过 | 两个相关正文文件的 47 个原有 Shell 块完整保留；加上前文简述后，48 个当前块经 Bash 语法检查通过。 |
| 教学与题解顺序 | 通过 | 23 道随堂练习的标签顺序与题解一致；14 道章末题保留。安装/小消息/XML/Zenoh/恢复环境/大图像对照依次衔接。 |
| 包含与引用 | 通过 | 32 个入口包含文件、337 个唯一标签、282 个被引用标签；资源、引用和答案定位检查通过，`git diff --check` 通过。 |
| 编译与分页 | 通过 | 最终两次 XeLaTeX 编译后目录、编号与引用稳定，整卷 307 页。实际检查物理页 26–27、49–57、281–284；三处操作介绍及一处题解介绍与对应代码保持相邻。其余最终页面与已看版本像素一致。 |
| 新运行实验 | 不适用 | 本轮调整教材顺序，没有改配置文件或节点程序；没有重新执行安装、运行通信实验，也没有扩大此前运行验收范围。 |

已更新 `02-专项技术栈/main.pdf`。没有新增未定义引用、重复标签或缺字；保留原有 Launch 段落的 2.8734 pt 越界提示（正文移动后为 engineering 第 408–409 行）。既有完整章节现场验证缺口不变。本轮独立差异、最终预览、编译日志及摘要见 [顺序调整证据](evidence/ros2-rmw-config-20261005/order/summary.json)。
