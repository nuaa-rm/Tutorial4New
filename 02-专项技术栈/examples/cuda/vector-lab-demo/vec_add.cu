#include "common.cuh"
#include "kernels.cuh"
#include <vector>

int main(int argc, char** argv) {
    if (argc > 3) return 2;
    int n = argc > 1 ? number(argv[1], 1 << 24) : (1 << 20) + 3;
    int threads = argc > 2 ? number(argv[2], 1024) : 256;
    std::size_t bytes = static_cast<std::size_t>(n) * sizeof(float);
    std::vector<float> a(n), b(n), c(n);
    for (int i = 0; i < n; ++i) {
        a[i] = static_cast<float>(i % 17 - 8);
        b[i] = static_cast<float>(i % 13);
    }
    Buffer da(n), db(n), dc(n);
    CUDA_CHECK(cudaMemcpy(da.p, a.data(), bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(db.p, b.data(), bytes, cudaMemcpyHostToDevice));
    int blocks = (n + threads - 1) / threads;
    vecAdd<<<blocks, threads>>>(da.p, db.p, dc.p, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaDeviceSynchronize());
    CUDA_CHECK(cudaMemcpy(c.data(), dc.p, bytes, cudaMemcpyDeviceToHost));
    for (int i = 0; i < n; ++i) {
        if (c[i] != a[i] + b[i]) {
            std::fprintf(stderr, "索引 %d 输出不一致\n", i);
            return 3;
        }
    }
    std::printf("n=%d threads=%d blocks=%d 跳过线程=%d 全部结果通过\n",
                n, threads, blocks, blocks * threads - n);
    std::printf("设备数组字节=%zu H2D=%zu D2H=%zu C[0]=%.1f C[n-1]=%.1f\n",
                3 * bytes, 2 * bytes, bytes, c[0], c[n - 1]);
}
