# IDE 界面配图

2026-09-14 在 Windows 本机用已安装软件截图，未使用合成界面。图像按捕获数据的实际 JPEG 格式保存。

- `clion-overview.jpg`：CLion 2025.1.3，工程文件树、源码、顶部运行控件和运行输出。
- `clion-cmake.jpg`：CLion 打开项目向导，Debug、MinGW、Ninja 与构建目录。
- `clion-debug.jpg`：CLion 在 main.cpp 第 11 行执行前暂停，score=60、bonus=15。
- `vscode-overview.jpg`：VS Code 1.137.0 中文界面，工程文件树、源码、集成终端和 total=75。
- `vscode-debug.jpg`：VS Code 在第 12 行执行前暂停，顶部调试工具栏、变量与调用栈，total=75。

示例来自 `../../examples/ide-demo`。CLion 截图使用其捆绑 MinGW；VS Code 使用本机已有的 GCC 8.1.0 MinGW、GDB 及 CMake Tools 1.24.42 / C/C++ 1.34.4。两者都已完成构建、运行和断点暂停验证。正文为新安装的 Windows 环境介绍 MSYS2 UCRT64 路线，Ubuntu 则使用系统 GCC，未在本机重新安装这些工具。

更新截图时打开这份小工程，核对版本、按钮提示和输出。不要截取无关项目、账号弹窗或凭据；截图位置改变时同步修改正文的位置说明。

## 2026-09-29 Ubuntu 补跑

正文的两张 VS Code 图现使用下列实际截图，旧 JPEG 保留作历史资源：

- `vscode-overview.jpg` → `vscode_run_revised.png`：Ubuntu 24.04.5 Distrobox 中复用主机 VS Code 1.139.1，CMake Tools 1.24.42、C/C++ 1.34.4，系统 GCC 13.3、GDB 15.1。真实符号重命名后，只有 main 的局部变量及其引用改为 reward，函数形参 bonus 保留；构建退出 0，终端输出 total = 75。
- `vscode-debug.jpg` → `vscode_debug_revised.png`：实际 Debug 构建，执行第 11 行后停在第 12 行，score=60、bonus=15、total=75；原始截图保留，正文仅用 LaTeX trim 裁去无关区域，没有修改界面或输出。

独立 Xvfb、临时 user-data/shared-data/XDG 配置中操作，集成终端明确选择已经安装的 `Maple Mono NF CN`，实际查看 Nerd 图标正常显示。未修改个人编辑器字体设置。两图实际查看原始像素及卷一物理页 62、66 后才加 revised 标记。

逐步运行/失败诊断/源码与截图散列见 `../../../docs/revision/evidence/volume-1-chapter-1-vscode-gui.json`。截图工具 `../../../scripts/capture_vscode_gui.py` 只提供隔离、按键/点击和截图，不替换 VS Code/CMake/调试器的实现；本次完整流程使用先前临时控制器，新工具另行验证了启动、真实终端字体与退出清理。复跑时检查屏幕状态再发送动作，不盲目使用旧坐标。

## CLion Ubuntu 补跑

三张历史 CLion 图现由 CLion 2026.2.3 在 Ubuntu 24.04.5 的实际操作截图替代，旧 JPEG 保留：

- clion-overview.jpg → clion_run_revised.png：独立教学副本、Debug 构建、Run 输出 total = 75，退出 0。
- clion-cmake.jpg → clion_cmake_revised.png：实际 CMake 设置，Debug、默认本机 GCC 工具链、Ninja、cmake-build-debug；不是旧版首次打开向导。
- clion-debug.jpg → clion_debug_revised.png：实际执行赋值后停在第 12 行，score=60、bonus=15、total=75。

官方包 SHA256 校验后在临时目录启动正常匿名试用；用隔离配置和 Xvfb，未登录或修改个人编辑器配置。GCC 13.3、捆绑 CMake 4.3.1 / Ninja 1.13.2 / GDB 17.1；编辑区/控制台/终端使用实际已装 Maple Mono NF CN，终端 Nerd 字形实际检查无方框。只调整真实窗口/侧栏与字体，PNG 保留原像素，正文 trim 裁边。候选原图与正文物理页 58/60/65 实际检查后才标记 revised；原始过程、失败的弹窗遮挡诊断、80 分变体与复原记录见 ../../../docs/revision/evidence/volume-1-chapter-1-clion-gui.json。
