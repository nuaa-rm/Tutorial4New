#include <iostream>
#include <mutex>
#include <thread>

int counter = 0;
std::mutex counter_mutex;

void add_many_times() {
    for (int i = 0; i < 100000; ++i) {
        std::lock_guard<std::mutex> lock(counter_mutex);
        ++counter;
    }
}

int main() {
    std::thread first(add_many_times);
    std::thread second(add_many_times);
    first.join();
    second.join();
    std::cout << counter << '\n';
    return 0;
}
