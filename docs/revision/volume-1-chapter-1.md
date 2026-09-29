# 卷一第一章：Linux 工作环境修订记录

本章文字、题解与演示项目已整理，真实安装/恢复、图形软件操作和板端实验仍有未验证项。**不能据此宣称 skill 全部验收通过。** 后续按卷、按章继续，最后统一处理仍缺环境的验证。

## 语言与内容

以修订前 `c5543bb` 中的 `Chapter1/11.tex`、`12.tex`、`13.tex` 为语言参照：保留四步安装的推进方式、操作中的“首先/然后/这时候”、给系统照相与“数字生命”等表达。新补的 Shell、Git、Conda 讲解也先承接实际问题，再带着操作并解释原因。保留原有轻松口吻，纠正单位、分区、密码、备份范围等技术结论；不把危险操作写成可以随手试错。

- UEFI/GPT 路线区分 ESP 与 `/boot`，保留 Windows/ESP，不把 swap 挂成 `/swap`；增加写盘前核对和完成后双系统验证。扩容先查占用，再准备备份与离线计划。
- Timeshift 明确默认排除个人数据。原先直接打包/覆盖运行中根目录的路线改为临时目录恢复实验，实际验证同名文件恢复与额外文件保留。
- 文件系统保留命令表与讲解，纠正挂载、usr-merge、权限、链接、apt update、重定向等易错点。Shell 项目比较普通变量、export、source；Git 项目用本地裸仓库演示真实提交交换。
- 保留已有 IDE 界面教程和教学工程，补终端验证与源码协作讲解；串口正文直接引入可运行软件回环源码，并明确回环的验证边界。
- 38 道随堂练习、12 道章末习题均有标签和可定位题解。题解按正文顺序排列，CLion/VS Code 的修改与调试共用题解。12 题保留是因为本章涵盖系统安装、文件、Shell、Git、IDE、串口及选修环境管理；没有按子文件机械凑题。

## 20 项检查

状态仅针对本章。本章没有“不适用”项。

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | `main.tex` 第一章 introduction：可验证目标、建议学时、本卷边界齐全。 |
| 2 核心小节示例 | 通过 | 下表逐节列出覆盖；四步安装、Timeshift 恢复和 IDE 界面使用连续操作示例，给出前提、操作与结果判断。 |
| 3 复杂概念项目 | 通过 | `examples/shell-environment-demo`、`git-workflow-demo`、`serial-loop-demo`，复用 `ide-demo`；源码、依赖与 README 齐全。 |
| 4 正文讲清项目 | 通过 | `14_shell.tex`、`15.tex`、`17_ide.tex`、`18_serial.tex` 展示文件结构/文件组成、完整核心代码与执行顺序；源码直接用 lstinputlisting 引入。 |
| 5 命令语法参数 | 通过 | `14_fs.tex` 参数表，Shell/Git/Conda/归档/串口各节说明参数与可替换路径；实际设备名、UEFI 和 Shell 条件不照抄。 |
| 6 随堂练习 | 通过 | 38 个 exercise，逐节任务见覆盖表；IDE 安装、界面、调试由综合练习明确分项。 |
| 7 难点归纳 | 通过 | UEFI/GPT、备份边界、链接、Vim 模式、环境继承、Git 区域、Conda、IDE、串口有 conclusion 或对应对比表。 |
| 8 易错与危险提示 | 通过 | 写盘/格式化、tar 覆盖、rm、chmod、PATH、Git 丢弃历史、环境删除、接线和 udev 权限均在操作前说明影响。 |
| 9 本章小结 | 通过 | `main.tex` “本章小结”归纳安装维护、命令、Shell、Git、Conda、IDE 与串口的联系和掌握程度。 |
| 10 章末习题 | 通过 | 12 题含基础、提高、实践与选修自测；题量依据见上文，不与随堂任务仅换说法重复。 |
| 11 本章验收 | 通过 | `main.tex` “本章验收”检查独立演示；无硬件时注明板端待补，不把软件回环当板端通过。 |
| 12 答案定位 | 通过 | `answers.tex` 每道题使用 ref 指向题目；结构脚本核验 38+12 对应。开放题给可行流程和判断标准。 |
| 13 作者语言习惯 | 通过 | 对照原 11/12/13 的连贯段落、自然过渡与条件选择修订，不沿用错误单位和技术结论。 |
| 14 图片实际检查 | 通过 | 本轮查看原图及段落，现正文使用 25 张图；四张机制图重绘；2026-09-29 两张 VS Code 图换为 Ubuntu 实测，原始截图与正文尺寸实际检查；旧安装器照片注明示例边界。 |
| 15 图片标记与引用 | 通过 | 四张重绘图与两张新 VS Code 截图经独立图和正文尺寸检查后使用 `_revised`；正文路径和生成脚本/IDE 图片说明一致。 |
| 16 文件组织 | 通过 | 保留 11/12/13 等编号文件，主文件清楚列出各节主题；新项目用概念名目录，避免打断作者指定的文件参照。 |
| 17 包含与引用 | 通过 | 全卷后续章节整理后的入口展开 23 个文件、175 个标签、121 个被引用标签；本章 38+12 题定位通过，无失效资源、循环包含、重复标签或未定义引用。 |
| 18 源码和格式 | 通过 | 命令不再滥用数学模式；表格列宽/三线表、图注、标题、代码协调，短源码与参数表连续排版。较早 CRLF 文件统一为 LF。短代码前保留分页空间，文件系统参数表标题与表体一起排版；IDE 初始短比较表改为普通 tabular，避免四行表跨页。 |
| 19 示例实际运行 | **未完成** | Bash/Git/tar/链接/权限/筛选/Conda/CMake/GDB/pySerial、apt/zsh/AstroNvim 临时配置及 Ubuntu VS Code GUI 已实际完成；真实写盘/系统恢复、原生桌面与登录设置、CLion 当前 GUI、Windows 安装/工具链和物理串口未验证。详见下文及两份补跑证据。 |
| 20 编译和 PDF | 通过 | 原首次整理 179 页；全卷后续整理及本次 VS Code 换图后，XeLaTeX 两次生成 206 页，引用稳定。原目录、正文、题解检查保留，本次实际查看物理页 7–8、62–67 与 IDE 题解 172，无缺字/越界/未定义引用；共享模板未改。 |

