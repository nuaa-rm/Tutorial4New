# 卷二第四章：OpenCV 与图像处理基础修订记录

以原 11/12/13.tex 的连贯操作讲解为参照，保留图像工具、流水线和 ROS 接口的教学范围。将零散代码整理为普通 CMake 图像实验与独立 ament 图像桥接两个完整工程，补齐练习、题解和实际中间图。软件验证已完成，相机实机仍未完成，不宣称全书验收通过。

## 项目与覆盖

本卷 `examples/opencv/image-lab-demo` 包含 CMake、README 和 14 个独立 C++ 程序，涵盖版本、Mat、读写/窗口/视频、HSV、阈值、滤波、形态学、轮廓、几何、ORB、合成输入和完整流水线。`examples/opencv/image-bridge-demo` 包含完整 CMake/package.xml、roundtrip 和 bridge_node，演示真实像素编码转换、Header 保留与异常拒收。正文在相应知识点直接展示全部核心代码及影响构建的配置，长源码按逻辑边界连续展示，没有省略函数中段。

12 道随堂练习分别以 `ex:v2-cv-` 的 build/mat/io/hsv/threshold/filter/morphology/contour/resize/features/pipeline/bridge 标签定位，覆盖每个核心小节。图像与视频共用 io 和 pipeline 练习，明确包含保存、读入失败、播放和退出；流水线用于综合前面的独立工具，桥接另有练习。十道章末题覆盖基础、几何验证/接口语义提高和丢失 H 区段的组合实践，不以改值题机械凑数。22 道题解全部通过 ref 定位。

## 20 项检查

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main 第四章含构建/读写/分割/几何/特征/ROS 目标、1–1.5 周学时和卷三赛场边界。 |
| 2 核心示例 | 通过 | B_opencv 的 12 个核心小节都有完整示例、前提、操作和结果，14 个程序及 ROS 共享覆盖关系见上文。 |
| 3 复杂项目 | 通过 | 两个工程完整，合成 PNG/MJPG 输入由 sample_demo 生成，无外找测试图要求。 |
| 4 正文展示项目 | 通过 | 目录、全部核心源码、两套构建配置直接展示，逐步解释流水线和回调，配实际六阶段图。 |
| 5 语法/参数 | 通过 | CMake -S/-B、文件与相机参数、图像类型、HSV、核/阈值、ORB 距离和 ROS 目录/版本均说明。 |
| 6 随堂练习 | 通过 | 12 题覆盖全部能力，共用 IO/流水线任务同时包含视频和窗口，不用“自行尝试”代替任务。 |
| 7 难点归纳 | 通过 | conclusion 区分 Mat 共享/clone、滤波/形态学、像素/encoding/Header；轮廓/像素面积有明确对照。 |
| 8 易错提示 | 通过 | 空输入、写失败、视频后端、红色色环、核去目标、坐标/画布、匹配不等于身份、文件覆盖和编码不符均说明。 |
| 9 本章小结 | 通过 | B_opencv_review 串联输入→分割→降噪→几何→绘图与 ROS，指出参数及赛场内容的查阅位置。 |
| 10 章末习题 | 通过 | 10 题覆盖核心内容，含特征几何与时间语义提高、单段红色流水线实践。 |
| 11 本章验收 | 通过 | 四项现场展示构建/窗口/视频、中间图/面积、ROI/缩放和 Jazzy 编码回调，与知识题分工。 |
| 12 答案定位 | 通过 | 12+10 题全部 ref，给具体输出、开放实践判断与实际版本边界。 |
| 13 作者口吻 | 通过 | 从前章采样接到图像，随操作说明原因与常见卡点，以“你/我们/不过/接下来”自然推进。 |
| 14 图片实际查看 | 通过 | 两张旧噪声图独立查看并核对同场景；新六阶段图实际生成、独立渲染和正文尺寸核对。 |
| 15 标记/引用 | 通过 | 已检查噪声图与新图带 _revised，B_opencv/E_camera 所有调用同步，脚本发布路径一致。 |
| 16 文件组织 | 通过 | 保留清楚的 B_opencv/B_opencv_review；普通图像与 ROS 工程分开，沿用 answers.tex。 |
| 17 包含/引用 | 通过 | 29 个入口文件、151 个标签、106 个被引用标签，路径/唯一性/22 题解定位检查通过。 |
| 18 源码/格式 | 通过 | 沿用标题映射；本章 cvblock 保持完整短代码，长源码沿职责分段，去掉不可断行的文件长串。 |
| 19 实际运行 | 未完成 | 64 条软件记录通过；无物理相机，驱动/参数设置、USB 连续帧及真实采集时间未验证；Humble 只给适配说明。 |
| 20 编译/PDF | 通过 | 卷入口至引用稳定，212 页；受影响目录、全章、图、答案和噪声图其他调用页均实际检查。 |

