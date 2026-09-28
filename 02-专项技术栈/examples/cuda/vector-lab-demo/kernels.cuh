#pragma once
#include <cuda_runtime.h>

__global__ void vecAdd(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}

__global__ void blockSum(const float* x, float* partial, int n) {
    extern __shared__ float tile[];
    int t = threadIdx.x;
    int i = blockIdx.x * blockDim.x + t;
    tile[t] = (i < n) ? x[i] : 0.f;
    __syncthreads();
    for (int step = blockDim.x / 2; step > 0; step /= 2) {
        if (t < step) tile[t] += tile[t + step];
        __syncthreads();
    }
    if (t == 0) partial[blockIdx.x] = tile[0];
}

__global__ void transform(float* x, int n, int stage) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return; // 此核没有块内屏障。
    if (stage == 0) x[i] *= 2.f;
    else if (stage == 1) x[i] += 1.f;
    else x[i] = fminf(fmaxf(x[i], 0.f), 255.f);
}
