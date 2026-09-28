#include <atomic>
#include <iostream>
#include <thread>

std::atomic<int> counter{0};
std::atomic<bool> stop{false};

void add_many_times() {
    for (int i = 0; i < 100000; ++i) ++counter;
}

void wait_for_stop() {
    while (!stop.load()) std::this_thread::yield();
    std::cout << "received stop signal\n";
}

int main() {
    std::thread first(add_many_times);
    std::thread second(add_many_times);
    std::thread observer(wait_for_stop);
    first.join();
    second.join();
    stop.store(true);
    observer.join();
    std::cout << "counter = " << counter.load() << '\n';
    return 0;
}
