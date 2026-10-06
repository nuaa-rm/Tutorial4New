# ROS2 三种数据路径图修正（2026-10-05）

本次修正卷二图 1.5 的图文对应关系，沿用 `ros2_image_paths_revised.pdf` 文件名和教材的青色矢量图风格。生成源为 `scripts/render_ros_image_path.py`。

- 第一行对应进程内传递：在同一个组件容器进程内，经 rclcpp 转移 UniquePtr 所有权，交接同一份消息与像素缓冲区。
- 第二行以 Fast DDS 的 SHM transport 为例：分别画出发布进程、订阅进程及共享传输缓冲区，标出序列化、复制写入、复制读出和反序列化。
- 第三行对应完整的跨进程共享样本零拷贝：发布端直接填充借出样本，订阅端借读后归还；两端应用与 DDS 访问同一个共享样本池，并列标出 Fast DDS Data Sharing 与 Cyclone DDS/iceoryx。
- 删除图内的实验验证范围、额外处理成本、普通 Image 能力限制等声明。图注与正文指引同步调整，标签沿用。

## 首轮图修正涉及的检查项

| 教材规范项 | 状态 | 依据 |
|---|---|---|
| 14. 图片实际查看及图文、风格对应 | 通过 | 已查看原图、修改后的整张图，以及物理 PDF 第 56 页的正文尺寸渲染；三行顺序与图注一致，进程边界、复制和共享样本可辨认，无文字重叠。 |
| 15. 整理标记及生成路径 | 通过 | 沿用 `_revised`；生成脚本及正文引用均指向同一 PDF，候选图与发布图的渲染像素一致。 |
| 17. 包含与交叉引用 | 通过 | 结构检查确认 32 个输入文件、337 个唯一标签、282 个引用标签，资源和题解定位检查通过；图标签保持 `fig:ros2-image-paths`。 |
| 18. 格式协调 | 通过 | 保持现有图注、0.97 倍正文宽度、中文字体和青色线框；用橙色虚线标明 SHM 复制箭头。 |
| 20. 编译与 PDF 检查 | 通过 | 从卷二 `main.tex` 在清洁临时目录连续 XeLaTeX 两遍，辅助文件稳定，无未定义引用；最终 307 页，与修正前逐页文本比较仅物理第 56 页变化，第 56、57 页均已视觉检查。 |

验证证据保存于 `docs/revision/evidence/ros2-image-path-figure-20261005/`。编译日志中既有 Launch 正文第 642–643 行的 2.8734 pt 超宽提示与本图无关，未在本轮修改。

## 图下讲解同步

随后同步调整 `A_ros2_image_path.tex` 图下的三段讲解：先按三行说明消息所有权、共享传输缓冲区和共享样本的区别，再引入组件与组件容器，最后把 UniquePtr 的交接明确放在第一行的进程内路径中。借出消息仍在下一节展开。

本轮正文口吻及图文对应检查通过；结构与引用检查通过。重新从卷二主入口在清洁临时目录连续 XeLaTeX 两遍，辅助文件稳定，仍为 307 页，无未定义引用或新增超宽提示。与上一轮 PDF 比较，物理第 56–65 页因文字增加重新分页，这十页均已视觉检查；图及三段讲解同页，Distrobox 提醒完整移至下一页，代码、标题与示例衔接正常。最新编译日志和页面预览保存在上述证据目录的 `prose/` 子目录。

## Fast DDS 与 Cyclone DDS/iceoryx 的范围区分

用户指出第二行采用的是 Fast DDS 结构，本轮明确其标题与图注为 Fast DDS SHM transport 示例。第三行改用共享样本与样本引用的通用表达，样本池上方并列标出两种实现。图内继续只讲路径。

图下讲解和借出消息节同步说明：Fast DDS 的 SHM transport 与 Data Sharing 是不同路径；Cyclone DDS/iceoryx 也可通过共享样本和借出接口实现跨进程零拷贝。正文交代 Humble 路径的固定布局、同机、共享内存配置、RouDi 与 QoS 条件，并区分普通发布 API 与 loan API。参考答案及示例 README 对既有 Cyclone DDS 0/0 探测明确为默认未启用 iceoryx 的配置。

机制核对、图文对应、生成路径、参考答案对应、结构与引用检查通过。本轮没有新增 iceoryx 运行实验，机制依据为官方 Humble 文档，既有实验数据沿用原记录。

最终图和正文尺寸渲染已检查通过；候选图与发布图的渲染像素一致。卷二主入口在清洁临时目录连续 XeLaTeX 两遍，辅助文件稳定，仍为 307 页，无未定义引用或本轮新增超宽提示。本轮目标变化页为物理第 56、67–69、283 页，均已视觉检查，并复核第 57 页衔接；图下讲解保持完整同页。最终证据保存在上述目录的 `iceoryx/` 子目录。

## 技术依据

- [ROS2 Humble 进程内通信示例](https://github.com/ros2/ros2_documentation/blob/humble/source/Tutorials/Demos/Intra-Process-Communication.rst)：UniquePtr 的消息所有权交接。
- [Fast DDS 2.6 Data Sharing](https://fast-dds.docs.eprosima.com/en/v2.6.11/fastdds/transport/datasharing.html)：SHM transport 的两次历史与传输缓冲区复制，以及共享历史的区别。
- [Fast DDS 2.6 Zero-Copy](https://fast-dds.docs.eprosima.com/en/v2.6.11/fastdds/use_cases/zero_copy/zero_copy.html)：发布端借出、Data Sharing 和订阅端借读归还。
- [Cyclone DDS 的 Humble 共享内存说明](https://github.com/ros2/rmw_cyclonedds/blob/humble/shared_memory_support.md)：iceoryx 配置、普通发布与借出接口，以及固定布局和 QoS 条件。
