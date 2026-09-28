# 卷二第七章：相机与成像原理修订记录

继续参考修订前 c5543bb 的 11/12/13.tex：从“算法能跑但相机图片糊了、颜色不对”的实际处境接着讲，用连贯段落解释操作、条件和结果。保留 CCD/CMOS、光圈/曝光/增益、快门、四种噪声、像素格式、Gamma、景深、焦段、标定、ROS、双目及 HDR/同步范围；纠正按 CMOS 名称推断快门、增益增加光子、低 RMS 保证质量以及 SAVE/COMMIT/部署混同等说法。

## 项目与题目

本卷 examples/camera/calibration-lab-demo 共 11 个核心 Python 文件、506 行。数值/数组实验、生成输入、角点检测、内参拟合、独立验证、YAML、回放服务、校正输出核对和双目求解都完整提供；README 写明依赖、目录、命令和真实验证边界。正文直接引入全部核心代码，较长回放按配置、初始化、保存、发布/退出分段，连续行号不漏源码。

13 道随堂练习和 10 道章末题全部以 label/ref 对应既有 answers.tex。核心能力由逐节练习覆盖，综合章末题合并传感器/快门/噪声和镜头/景深条件，不机械增加题数。开放题给输出、模式、参数读回、图片与缺设备时的记录标准。

## 20 项检查

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | main 第七章保留可验证的曝光、格式、模型、ROS 部署目标、4–6 天建议学时和卷三/几何章边界。 |
| 2 核心示例 | 通过 | E_camera/E_calibration 有查表、操作、完整数值和图像/ROS 示例；快门共用运动预算、项目准备共用后续运行练习，覆盖关系写明。 |
| 3 复杂项目 | 通过 | 11 文件组成完整链路，模拟输入可生成、依赖和运行路径齐全，无未实现回调或伪代码。 |
| 4 正文展示 | 通过 | 项目结构、全部源码、数据生成条件、K/D/R/P 与 YAML 配置作用在相应概念旁讲解。 |
| 5 命令/参数 | 通过 | 通用形式、米/毫米/毫秒单位、内角点、径向参数、重映射、发行版与可替换路径均说明。 |
| 6 随堂练习 | 通过 | 13 题覆盖传感器、曝光、噪声、格式/Gamma、景深、运动/焦段、拟合、裁剪、ROS、双目、HDR。 |
| 7 难点归纳 | 通过 | 三处 conclusion 串联快门/模糊、亮度/信息、拟合/验证/部署及不同外参。 |
| 8 易错提示 | 通过 | 输出覆盖、自动曝光、模型/坐标系、正面退化、尺寸不一致、参数单位、归档覆盖和服务缺失均明确。 |
| 9 本章小结 | 通过 | E_camera_review 用 conclusion 回顾成像→标定→独立检查→部署，保留查阅与实拍边界。 |
| 10 章末习题 | 通过 | 10 个综合自测任务覆盖基础、条件比较、单位/时序提高与运行实践。 |
| 11 本章验收 | 通过 | 四项要求提交真实设备/模式、图片和配置、不同独立验证图、重启读回与校正输出；双目/HDR 另交同步证据。 |
| 12 参考答案 | 通过 | 13+10 全部 label/ref 定位；计算、实际对照、开放实践思路与判断标准齐全。 |
| 13 作者口吻 | 通过 | 从上一章接着讲，随步骤解释原因与后果，使用“你/我们/首先/然后/不过”，保留适量自然吐槽。 |
| 14 图片实际查看 | 通过 | 9 张旧图实际查看，新矢量图、真实 GUI 截图独立查看及正文尺寸检查；既有 Gaussian/salt 仅按新比较布局复核。 |
| 15 标记/引用 | 通过 | 检查后发布 9 个 revised 文件，旧图全部调用同步；真实照片及 GUI 像素未改，渲染脚本支持候选/发布路径。 |
| 16 文件组织 | 通过 | E_camera 主讲成像与项目准备、E_calibration 讲模型与 ROS，E_camera_review/answers 沿用原职责。 |
| 17 包含/引用 | 通过 | 29 个入口文件、214 标签、180 个被引用标签；路径、唯一性及全部 23 题定位通过。 |
| 18 源码/排版 | 通过 | 保留公式/命令含义，消除长调用越界，回放拆分不把函数定义与说明交错；检查全章代码、照片和公式。 |
| 19 实际运行 | 未完成 | 数值、图像求解、单目 GUI、CLI、参数保存/重启、真实 image_proc 和双目回放均实测；真实曝光/相机标定、HDR/硬件同步、厂商驱动与双目 GUI 操作未完成。 |
| 20 编译/PDF | 通过 | 从卷入口编译到引用稳定，235 页；完整相机章、题解、目录和邻章衔接实际查看，无缺图、overfull、未定义引用。 |

本章为 19 项通过、1 项未完成。软件模拟和教学回放支持正文结论，但不冒充物理相机验收。

## 实测证据

- [runtime.json](evidence/volume-2-chapter-7-runtime.json)：34 条实际检查，含版本、11 个源码散列、输入/输出、负例与硬件缺口。
- [gui.json](evidence/volume-2-chapter-7-gui.json)：已安装 camera_calibration 5.0.13 的 OpenCVCalibrationNode，真实界面采样及鼠标点击 CALIBRATE/SAVE/COMMIT。没有修改采样/求解内部状态。归档含 40 张图与 ost.yaml/ost.txt，写入 YAML 的 K/D 与 GUI 消息逐项一致。
- [cli.json](evidence/volume-2-chapter-7-cli.json)：正文 ros2 run 命令实际开启窗口；话题为 Image、可靠发布者、约 10 Hz，SetCameraInfo 服务真实可见；rqt 实际选择 /camera/image_rect 并显示校正棋盘格。CLI 启动验证和 GUI 按钮验证分别记录，未将两者混称同一进程。
- scripts/verify_camera_examples.py、verify_camera_gui.py、verify_camera_cli.py 为可复核验证入口；全部图形检查使用独立 Xvfb，仅终止本脚本启动的进程。GUI 默认归档有原文件时先备份并还原，没有覆盖用户已有归档。

