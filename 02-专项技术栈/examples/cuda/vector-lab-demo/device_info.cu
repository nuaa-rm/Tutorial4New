#include "common.cuh"

int main() {
    int count, runtime, driver;
    CUDA_CHECK(cudaGetDeviceCount(&count));
    CUDA_CHECK(cudaRuntimeGetVersion(&runtime));
    CUDA_CHECK(cudaDriverGetVersion(&driver));
    std::printf("设备数=%d runtime=%d driver-api=%d\n", count, runtime, driver);
    if (count == 0) return 2;
    CUDA_CHECK(cudaSetDevice(0));
    cudaDeviceProp p{};
    CUDA_CHECK(cudaGetDeviceProperties(&p, 0));
    std::printf("设备0=%s compute=%d.%d 最大块线程=%d 设备内存=%zu\n",
                p.name, p.major, p.minor, p.maxThreadsPerBlock, p.totalGlobalMem);
    // 确认运行时能实际分配设备内存，不只查询管理工具。
    Buffer probe(1);
}
