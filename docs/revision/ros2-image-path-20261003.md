# ROS2 大图像链路修订与验收（2026-10-03）

本轮在卷二第一章内部加入“**大图像链路：中间件与内存**”，依次讲图像预算、中间件选择、零拷贝与组件容器、借出消息、250 Hz 合成对照。沿用 Ubuntu 22.04 / ROS2 Humble 主线，承接前面的节点、ament、Launch 和排障操作。相机 1440×1080@250 Hz 的上限来自用户实际工作场景；本轮没有接入物理相机。

正文是 [A_ros2_image_path.tex](../../02-专项技术栈/chapters/A_ros2_image_path.tex)，实测表独立放在 [A_ros2_image_results.tex](../../02-专项技术栈/chapters/A_ros2_image_results.tex)，由前者包含，仍属于第一章。主入口、章首学习目标、工程节的进阶指引、章末小结、题目、验收与卷末题解已同步。没有移动或重命名既有章节，也没有修改共享模板。原有目录只显示节级，新内容的五个小节在正文编号为 1.3.1—1.3.5。

新增 [image-path-demo](../../02-专项技术栈/examples/ros2/image-path-demo/README.md) 包含真实 Frame 接口、Source/Sink 组件、两处组件注册、完整清单与构建文件、三种布局的 Launch、借出能力探测、Fast DDS 显式配置和结果记录器。正文直接引入完整核心文件，解释它们的执行顺序；记录器是辅助调度与收集程序，其计时点、参数、输出和资源口径写在正文与 README。五道新随堂练习分别覆盖预算、RMW 对照、两类容器与所有权、借出/回退、慢处理与部署设计；章末由 10 题增至 14 题，用四道综合题覆盖新增能力，避免只重复随堂操作。全章 18 道随堂练习、14 道章末题均有可定位题解。

图像预算按紧密排列计算：Bayer8/mono8 为 388.8 MB/s，BGR8 为 1166.4 MB/s，帧间隔 4 ms。每次完整 BGR8 复制的新增读写量估算为 2.3328 GB/s，明确区分估算和内存总线实测，也说明 step、格式转换、缓存/DMA 与协议开销。ROS2 组件容器、Distrobox/Podman 系统容器、进程内交接、SHM transport、Data Sharing 和两端借出分开解释。

## Zenoh 后续补充

在以上五节内继续补入 Zenoh / rmw_zenoh_cpp 的安装、路由器、发现、三种组件布局、共享内存配置与借出对照；相机尺寸保持 1440×1080（宽×高）。当前 PDF 为 293 页。后续新增软件 23 组图像运行与 2 组借出探测，完整记录、资源回退案例与同一章逐项检查见 [Zenoh 补充验收](ros2-zenoh-20261003.md)。下面的 28+4 是先前轮次记录；当前共同性能表另追加 Zenoh，原始 DDS 数值未替换。

## 软件实测与限制

所有新增软件实验在带 NVIDIA 集成的 ubuntu2204 Distrobox 内进行：Ubuntu 22.04.5，rclcpp 16.0.21、rcl 5.3.13、rmw_fastrtps_cpp 6.2.10、rmw_cyclonedds_cpp 1.3.5、Fast DDS 2.6.12。主机 i7-12700H，MemTotal 为 65621640 KiB；容器共享宿主网络和 IPC，/dev/shm 约 32 GiB。设备查询显示 RTX 3070 Ti Laptop GPU / 驱动 615.71.09。本例不使用 GPU；设备可见性不证明图像到 GPU 的传输路径。[环境](evidence/ros2-image-path-20261003-runtime/environment.json)、[资源检查](evidence/ros2-image-path-20261003-runtime/container-resources.txt)、[汇总及源码 SHA](evidence/ros2-image-path-20261003-runtime/summary.json)保留实际证据。

