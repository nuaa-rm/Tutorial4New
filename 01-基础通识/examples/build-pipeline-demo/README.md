# 从 C++ 源码到可交付程序

配合卷一第三章：观察编译四阶段，比较配置/构建/安装，验证多文件、库、公开使用要求和外部依赖。各子目录独立构建，不需要 ROS。Ubuntu 22.04/24.04 中安装 `build-essential cmake libopencv-dev`；实际验证环境为 GCC 13.3、CMake 3.28.3、OpenCV 4.6。显示图片需要桌面。

先将本目录复制到自己的练习目录，所有命令在复制后的子目录执行，避免改动教材原版。

## stages：编译四阶段

在 `stages` 运行：

```bash
g++ -std=c++17 -E hello.cpp -o hello.ii
g++ -std=c++17 -S hello.ii -o hello.s
g++ -c hello.s -o hello.o
g++ hello.o -o hello
./hello
```

依次得到预处理文本、汇编、目标文件、程序，输出 `armor=3` 和 `function=main`。在 hello.ii 中可找到宏展开后的编号。

## hello-cmake：配置与构建

在 `hello-cmake` 运行：

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --parallel 2
./build/hello
```

配置打印 training_armor 和编译器路径，运行仍输出上面的两行。改目标名时，同步改 `add_executable` 与 `target_compile_features`，再用空构建目录验证。

## armor-demo：多文件、库、模块与安装

在 `armor-demo` 先验证手动编译：

```bash
g++ -std=c++17 -I include src/main.cpp src/armor.cpp -o armor_manual
./armor_manual
```

输出 `score=30`。include/armor.hpp 声明接口，src/armor.cpp 定义实现，src/main.cpp 调用接口。最终 CMakeLists.txt 将实现构建成静态库，PUBLIC 传播头文件目录；载入 Function.cmake 后打印编译器、构建类型与未定义变量。

```bash
cmake -S . -B build-lib -DCMAKE_BUILD_TYPE=Debug
cmake --build build-lib --parallel 2
./build-lib/armor_demo
cmake --install build-lib --prefix "$PWD/stage"
./stage/bin/armor_demo
```

两次均输出 `score=30`，生成 libarmor.a；安装只复制程序到 stage/bin，无需 sudo。安装前必须先构建。

`cmake/Multifile.cmake` 保存未拆库的版本，`cmake/Static.cmake` 保存拆库后尚未加入模块/安装规则的版本。复现正文对应阶段时，在工程副本中把相应文件复制成 CMakeLists.txt；直接运行原版则得到最终阶段。`-DSAVE_OUTPUT=ON` 后重新构建，多一行 `save output enabled`，仅演示编译宏，不保存文件。

把 STATIC 改为 SHARED 后用新的 build-shared 目录构建，得到 libarmor.so，构建目录内运行仍输出30分。实验后恢复 STATIC。源文件乘数改为20后只需构建，分数变60；PUBLIC 改 PRIVATE 后，库能编译，主程序因未收到头文件目录而失败。

## opencv-demo：查找、链接与运行

在 `opencv-demo` 运行：

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --parallel 2
./build/image_viewer test.ppm
```

输出 `size=2x2`，窗口显示红/绿/蓝/白四个像素，按任意键结束。test.ppm 是可直接阅读的文本样本，正文也给出生成命令。不传参数退出1；传 missing.png 退出2，紧接着用 `echo $?` 读取状态。

无桌面时先运行这两条错误路径，不能把它们当作显示窗口通过。自装 OpenCV 时，OpenCV_DIR 指向包含 OpenCVConfig.cmake 的目录；find_package 不替你安装开发包。完整图像算法在卷二展开。
