# IDE 界面配图

2026-09-14 在 Windows 本机用已安装软件截图，未使用合成界面。图像按捕获数据的实际 JPEG 格式保存。

- `clion-overview.jpg`：CLion 2025.1.3，工程文件树、源码、顶部运行控件和运行输出。
- `clion-cmake.jpg`：CLion 打开项目向导，Debug、MinGW、Ninja 与构建目录。
- `clion-debug.jpg`：CLion 在 main.cpp 第 11 行执行前暂停，score=60、bonus=15。
- `vscode-overview.jpg`：VS Code 1.137.0 中文界面，工程文件树、源码、集成终端和 total=75。
- `vscode-debug.jpg`：VS Code 在第 12 行执行前暂停，顶部调试工具栏、变量与调用栈，total=75。

示例来自 `../../examples/ide-demo`。CLion 截图使用其捆绑 MinGW；VS Code 使用本机已有的 GCC 8.1.0 MinGW、GDB 及 CMake Tools 1.24.42 / C/C++ 1.34.4。两者都已完成构建、运行和断点暂停验证。正文为新安装的 Windows 环境介绍 MSYS2 UCRT64 路线，Ubuntu 则使用系统 GCC，未在本机重新安装这些工具。

更新截图时打开这份小工程，核对版本、按钮提示和输出。不要截取无关项目、账号弹窗或凭据；截图位置改变时同步修改正文的位置说明。
