#include <iostream>
#include <thread>
#include <functional>

void print_range(int begin, int end) {
    for (int i = begin; i <= end; ++i) std::cout << i << ' ';
    std::cout << '\n';
}

void add_one(int& value) { ++value; }

int main() {
    std::thread first(print_range, 1, 3);
    int value = 0;
    std::thread second(add_one, std::ref(value));
    first.join();
    second.join();
    std::cout << "value = " << value << '\n';
    return 0;
}