| 实验 | 记录与结果 |
|---|---|
| Release 构建与 rosdep | 独立 /tmp 工作空间构建 image_path_demo 成功，全部清单依赖已满足；两个类进入组件索引。保存 build.log、rosdep-check.log。 |
| 小输入 6 组 | 两种 RMW × separate/same/intra；64×48 BGR8、25 Hz、每组 50 帧，全部收到 50 帧，首尾像素检查无失败；intra 地址记录全部匹配。[逐轮数据](evidence/ros2-image-path-20261003-runtime/small-fixed/results.json)。 |
| 正文默认参数 | 手动启动 intra，25 Hz、100 帧，全部收到；component list 显示 /image_box 下的 /sink、/source。保存 manual-default.log 和 manual-component-list.txt。 |
| 相机场景合成负载 18 组 | 1440×1080 BGR8，目标 250 Hz，每轮 1000 帧，两种 RMW × 三种布局，各重复三次，best_effort、深度 5、两秒排空、没有算法工作与外部订阅者。[逐轮数据](evidence/ros2-image-path-20261003-runtime/bgr250-1440x1080/results.json)。 |
| 慢处理 2 组 | 小图像，Fast DDS separate，250 Hz、500 帧、8 ms 模拟工作。深度 5 收到 249 帧、P95 20.003 ms；深度 100 收到 344 帧、P95 746.568 ms。两次都用两秒排空。[深度 5](evidence/ros2-image-path-20261003-runtime/slow-5/results.json)、[深度 100](evidence/ros2-image-path-20261003-runtime/slow-100/results.json)。 |
| 借出能力 4 组 | 默认 Fast DDS 的 Float64/Image 为 0/0；显式 Data Sharing 为 1/0；Cyclone DDS 为 0/0；显式配置后禁用借出为 0/0。四次发布 API 调用成功，false 轮次使用本地分配回退。[原始输出](evidence/ros2-image-path-20261003-runtime/loans.json)。 |
| 最终记录器复核 1 组 | Fast DDS intra，20 帧全部接收，正常退出，校验新增加的退出状态记录与无样本保护。[记录](evidence/ros2-image-path-20261003-runtime/final-runner/results.json)。 |

当前教材使用 **28 组图像运行 + 4 组借出探测**。相机尺寸更正为 **1440×1080（宽×高）** 后，已重新执行全部 18 组大图像对照，并更新命令、预算公式、习题与答案。旧的 18 组宽高反置运行原样保留在 `bgr250/`，作为历史记录，不用于当前表格；累计实际执行 46 组图像运行。大负载中位数如下，指标分别取三轮中位数，P95 不跨轮合并样本：

| RMW | 布局 | 实际发送 Hz | 实际接收 Hz | 接收比例 | P95 ms |
|---|---|---:|---:|---:|---:|
| Fast DDS | separate | 250.0 | 87.5 | 34.7% | 2.445 |
| Fast DDS | same | 250.0 | 250.2 | 100.0% | 0.968 |
| Fast DDS | intra | 250.0 | 250.0 | 100.0% | 0.042 |
| Cyclone DDS | separate | 250.0 | 249.6 | 99.7% | 3.580 |
| Cyclone DDS | same | 250.1 | 250.2 | 100.0% | 0.959 |
| Cyclone DDS | intra | 250.0 | 250.0 | 100.0% | 0.031 |

这是此机器、此配置、此输入下的对照，不是中间件普遍排名，也未单独测出某一次 DDS 复制耗时。separate 有两个单线程执行器，same/intra 有一个，因此部署布局也是变量。P95 仅覆盖已收到样本；Fast DDS separate 三轮接收比例为 34.7%、35.9%、18.1%，不能用其较低 P95 掩盖丢帧。Cyclone DDS separate 为 99.7%、99.7%、99.8%。默认 SHM 是否承载全部大样本、具体回退路径没有单独跟踪证明，不推断为已测定的唯一瓶颈。

