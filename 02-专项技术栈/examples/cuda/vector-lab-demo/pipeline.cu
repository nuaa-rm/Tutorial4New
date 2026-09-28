#include "common.cuh"
#include "kernels.cuh"
#include <algorithm>
#include <chrono>
#include <vector>
using Clock = std::chrono::steady_clock;

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    return values[values.size() / 2];
}

int main(int argc, char** argv) {
    if (argc > 3) return 2;
    int n = argc > 1 ? number(argv[1], 1 << 24) : (1 << 20) + 3;
    int repeats = argc > 2 ? number(argv[2], 31) : 7;
    if (repeats % 2 == 0) return 2;
    int blocks = (n + 255) / 256;
    std::size_t bytes = static_cast<std::size_t>(n) * sizeof(float);
    std::vector<float> x(n), cpu(n), output(n);
    for (int i = 0; i < n; ++i) x[i] = static_cast<float>(i % 256 - 17);
    Buffer device(n);
    cudaEvent_t begin, end;
    CUDA_CHECK(cudaEventCreate(&begin));
    CUDA_CHECK(cudaEventCreate(&end));
    auto cpuRun = [&] {
        cpu = x; // 初始数据和数组分配不计入所比较的处理阶段。
        auto start = Clock::now();
        for (auto& v : cpu) v *= 2.f;
        for (auto& v : cpu) v += 1.f;
        for (auto& v : cpu) v = std::min(std::max(v, 0.f), 255.f);
        return std::chrono::duration<double, std::milli>(Clock::now() - start).count();
    };
    auto gpuRun = [&](bool resident, float& kernelMs) {
        output = x;
        CUDA_CHECK(cudaDeviceSynchronize());
        auto start = Clock::now();
        if (resident) {
            CUDA_CHECK(cudaMemcpy(device.p, x.data(), bytes, cudaMemcpyHostToDevice));
            CUDA_CHECK(cudaEventRecord(begin));
        }
        for (int stage = 0; stage < 3; ++stage) {
            if (!resident)
                CUDA_CHECK(cudaMemcpy(device.p, output.data(), bytes, cudaMemcpyHostToDevice));
            transform<<<blocks, 256>>>(device.p, n, stage);
            CUDA_CHECK(cudaGetLastError());
            if (!resident) {
                CUDA_CHECK(cudaDeviceSynchronize());
                CUDA_CHECK(cudaMemcpy(output.data(), device.p, bytes, cudaMemcpyDeviceToHost));
            }
        }
        if (resident) {
            CUDA_CHECK(cudaEventRecord(end));
            CUDA_CHECK(cudaEventSynchronize(end));
            CUDA_CHECK(cudaMemcpy(output.data(), device.p, bytes, cudaMemcpyDeviceToHost));
        }
        double wallMs = std::chrono::duration<double, std::milli>(Clock::now() - start).count();
        if (resident) CUDA_CHECK(cudaEventElapsedTime(&kernelMs, begin, end));
        if (output != cpu) { std::fputs("流水线结果不一致\n", stderr); std::exit(3); }
        return wallMs;
    };
    // 初始化上下文、预热三个路径；校验在计时区间外。
    float kernelMs = 0;
    cpuRun(); gpuRun(true, kernelMs); gpuRun(false, kernelMs);
    std::vector<double> cpuTimes, residentTimes, roundtripTimes, kernelTimes;
    for (int i = 0; i < repeats; ++i) {
        cpuTimes.push_back(cpuRun());
        residentTimes.push_back(gpuRun(true, kernelMs));
        kernelTimes.push_back(kernelMs);
        roundtripTimes.push_back(gpuRun(false, kernelMs));
    }
    CUDA_CHECK(cudaEventDestroy(begin));
    CUDA_CHECK(cudaEventDestroy(end));
    std::printf("{\"n\":%d,\"repeats\":%d,\"resident_bytes\":%zu,\"roundtrip_bytes\":%zu,"
                "\"cpu_ms\":%.6f,\"kernel_ms\":%.6f,\"resident_ms\":%.6f,"
                "\"roundtrip_ms\":%.6f,\"all_checked\":true}\n",
                n, repeats, 2 * bytes, 6 * bytes, median(cpuTimes), median(kernelTimes),
                median(residentTimes), median(roundtripTimes));
}
