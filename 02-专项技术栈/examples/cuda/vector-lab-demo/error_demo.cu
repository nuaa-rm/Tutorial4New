#include "common.cuh"
#undef NDEBUG // 错误示例在 Release 下也要保留设备断言。
#include <cassert>

__global__ void emptyKernel() {}
__global__ void executionError() { assert(false); }
__global__ void memoryError(float* p) { p[1] = 7.f; }

int main(int argc, char** argv) {
    std::string mode = argc > 1 ? argv[1] : "launch";
    if (mode != "launch" && mode != "execute" && mode != "memory") return 2;
    Buffer data(1);
    if (mode == "launch") emptyKernel<<<1, 1025>>>();
    else if (mode == "execute") executionError<<<1, 1>>>();
    else memoryError<<<1, 1>>>(data.p); // 仅在 memcheck 下演示，独立进程。
    CUDA_CHECK(cudaGetLastError());
    std::puts("启动检查通过，继续检查执行");
    CUDA_CHECK(cudaDeviceSynchronize());
}