## 核心能力覆盖

| 正文 | 示例与对应练习 |
| --- | --- |
| `11.tex` 系统分区、启动盘、安装、启动设置 | 四步连贯安装示例及 Try Ubuntu 检查；partition-plan、usb-image、installer-review、boot-order。 |
| `11.tex` 扩容、GRUB、桌面选修 | GParted 观察/离线计划、配置备份和默认项检查、主题与 Caffeine 操作；resize-plan、grub-plan、desktop-plugins。 |
| `12.tex` 快照、归档恢复 | 快照创建列表、连续目标恢复操作，tar 临时目录完整实验；snapshot、tar-options。 |
| `13.tex` 重装选修 | 从备份验证到分区保留再到构建工程的连续操作；reinstall-plan。 |
| `14_fs.tex` 目录/挂载、用户、资源、包 | 查看设备与挂载，id/whoami，free/uname/df/du，apt 安装 tree；fs-layout、user-info、disk-space、apt-package。 |
| `14_fs.tex` 文件/链接/权限/归档、查找/管道、编辑 | 文件操作、硬软链接复制、755、grep/重定向、Vim 编辑退出；file-ops、links-permissions-archive、find-python、pipe-count、vim-edit。 |
| `14_fs.tex` AstroNvim 选修 | 新版 Neovim 安装、备份旧配置、模板及搜索操作；astronvim。 |
| `14_shell.tex` Shell、脚本、配置、环境、zsh | 简单脚本、别名、父子项目、PATH、连续 zsh 教程；shell-script、shell-alias、shell-inheritance、shell-path、zsh-config。Shell/终端关系归入脚本练习的解释器选择。 |
| `15.tex` 四区/身份、交换、分支、忽略 | 安装检查归入 Git 配置练习；仓库身份、两次交换项目、快进合并、例外规则；git-config、git-commits、git-branch、git-ignore。 |
| `16.tex` 环境管理选修 | 配置来源读取及单独的 Python/NumPy 环境；conda-config、conda-env。 |
| `17_ide.tex` 安装、工程、界面、构建、调试与排错 | 两套 GUI 连续教程和同一 CMake 工程；ide-clion/ide-vscode 分别练修改调试，ide-setup 明确覆盖安装、工程协作、界面、构建入口、工具栏与错误判断。 |
| `18_serial.tex` 接线、设备权限、命名、设置、收发、排错 | 接线核对、插拔识别、udev、stty、板端约定/TTL 回环、软件回环、fuser；serial-device、serial-udev、serial-bytes、serial-diagnosis。diagnosis 分项覆盖连接类型、参数意义和故障层次。 |

## 首次修订的实际运行与边界

