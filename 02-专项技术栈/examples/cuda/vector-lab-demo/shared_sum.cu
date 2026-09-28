#include "common.cuh"
#include "kernels.cuh"
#include <numeric>
#include <vector>

int main(int argc, char** argv) {
    if (argc > 3) return 2;
    int n = argc > 1 ? number(argv[1], 1 << 24) : 513;
    int threads = argc > 2 ? number(argv[2], 512) : 256;
    if (threads < 32 || (threads & (threads - 1)) != 0) {
        std::fprintf(stderr, "归约块大小须为 32..512 的二次幂\n");
        return 2;
    }
    int blocks = (n + threads - 1) / threads;
    std::vector<float> x(n), partial(blocks);
    for (int i = 0; i < n; ++i) x[i] = static_cast<float>(i % 8);
    Buffer dx(n), dp(blocks);
    CUDA_CHECK(cudaMemcpy(dx.p, x.data(), n * sizeof(float), cudaMemcpyHostToDevice));
    blockSum<<<blocks, threads, threads * sizeof(float)>>>(dx.p, dp.p, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(partial.data(), dp.p, blocks * sizeof(float), cudaMemcpyDeviceToHost));
    double actual = std::accumulate(partial.begin(), partial.end(), 0.0);
    double expected = std::accumulate(x.begin(), x.end(), 0.0);
    if (actual != expected) return 3; // 当前小整数数据，块内加法可精确表示。
    std::printf("n=%d threads=%d blocks=%d 每块shared字节=%zu sum=%.0f CPU=%.0f\n",
                n, threads, blocks, threads * sizeof(float), actual, expected);
    for (int i = 0; i < blocks && i < 4; ++i)
        std::printf("partial[%d]=%.0f\n", i, partial[i]);
}