小图 same 中曾出现 50 帧的 49 次地址数值相同；分配器复用地址说明指针相等不能单独证明零拷贝。intra 的结论结合启用选项、唯一所有权接口、同进程一对一条件及记录，限定到本例的像素交接。图像生成仍分配/填充，其他处理边界未被省掉。

延迟从填充完成后、publish 前的 Linux 单机单调时钟起算，到回调入口；不含曝光、SDK、填充、识别完成和控制执行。CPU 秒包括发现、加载与排空，RSS 相加重复计算共享页，都不是稳态利用率或实际物理内存结论。原先运行的辅助记录器另存为 benchmark-recorder.py；当前版本新增 Launch 退出状态和零样本保护，指标定义没有改变。本次正确尺寸的 18 组对照全部使用当前版本，Launch 正常退出、每轮发送 1000 帧、首尾像素检查无失败；same/intra 共 12 轮全部接收 1000 帧。后续选型应调整顺序、重复并测实际算法与相机。

**未完成的物理验证**：实际相机/SDK/DMA、Bayer 转换、识别/控制延迟、CPU/GPU 图像传输、第二台主机或跨系统容器共享样本、订阅端借出和完整跨进程图像零拷贝。本轮不将这些写成实测通过。新增的物理相机验收任务保留在章末；没有设备时记录未完成。既有 ROS2 基础、Launch、日志、IDE 与 GUI 软件证据沿用本聊天上一轮的 [Humble 验证记录](volume-2-humble-20261003.md)，本轮未重复宣称新的硬件验证。

## 逐项章节检查

按 [textbook-chapter 规范](../../.agents/skills/textbook-chapter/SKILL.md) 检查完整第一章，19 项通过、1 项未完成；没有不适用项。

| 项 | 状态 | 位置与依据 |
|---|---|---|
| 1. 章首目标、学时、边界 | 通过 | main.tex 的第一章 introduction，增补对照与借出目标、半天至一天实验学时；保留先修与卷三边界。 |
| 2. 核心小节示例 | 通过 | 既有三个正文子文件保留示例；新增五节均有示例，明确共用项目对应关系、条件与结果判断。 |
| 3. 复杂概念完整项目 | 通过 | image-path-demo 含接口、组件、清单、构建、Launch、配置、记录器和 README，实际 Release 构建成功。 |
| 4. 正文项目内容与讲解 | 通过 | 目录、完整 Frame/组件/清单/CMake/Launch/探测/XML 直接引入；解释计时点、注册和所有权；新增路径图。 |
| 5. 命令、参数、替换条件 | 通过 | BOOK、独立工作空间、Bash/Zsh 脚本、容器名、域、尺寸/频率/帧数、记录器子集、输出路径与排空口径均说明。 |
| 6. 随堂练习覆盖 | 通过 | 新增五题覆盖五节；组件练习同时覆盖系统容器资源检查，已有 13 题保留，总计 18。 |
| 7. 难点小结 | 通过 | 预算/队列表、中间件表、三路径图及 conclusion 对比容器、共享内存、Data Sharing、借出与回退。 |
| 8. 易错点与操作边界 | 通过 | 说明配置继承、额外订阅者、动态类型、地址复用、所有权失效、资源容量、时间同步、失败日志；无新增破坏性操作。 |
| 9. 本章小结 | 通过 | A_ros2_review.tex 增补负载→RMW/QoS→布局/所有权→借出→测量的知识地图。 |
| 10. 章末习题 | 通过 | 14 题含基础、提高、实践；新增四道综合题覆盖预算、两类容器、借出边界和性能指标，数量调整理由见前文。 |
| 11. 本章验收 | 通过 | 增补现场改参数/布局、借出配置与物理相机埋点任务；与标准答案习题分工明确。任务的列出不等于已经执行。 |
| 12. 参考答案完整 | 通过 | answers.tex 中 18 个 exercise 和 14 个 problem 标签均有对应 ref，静态检查无遗漏，PDF 编号稳定。 |
| 13. 语言口吻 | 通过 | 承接字符串到图像的处境，随操作解释数据、输出与故障，保留“学长带着操作”的连贯语气。 |
| 14. 图片内容与风格 | 通过 | 实际查看 ROS2 分层图作风格参照；新图青色、宋体、统一框/箭头，候选及正文实际尺寸均检查；既有 _revised 图按规范跳过重复整理。 |
| 15. 整理标记与引用 | 通过 | ros2_image_paths_candidate.pdf → ros2_image_paths_revised.pdf；先检查候选，再发布，正文引用与 render_ros_image_path.py 输出一致。 |
| 16. 文件组织 | 通过 | 新内容与实测表分工清楚，实验集中于第一章 examples/ros2；没有不必要的既有文件改名。 |
| 17. 包含与交叉引用 | 通过 | main→image_path→image_results 单一包含；前文组件指引、图/表/习题引用匹配，编译无未定义或重复标签。 |
| 18. 格式协调 | 通过 | 保持模板标题层级、三线表与 listings；短命令、接口与探测配置保留同页，大段源码/清单按模板自然续页，流程图紧随正文。 |
| 19. 示例实际运行 | 未完成 | 当前教学软件运行 28+4 组已检查，宽高反置的旧 18 组保留为历史记录，既有软件证据见上一轮；物理相机、GPU 图像边界、跨机器/跨系统容器与订阅端借出尚未执行，不能计入通过。 |
| 20. 编译与 PDF 检查 | 通过 | 从完整卷二主文件在清洁暂存目录按项目导出函数连续 XeLaTeX 三遍，引用/目录稳定；无 Overfull、缺文件、重复标签或未定义引用，检查目录、章首、新正文、表图、代码与新增题解页。 |