- Arch 主机 Bash 5.3.20、Git 2.55.0：父子变量三组对照、本地/远程两次及第三次提交、快进分支、忽略例外、正文 tar 恢复、硬软链接复制、755、grep 与重定向成功。日志：`evidence/volume-1-chapter-1-shell-git-tar.txt`。
- Miniforge3/Conda 26.7.2 临时安装：官方 SHA256 校验通过，Python 3.10.21、NumPy 2.2.6；配置读取、关闭自动激活、创建/激活/导入/退出/删除成功。此版本提示 auto_activate_base 是 auto_activate 的别名，正文已有版本差异提示。测试写配置使用 `--file /tmp/tutorial-conda/.condarc`，没有改用户登录配置。日志：`evidence/volume-1-chapter-1-conda.txt`。
- Distrobox `ubuntu2404` 实际为 Ubuntu 24.04.5 / ROS 2 Jazzy。安装缺少的 python3-serial、gdb、python3-venv 等依赖；系统 Python + pySerial 3.5 回环实测 hello 和二进制变体，十六进制分别为 `68 65 6c 6c 6f 0a`、`00 41 ff 0a`，超时读取为空。
- 同一容器 GCC 13.3 / CMake 构建 ide-demo 输出 `total = 75`。GDB 15.1 断点读到 score=60、bonus=15，步入/步过/返回后 result=75、total=75，程序正常退出。这验证程序与命令行调试，没有代替两套 GUI 的实际点击。
- **尚缺验证环境**：Windows+UEFI 实际压缩/写 USB/安装/启动切换、Live 扩容、Timeshift 系统恢复与重装、当前 GNOME/GRUB/zsh/AstroNvim 新配置过程、CLion/VS Code 当前 GUI 全流程、真实 USB CDC ACM 板/TTL 接线、udev 身份绑定与板端协议。软件安装/配置的后续补跑见本文末尾：apt、AstroNvim与zsh临时安装及配置已实际完成，原生桌面与登录切换仍待验证。保留操作前提与验证标准，不盲目改主力系统来凑验证。
- 已有五张 IDE 真实截图用于认按钮，界面版本为 CLion 2025.1.3、VS Code 1.137.0 Windows 中文界面；本次没有把历史截图当作当前操作实测。

## 图片与 LaTeX 整理

| 原图 | 正文新图 | 调整 |
| --- | --- | --- |
| `images/linux7.jpg` | `images/linux-directory_revised.pdf` | 统一青色矢量线框、字体与目录术语，说明 usr-merge；保留主要树形关系。 |
| `images/linux8.png` | `images/mount_revised.pdf` | 区分设备节点、文件系统与挂载点，避免误把设备文件当内容目录。 |
| `images/shell.png` | `images/shell_revised.pdf` | 用户空间应用经系统调用使用内核，不把 Shell 画成所有程序必经的编译层。 |
| `images/git.png` | `images/git-workflow_revised.pdf` | 四区关系和真实命令方向，统一字体、箭头与配色，说明 diff 两种比较位置。 |

旧图保留为历史资源，第一章引用已切换；没有重命名或移动 .tex 文件。淘汰本章中与 UEFI/GPT 路线冲突的 install5/install6 图和过时快捷键表引用，真实截图不篡改。图生成脚本区分 candidate 与检查后的 revised 输出。源文件直接引入项目代码；题解从手写题号改为标签引用，避免新增习题导致串号。新增结构脚本只检查路径、标签和题解定位，不冒充内容、运行或视觉验收。

编译日志中尚存第二章原有的越界警告，将在第二章修订中处理；不把第一章通过扩大为整卷版面通过。

## 全书收尾补跑：包管理、zsh 与 AstroNvim

补跑证据见evidence/volume-1-chapter-1-extra-tools.json。Ubuntu中实际执行apt update、search cowsay、install tree/cowsay/ripgrep/gcc；tree列出1目录1文件，cowsay输出hello textbook，再remove本次新装cowsay并核对未安装。复用已有Neovim0.12.5，不重复写/opt。

审阅官方Oh My Zsh安装脚本后，用临时ZDOTDIR/ZSH与--unattended实际安装；克隆p10k、autosuggestions、syntax-highlighting，设置主题/插件并验证三个函数可用和别名输出migrated_alias。实际PTY完成p10k向导，ASCII/Lean/256色/两行/紧凑等选择保存临时.p10k.zsh与.zshrc，原始选择输出及源码散列保留；没有虚构用户终端字体显示或修改登录shell。

