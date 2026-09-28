# 长空御风视觉组培训教材

南航长空御风战队视觉组新人培训用书。仓库由旧「合订本」拆为**三卷独立 LaTeX 工程**，每卷自带 `main.tex`，可单独编译 PDF。

| 项目 | 说明 |
|------|------|
| 版本 | 2026.09 |
| 排版 | [ElegantBook](https://github.com/ElegantLaTeX/ElegantBook) + XeLaTeX |
| 组内方向 | **自瞄** · **雷达** · **导航** |
| 远程 | `https://github.com/nuaa-rm/Tutorial4New.git` |

---

## 三卷分工

| 卷册 | 目录 | 定位 | 考核重心 |
|------|------|------|----------|
| **卷一 · 基础通识** | [`01-基础通识/`](01-基础通识/) | 全员必过：环境、C++、构建 | 能独立配置环境、写小工程、用 git |
| **卷二 · 专项技术栈** | [`02-专项技术栈/`](02-专项技术栈/) | 按方向选修的技能书 | 能在工程中落地对应模块 |
| **卷三 · RM 视觉概述** | [`03-RM视觉概述/`](03-RM视觉概述/) | 赛场链路与工程准则 | 能画链路、指接口、复述红线（不考手推公式） |

**边界速查**

| 问题类型 | 去哪卷 |
|----------|--------|
| 不会装 Ubuntu / CMake / 现代 C++ | 卷一 |
| 不会写 ROS2 节点、不懂 PnP / Kalman / SDR | 卷二 |
| 不知道自瞄三段怎么串、调车守什么规矩 | 卷三 |

---

## 培养路径

```
开营：精读卷三第 1、2、5 章（半天量级）
        │
        ▼
卷一通识考核通过（标 * 小节选修，不计入通识考核）
        │
        ▼
按方向选修卷二 ──┬── 自瞄：ROS2 → OpenCV → 深度学习 → 相机 → 滤波 → BA → MPC（CUDA 建议）
                ├── 雷达：ROS2 → 多机通信 → SDR → OpenCV → 深度学习 → 相机（CUDA / 滤波建议）
                └── 导航：ROS2 → 导航章（相机 / 滤波 / 多机通信建议）
        │
        ▼
卷三中期链路答辩 → 进入实车 / 方向仓库
```

说明：

- 「识别」「CUDA」「激光雷达（LiDAR）」是**技能或器件**，不是与自瞄 / 雷达 / 导航并列的第四方向。
- 导航正文中的「激光雷达」指测距传感器；**雷达方向**指高台全场感知站，二者勿混称。

---

## 各卷目录概要

### 卷一 · 基础通识

入口：[`01-基础通识/main.tex`](01-基础通识/main.tex)

1. Linux 工作环境（安装、备份*、文件系统、Shell、Git、Conda*、CLion 与 VS Code 安装及图形界面操作、Linux 串口通信基础；选修小节含 zsh 美化*、AstroNvim*、桌面美化*）
2. 现代 C++（类、lambda / 引用与移动、智能指针、STL、多线程）
3. 编译过程与 CMake

前置页：认识技术组与视觉组、编者说明。

### 卷二 · 专项技术栈

入口：[`02-专项技术栈/main.tex`](02-专项技术栈/main.tex)

| 章 | 主题 | 正文 |
|----|------|------|
| ROS2 基础 | 节点、接口、完整工程、构建与排障 | `chapters/A_ros2.tex`、`A_ros2_project.tex`、`A_ros2_engineering.tex`、`A_ros2_review.tex` |
| 多机通信方法 | TCP / 串口帧、latest-value、故障隔离 | `chapters/J_comm.tex` |
| SDR 与电磁波解析 | IQ、分阶段状态机、解析流水线 | `chapters/K_sdr.tex` |
| OpenCV | Mat、HSV、滤波、轮廓、cv_bridge | `chapters/B_opencv.tex` |
| 神经网络与深度学习 | PyTorch、LeNet、YOLO / 部署入口 | `chapters/C_dl.tex` |
| CUDA 与 GPU 加速 | Toolkit 安装、Host/Device、kernel | `chapters/D_cuda.tex` |
| 相机与成像 | CMOS、曝光、噪声、标定入口 | `chapters/E_camera.tex` |
| 信号处理与滤波 | 低通、Kalman / EKF / UKF | `chapters/F_filter.tex` |
| 几何视觉与 BA | 投影、PnP、BA、附录 | `chapters/G_ba.tex` |
| 模型预测控制 | 云台动态、QP、滚动时域 | `chapters/H_mpc.tex` |
| 导航与 SLAM | Nav2、TF、代价地图、恢复与行为树 | `chapters/I_nav.tex` |

材料部分来自旧合订本、`最小二乘法` 讲义，以及公开雷达站架构实践（通信 / SDR 两章为概述，赛场参数以队内仓库与规则为准）。

### 卷三 · RM 视觉概述

入口：[`03-RM视觉概述/main.tex`](03-RM视觉概述/main.tex)

1. 视觉组职责与技术全景  
2. 自瞄系统概述  
3. 导航在 RM 中的应用  
4. 雷达站与全场感知概述  
5. 相机与前端赛场实践 checklist  
6. 工程准则与调车文化（五条）  
7. 进阶地图与资料索引（活页）

体例：**少公式、多框图与验收**；公式与实现回卷二。

---

## 仓库结构

```text
Tutorial4New/
├── README.md                 # 本说明
├── .gitignore
├── main.tex                  # 仅提示「请编各卷」的占位入口（勿当合订本）
├── 01-基础通识/               # 卷一
├── 02-专项技术栈/             # 卷二
├── 03-RM视觉概述/             # 卷三
├── templates/
│   ├── elegantbook.cls       # ElegantBook 类文件
│   ├── preamble.tex          # 共用导言、代码环境、封面入口
│   ├── cover.tex             # 三卷共用封面与内标题页
│   └── chapter-guide.md      # 章节编写与改造规范（完整版）
├── .claude/skills/
│   └── textbook-chapter/     # 章节编写规范（AI 摘要版，与 chapter-guide.md 同步维护）
├── cumcmthesis.cls           # 旧数模模板（已弃用，仅本地对照）
├── assets/covers/            # 共用插画、三卷封面 PDF、预览与复用说明
└── 长空御风.png              # 原始队徽素材
```

封面使用与正文一致的青色主题，三卷通过 `\TextbookVolume{1/2/3}` 切换卷号和导览内容。单独的封面 PDF 与重建方式见 [封面素材说明](assets/covers/README.md)。

本地可有但不纳入 git（见 `.gitignore`）：

- `_legacy/`：旧合订本 Chapter1–11 等归档（含旧图）
- `参考文献/`：讲义 PDF、PPT、宣传文案等大附件

各卷目录内：

- `elegantbook.cls` → 符号链接到 `../templates/elegantbook.cls`
- `images/`：本卷插图（实体目录，非共用根目录）
- 编译产物 `main.pdf`、`*.aux` 等由 `.gitignore` 忽略，需本地 `xelatex` 生成

---

## 编译说明

### 依赖

- TeX Live（或 MacTeX）完整环境，**XeLaTeX**
- 中文字体：macOS 上 ElegantBook + `chinesefont=ctexfont` 通常走系统宋黑；Linux 请保证 ctex 字体集可用
- 可选：`latexmk -xelatex main.tex`

### 命令

```bash
# 任选一卷，建议编译两次以生成目录
cd 01-基础通识    # 或 02-专项技术栈 / 03-RM视觉概述
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

封面图由 [`templates/preamble.tex`](templates/preamble.tex) 中的 `\cover{cover.png}` 指定，经 `\graphicspath` 从各卷 `images/` 读取。

### 常见问题

| 现象 | 处理 |
|------|------|
| 找不到中文字体 / `STHeiti` | 检查 ctex 字体集；或改 `chinesefont` 选项 |
| 找不到图片 | 确认在卷目录下编译，且图片已放入该卷 `images/` |
| 根目录 `main.tex` 只有一页提示 | 预期行为；请进入三卷子目录编译 |

---

## 排版与模板

- **当前**：ElegantBook（`lang=cn`，`scheme=chinese` → 「第一章 …」），主题色 cyan，`mode=fancy`
- **已弃用**：`cumcmthesis.cls`（数模竞赛模板，不适合教材）
- **共用**：[`templates/preamble.tex`](templates/preamble.tex) 提供 `tcode` / `tpython` / `tbash`、listings 对 CMake/XML 的支持、标题层级映射、`example` 环境中文名（显示为「示例」）等
- **备选**：若 ElegantBook 过重，可改为 `ctexbook`，导言仍可复用

章首「学习目标 / 学时 / 边界」使用 ElegantBook 的 `introduction`（内容提要）环境；章节结构（示例 / 随堂练习 / 难点小结 / 章末习题与验收）与语言口吻规范见 [`templates/chapter-guide.md`](templates/chapter-guide.md)，撰写或改造章节前请先阅读。

---

## 工程准则（摘要）

完整条文见卷三「工程准则与调车文化」，开营 / 结营建议各读一次：

1. 实测优先，仿真为辅  
2. 边测边写，过程正确比结果正确更重要  
3. 拒绝重复造轮子；重构是学习，调车是工作  
4. 时间 / 进度 / 合作 / 钻研  
5. 先定位问题，再寻找解，切忌盲目乱试  

---

## 贡献与维护

1. **改正文**：只改对应卷下的 `.tex`，不要改 `_legacy/`（除非刻意归档）。
2. **写章节**：遵循 [`templates/chapter-guide.md`](templates/chapter-guide.md) 的章节规范（章首提要、示例 / 练习 / 小结、章末习题与验收、语言口吻）。
3. **改模板**：优先改 `templates/preamble.tex`；类文件升级时同步 `templates/elegantbook.cls`。
4. **加图**：放入对应卷的 `images/`，正文用相对文件名即可（`\graphicspath` 含 `images/`）；插图缺失时可用 `\IfFileExists` 占位框过渡，不影响编译。
5. **勿提交**：各卷 `main.pdf`、LaTeX 中间文件、`.DS_Store`、`_legacy/`、`参考文献/`（见 [`.gitignore`](.gitignore)）。
6. **接口变更**：消息字段、坐标系、串口协议变更须同步文档与卷三索引活页中的责任人字段。

Issue / PR 请说明改动卷册与是否影响编译。

---

## 相关资料

- 队内大纲（文书侧）：`视觉培训/教材体系/`
- 自瞄公式讲义：`视觉培训/最小二乘法/`（BA / Kalman / MPC）
- 仓库内曾放置的 `参考文献/`、旧合订 `_legacy/`：**不上传**（本地保留即可，见 `.gitignore`）
- 雷达站公开参考实现（延伸阅读，注意许可与权重策略）：  
  [TCR-RM2026-Radar-OpenSource](https://github.com/coach114514/TCR-RM2026-Radar-OpenSource)

---

## 更新日志

- **2026-09-11**
  - 卷一第 1 章按章节编写规范改造：补齐示例、随堂练习、难点小结、易错警示，章末新增本章小结与 10 道习题
  - 新增选修小节：zsh 与终端美化*、AstroNvim*、桌面美化*（配图暂为占位框，待补截图）
  - 修正知识点错误（git 分支创建命令、apt 更新单个软件、HTTPS 克隆私有仓库、重定向与 vim 命令描述等）；修复 `\texttildelow` 字体缺字；`example` 环境显示名改为「示例」
  - 新增章节编写规范：`templates/chapter-guide.md`（完整版）与 `.claude/skills/textbook-chapter/`（AI 摘要版）
- **2026-08-24**
  - 合订本拆为三卷独立工程；改用 ElegantBook；封面接入队徽图
  - 完成卷一正文；卷二 ROS2 / 通信 / SDR / OpenCV / 深度学习 / CUDA / 相机 / 滤波 / BA / MPC / 导航
  - 完成卷三概述（自瞄 / 导航 / 雷达 / 相机 checklist / 工程五条 / 索引）
  - 统一三方向表述；旧章归档至 `_legacy/`
- 更早记录见 git history（合订本时期）