环境为 Distrobox ubuntu2404 / Ubuntu 24.04.5、Jazzy、Python 3.12.3、OpenCV 4.6.0、NumPy 1.26.4。新增 camera_calibration/image_proc 5.0.13、camera_info_manager/manager_py 5.1.8 及必要依赖；没有改宿主驱动和用户全局环境。当前容器没有可用 /dev/video*，因此无实拍结果。

固定种子生成 83 张训练、15 张独立验证、12 张正面和 94 对双目图；求解不读取 truth.json。主要实际结果：

| 对照 | 实际输出 | 解释 |
| --- | --- | --- |
| 多姿态 / 正面 | RMS 0.254637 / 0.262881 pixel；fx 559.70 / 2493.39 | 正面低残差仍可能约束不足，真实生成 fx=560。 |
| 同一验证000 | RMS 0.337428 / 1.207639；最大残差0.552163 / 2.961584 pixel | 固定内参，只估该照片位姿；不是独立外部真值。 |
| 方格0.025→25 | K 最大差约0.000028 pixel；平移倍率中位数999.999991 | 像素内参基本不变，空间尺度大1000倍。 |
| Gamma | 2.2/1/0.5 全部运行，128映射186/128/64 | Bayer48/BGR144字节、中心[50,100,200]；Gamma1全表恒等。 |
| 光子100/400/900 | 理论相对标准差10%/5%/3.33%，实际抽样与保存通过 | 数值模型已声明，不能倒推原教材照片的噪声参数。 |
| 景深 | N4近1526.72/远2898.55 mm；N8近1234.57/远5263.16 mm；s7000远界null | 同单位、明确判据，远界无穷不输出负距离。 |
| 服务 / 重启 | 错尺寸/零焦距拒绝，不覆盖已有文件；有效参数写盘并重启读回 | 保存与持久化实际成立，不只查看一次参数。 |
| image_proc | 同时间戳/光学frame/mono8，真实输出与相同模型 remap 最大差0 | 验证使用链路，仍需另查模型质量。 |
| 双目 | 93有效对、基线0.11994681 m、纵向RMS0.09093007 pixel | 使用拟合图的残差，实机独立验证与双目GUI仍未完成。 |

所有故意错误都限定在临时输出目录；不提交生成的数百张图片或归档。GUI 样本40时 Size覆盖仅约0.747，实际源码也允许 len(db)>=40 开放按钮，正文明确按钮可用不代表质量已合格。ROS 其他发行版只说明适用差异，不当作已经运行。

## 图片和 PDF

| 原文件 | 检查后文件 | 处理 |
| --- | --- | --- |
| rolling_shutter.png | rolling_shutter_revised.png | 球杆照片像素不变，正文解释受控实拍边界。 |
| raw.png / poisson.png / x.png | raw_revised.png / poisson_revised.png / camera_multiplicative_revised.png | 像素不变，合并与既有 Gaussian/salt 的五图对照，生成参数未知。 |
| gamma.png | camera_gamma_revised.pdf | 中文青色矢量保留两条幂律、恒等线与0.218→0.5；加入实际坡道/LUT，不保留不知条件的人像作为数据。 |
| diffuse_circle.png / aperture.png | camera_focus_revised.pdf | 合并薄透镜光束、传感器偏离合焦面、孔径与弥散圆截面，景深/焦深与衍射条件写明。 |
| depth_of_field.png / simple.png | camera_dof_revised.pdf | 保留前后/总景深及远距离近似，补有限远界与单位条件；不按距离比例画。 |
| 新 GUI 图 | camera_sampling_revised.png / camera_calibrated_revised.png | 实际界面原像素，采样与按钮状态明确；没有为配色修改输出。 |

3 张矢量图与 2 张 GUI 图先以 candidate 查看；focus 底部说明重叠已修复，再检查正文实际尺寸。发布改名的文件散列前后一致。没有其他章节调用旧图后才移除被替代原文件；tex 无重命名/移动，未改共享模板。

实际查看物理页4–5、130–158、228–231，覆盖目录、前章末、相机全章、后章首和完整题解；修改函数分段及两道综合题后再次核对149–158、228–231。最终235页，引用稳定，无overfull、未定义引用和缺资源。模板既有字体形状替代提示仍在，已看页面无缺字或错误编号。

模型核对采用 [OpenCV 4.6 官方接口](https://docs.opencv.org/4.6.0/d9/d0c/group__calib3d.html)、[Jazzy 标定器源码](https://github.com/ros-perception/image_pipeline/tree/jazzy/camera_calibration) 和 [CameraInfo 定义](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/CameraInfo.msg)；查表示例来自 [Basler 官方规格](https://docs.baslerweb.com/aca1920-155um)，曝光单位见 [Basler Exposure Time](https://docs.baslerweb.com/exposure-time)，景深/焦深条件与 [Edmund Optics 说明](https://www.edmundoptics.com/knowledge-center/application-notes/imaging/depth-of-field-and-depth-of-focus/) 交叉核对。

交付完整 TeX diff 为 /tmp/volume-2-chapter-7.patch；对应本章单独提交。未完成项需要物理设备或实际双目 GUI 补测才能改为通过。
