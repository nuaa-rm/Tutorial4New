#include <chrono>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

const int philosopher_count = 5;
std::mutex forks[philosopher_count];

void dine(int id) {
    int left = id;
    int right = (id + 1) % philosopher_count;
    for (int round = 0; round < 2; ++round) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        std::scoped_lock lock(forks[left], forks[right]);
        std::cout << "philosopher " << id << " is eating\n";
    }
}

int main() {
    std::vector<std::thread> philosophers;
    for (int i = 0; i < philosopher_count; ++i)
        philosophers.emplace_back(dine, i);
    for (auto& philosopher : philosophers) philosopher.join();
    return 0;
}