## 构建与交付

尺寸更正轮的卷二 PDF 为 **290 页**；Zenoh 补充后，当前仓库忽略的 02-专项技术栈/main.pdf 为 **293 页**，最新编译/视觉证据见 Zenoh 验收；尺寸更正后的临时输出位于 /tmp/tutorial4new-ros-image-size-20261003，更正前 PDF 保留在该目录的 previous-main.pdf；初次扩写输出保留在 /tmp/tutorial4new-ros-image-path-20261003。编译日志与最终 PDF SHA 放在本轮 evidence 中。没有新增文献条目或使用 cite，不额外宣称执行过 bibliography 后端流程；沿用模板的 Fandol 斜体字体替代提示，不影响已检查内容。

初次扩写已视觉检查物理 PDF 页 4、7、40—56、265—267，覆盖目录、章首、所有新增正文与新增答案；预览保留在 pdf-qa/ 中。尺寸更正后，整卷页数与分页保持不变，逐页文本比对仅第 40、53、54、56、265 页发生变化，已再次逐页检查这五页的尺寸、命令、表格与题解；当前预览保留在 pdf-qa-corrected-size/ 中。流程图首次候选中发现 Data Sharing 标注与框内文字相撞，修正后发布；正文浮动图整页留白、短命令跨页也已调整并复核。

技术依据来自官方主线：[Humble 进程内通信](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials/Demos/Intra-Process-Communication.rst)、[Humble 组件概念](https://github.com/ros2/ros2_documentation/blob/humble/source/Concepts/Intermediate/About-Composition.rst)、[Fast DDS 的 Humble RMW 配置与借出前提](https://github.com/ros2/rmw_fastrtps/blob/humble/README.md)、[Humble 借出回退与生命周期实现](https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/loaned_message.hpp)、[Humble 发布者借出条件](https://github.com/ros2/rmw_fastrtps/blob/humble/rmw_fastrtps_cpp/src/publisher.cpp)、[Fast DDS 2.6 系列零拷贝三段条件](https://fast-dds.docs.eprosima.com/en/v2.6.11/fastdds/use_cases/zero_copy/zero_copy.html)。具体结果以本轮实际安装版本与原始日志为准。
