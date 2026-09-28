#include <cstdio>
#include <vector>

int main() {
    const std::vector<int> x{1, 7, 2, 8};
    int prefix = 0;
    for (int value : x) {
        int mask = (value >= 5) ? 255 : 0;
        prefix += value;
        std::printf("输入=%d 阈值=%d 前缀和=%d\n", value, mask, prefix);
    }
}
