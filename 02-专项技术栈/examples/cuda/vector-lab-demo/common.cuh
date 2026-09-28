#pragma once
#include <cuda_runtime.h>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>

#define CUDA_CHECK(call) do { \
    cudaError_t e = (call); \
    if (e != cudaSuccess) { \
        std::fprintf(stderr, "%s:%d %s: %s\n", __FILE__, __LINE__, \
                     #call, cudaGetErrorString(e)); \
        std::exit(1); \
    } \
} while (0)

inline int number(const char* text, int limit) {
    try {
        std::size_t used;
        long long value = std::stoll(text, &used);
        if (used != std::string(text).size() || value < 1 || value > limit)
            throw std::invalid_argument("范围");
        return static_cast<int>(value);
    } catch (...) {
        std::fprintf(stderr, "参数须为 1..%d 的整数\n", limit);
        std::exit(2);
    }
}

// 只拥有一个设备数组，离开作用域时释放，禁止拷贝造成重复释放。
struct Buffer {
    float* p = nullptr;
    explicit Buffer(std::size_t count) {
        CUDA_CHECK(cudaMalloc(&p, count * sizeof(float)));
    }
    ~Buffer() { CUDA_CHECK(cudaFree(p)); }
    Buffer(const Buffer&) = delete;
    Buffer& operator=(const Buffer&) = delete;
};
