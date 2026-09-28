# CLion 与 VS Code 共用示例

将本目录复制到自己的练习目录，用 CLion 的 Open 或 VS Code 的 Open Folder 打开。

- 需要支持 C++17 的编译器、CMake 3.16 或更高版本，以及对应构建工具。
- CLion：选择 Debug 工具链配置，等待 CMake 加载，构建并运行 `ide_demo`。
- VS Code：安装 Microsoft C/C++ 与 CMake Tools，选择 Kit 和 Debug Variant，依次执行 CMake: Configure、CMake: Build、CMake: Run Without Debugging。
- 预期输出：`total = 75`，正常退出。
- 调试：在 main.cpp 第 11 行放断点，使用 CLion Debug 或 CMake: Debug。暂停行尚未执行；步过后 total=75。

两套软件分别使用 `cmake-build-debug` 和 `build`（或 `build-vscode`）目录，避免共用 CMake 缓存。详细按钮说明见第一章“CLion 与 VS Code 开发环境”。
