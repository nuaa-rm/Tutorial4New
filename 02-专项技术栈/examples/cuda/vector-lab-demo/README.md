# CUDA 向量实验

在当前目录执行命令。依赖兼容 NVIDIA GPU/驱动、CUDA 编译及 cudart 开发包、GCC、CMake。已在 Distrobox ubuntu2404 / Ubuntu 24.04.5 / GCC 13.3 / CUDA 12.6.3 / RTX 3070 Ti Laptop（计算能力 8.6）运行。安装方法见教材；这里不安装宿主驱动。无 GPU 的 cpu_demo 可单独由 g++ 编译。

~~~bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.6/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=86
cmake --build build -j2
./build/cpu_demo
./build/device_info
./build/vec_add
./build/vec_add 257 256
./build/shared_sum 513 256
./build/pipeline
./build/pipeline 257 3
~~~

86 来自实测计算能力 8.6，换设备须换成自己的架构；编译器路径同样不能照搬到其他安装。vec_add 参数是长度和块线程数，默认 1048579 / 256，校验全部元素并打印边界与传输量。shared_sum 默认 513 / 256，块大小只接受 32..512 的二次幂，补零后归约，前三块为 896/896/0，总和 1792。普通浮点数据不能据此要求跨算法完全相等。

pipeline 参数为长度和奇数重复次数（默认 1048579 / 7）。三步为乘 2、加 1、限幅；比较单线程 CPU 三遍处理、GPU 中间结果留存和每步往返。输出 JSON 为预热后的中位数，CPU 和 GPU 完整处理阶段用主机稳态时钟，GPU 三个核区间另用事件测量。包含指定传输和启动/同步，但排除上下文初始化、内存分配、数据生成和结果校验；不是相机端到端延迟。所有路径逐元素校验，数值越小不代表其他任务也越快。

错误示例必须用独立进程。下列两条预期返回 1；execute 触发本进程设备断言，后续操作另启程序：

~~~bash
./build/error_demo launch
./build/error_demo execute
~~~

可安装 Compute Sanitizer，先 memcheck 查访问，再 racecheck 查共享内存冲突，synccheck 查同步。--error-exitcode 9 使工具发现错误时也返回失败。最后一条故意写越界，预期工具发现错误，不能算正常通过；仅在 memcheck 下运行 memory 模式。

~~~bash
/usr/local/cuda-12.6/bin/compute-sanitizer --tool memcheck --error-exitcode 9 ./build/vec_add 257 256
/usr/local/cuda-12.6/bin/compute-sanitizer --tool memcheck --error-exitcode 9 ./build/shared_sum 513 256
/usr/local/cuda-12.6/bin/compute-sanitizer --tool racecheck --error-exitcode 9 ./build/shared_sum 513 256
/usr/local/cuda-12.6/bin/compute-sanitizer --tool synccheck --error-exitcode 9 ./build/shared_sum 513 256
/usr/local/cuda-12.6/bin/compute-sanitizer --tool memcheck --error-exitcode 9 ./build/error_demo memory
~~~

nvcc 直接构建同一源码：

~~~bash
/usr/local/cuda-12.6/bin/nvcc -O2 -std=c++17 -arch=sm_86 -lineinfo vec_add.cu -o /tmp/textbook-vec-add
/tmp/textbook-vec-add 257 256
~~~

项目不依赖 cuDNN/cuBLAS，也没有 TensorRT 引擎；这些是教材给出的后续方向。普通推理格式导出/比较使用前章的完整 LeNet 项目，不再复制一份。