## 运行与环境

证据为 [volume-2-chapter-4-runtime.json](evidence/volume-2-chapter-4-runtime.json)，重放脚本 `scripts/verify_opencv_examples.py`。环境为 Distrobox ubuntu2404、Ubuntu 24.04.5、GCC 13.3、OpenCV 4.6.0、ROS 2 Jazzy、cv_bridge 4.1.0。已有依赖可用，没有将宿主 Arch 当成 ROS 构建环境。

- 14 个目标实际构建；基础输出及练习变体全部核验，包括 Mat 的 9/1、HSV 两段、阈值边界、滤波/大核、轮廓与 Canny 面积、缩放及 ORB 平移几何。
- 真实合成输入中 mask/opened/closed 像素为 3600/3599/3600，两个外轮廓/两个保留项，面积均 1711。面积阈值 2000 变体保留 0，但前面中间图不变；仅 low H 时像素 1801/1800/1800、外轮廓和保留均 1。
- Xvfb 中实际操作 viewer 保存和视频窗口，逐像素核对 saved.png；MJPG 文件自然读完 20 帧，Esc 提前退出读到 4 帧。窗口截图为真实独立显示环境，没有操纵用户桌面。
- ament 工程实际 colcon 构建，roundtrip 得到灰度 76/单通道/精确保留 sec=12、nanosec=345 和 frame。真实 ROS 回调/订阅核对 mono8、step=8、64 个像素、Header 与输入一致；CLI echo 和 image_tools/showimage 也运行。
- 注入错误 encoding 后日志实际拒收，随后正常帧仍处理。四张窗口证据用 xwd 记录，宿主 ImageMagick 仅转换格式为 PNG，未改截图像素；与六张实际 C++ 输出一起保存在 assets。

API 核对采用 [OpenCV 阈值官方教程](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)、[OpenCV 轮廓面积官方接口](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html)、[ORB 官方接口](https://docs.opencv.org/4.x/db/d95/classcv_1_1ORB.html) 和 [已安装版本 cv_bridge 4.1.0 源码](https://github.com/ros-perception/vision_opencv/tree/4.1.0/cv_bridge)。本环境头文件为 cv_bridge/cv_bridge.hpp；不把其他发行版的 .h 适配建议写成已实测。

## 图、文件与 PDF

旧图 `gaussian.png → gaussian_revised.png`、`salt.png → salt_revised.png` 保留真实原图像素，已核对同一场景、灰度表现、密度和正文尺寸，原有风格协调，不为统一而篡改图像。除 B_opencv 外，E_camera 的两个 includegraphics 也同步改路径并复查其物理页 119/122；此处只有引用路径变化，相机章节尚未全面修订。

新图 `opencv_pipeline_candidate.pdf → opencv_pipeline_revised.pdf` 从真实六张中间图排版，青色中文标题与章节一致。独立渲染发现本机 Matplotlib/Pillow 的压缩索引图出现斜纹，脚本改为直接嵌入原像素，复查后矩形、孔洞与边缘均正确，再发布整理标记；不是改变处理结果来修图。

tex 无移动或重命名，main 仍包含 B_opencv→B_opencv_review；仅更新本章目标，局部代码环境不修改共享模板。最终 PDF 212 页，实际检查物理页 4–5（目录）、71–89（全章）、90（后章衔接）、199–203（题解及相邻章）、119/122（噪声图其他调用）。最终又核对 71/78/85/119/122 的目标与图像。无 overfull、缺文件、重复标签、未定义引用或重编提示；模板/其他未修订内容原有的字体替代与 math 字体提示保留，未造成所检查页显示问题。
