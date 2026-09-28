#include <future>
#include <iostream>

int square(int value) { return value * value; }

int main() {
    std::future<int> result = std::async(
        std::launch::async, square, 12);
    std::cout << result.get() << '\n';       // 输出 144
    return 0;
}