临时XDG配置、数据、状态和缓存中按官方模板安装AstroNvim6系列与插件，9种语法解析器实际编译/安装。用Neovim输入接口执行Space-ff，真实选择器找到hello.txt；退出输入模式后确认并打开其实际缓冲区，读到hello textbook；Space-fw输入textbook找到hello.txt第1行第7列。初次自动确认尚在insert模式，缓冲区未打开；保存失败诊断，增加Esc和状态等待后实际成功，没有改搜索实现。执行LspInstall clangd，Mason安装后实际运行clangd23.1.0，退出0。遵循官方0.11+需求及搜索/LSP入口：[AstroNvim](https://docs.astronvim.com/)，向导与临时配置参考[Powerlevel10k](https://github.com/romkatv/powerlevel10k)。

这次包管理/Shell 补跑移除了 apt tree/cowsay、AstroNvim 模板/插件/搜索/LSP、zsh 框架/主题/插件及别名配置的软件缺口，未改正文和图片。登录 shell、原生桌面、双系统写盘/备份恢复、IDE GUI 和物理串口当时仍待验证；后续 VS Code 补跑见下文。

## 全书收尾补跑：VS Code GUI 与终端字体

证据见 `evidence/volume-1-chapter-1-vscode-gui.json`。Ubuntu 24.04.5 中复用主机 VS Code 1.139.1、现有 CMake Tools 1.24.42 与 C/C++ 1.34.4；在独立 Xvfb、临时 user-data/shared-data/XDG 目录中打开 ide-demo 的副本。真实选择 GCC 13.3 与 Debug，配置和构建退出 0，Run Without Debugging 的真实终端输出 total = 75。系统没装 Ninja，本次扩展选择 Unix Makefiles，未把无 Ninja 的探测日志当作构建失败。

真实断点停在第 11 行，score=60、bonus=15；total 尚未赋值，显示的旧内存值没有教学意义。步入后执行加法，result=75；步出仍可能停在赋值前的调用行，继续一步到第 12 行才确认 total=75。Continue 正常退出；Restart 重新停在断点，Stop 结束会话。容器中 GDB 报 controlling terminal 权限警告，这个不读取 stdin 的示例仍正常执行；保留原始提示，不推断所有终端交互程序都能忽略它。

搜索 bonus，真实跳转定义并执行 Rename Symbol。第一次过早保存使改名取消，源码仍未变化，保留失败诊断。重试后查看 Refactor Preview 并点击 Apply，只有 main 中局部声明和使用两处改为 reward，函数形参及函数内部的 bonus 两处保留；保存、构建退出 0、运行输出 75。随后实际 Undo/保存并构建，磁盘源码与随书原文件字节相等，SHA256 为 379f34aa12d5bea66c95c8e8de22753d324d655c10504b6b5152174a99749c17。

根据用户指出的白色方框问题，在本次临时 VS Code 配置中设置 terminal.integrated.fontFamily=Maple Mono NF CN；容器 fc-match 实际返回 MapleMono-NF-CN-Regular.ttf，查看终端截图确认系统/文件夹/箭头图标显示正常。正文增加单独选择集成终端字体的说明，以及命令面板核对完整动作名的提醒；最近使用项曾误选 Append Build Directory，不能把它算作 Build，纠正后才取得真正构建成功的记录。

两张历史 VS Code JPEG 的正文引用换为 vscode_run_revised.png、vscode_debug_revised.png，原图保留。真实 1600×1000 截图仅格式转换和正文 trim 裁边；先看原图、候选 PDF 物理页 62–67 和目录 7–8，再字节不变地加 revised 标记并编译复查。IDE 图片 README 同步，.tex 文件没有改名或移动。新增截图工具另行实测启动、字体和退出，完整语义操作使用临时控制器，证据区分两次运行。

第19项仍未完成：本次没有重跑 Windows 软件安装/工具链、CLion 当前 GUI、UEFI 双系统写盘/系统恢复、GNOME/GRUB/登录 shell 或物理串口。临时 Ubuntu GUI 验证也不代替用户桌面集成验证。所有本次启动进程已经退出，检查两组明确临时配置路径没有残留 VS Code 进程。

## IDE 正文排版与工具链补充

进一步复查发现 17_ide.tex 开头误用了 begin{center}，末尾却是 endgroup，长正文被居中。改为与末尾对应的 begingroup，保留局部表格/图片的居中与 emergencystretch 分组；正文恢复普通段落排版，与相邻 11/12/13 一致。新字体配置名改用可换行的 ASCII path，修复取消居中后出现的 22.19pt 越界，没有改变配置项内容。

实际检查 IDE 全节物理页55–67、目录7–8、题解172；两次最终 XeLaTeX 编译仍为206页，无缺字/越界/未定义引用，题解与标签定位通过。此前整段居中的版面问题未被早期检查发现，本次修正后更新最终检查依据。

VS Code 当时因缺 Ninja 使用 Unix Makefiles，这次补装 Ubuntu ninja-build 1.11.1。在独立 ninja-build 目录用 -G Ninja、Debug 实际配置、构建并运行同一 ide-demo，输出 total = 75，退出0。补充日志保留在 VS Code 证据的 toolchain_followup；原 GUI 流程仍只按当时实际使用的 Makefiles 记录，未声称补装后又做了 Ninja GUI 验证。
