#include <chrono>
#include <exception>
#include <future>
#include <iostream>
#include <thread>

void calculate(std::promise<int> result) {
    try {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        result.set_value(6 * 7);
    } catch (...) {
        result.set_exception(std::current_exception());
    }
}

int main() {
    std::promise<int> promise;
    std::future<int> future = promise.get_future();
    std::thread worker(calculate, std::move(promise));
    std::cout << "answer = " << future.get() << '\n';
    worker.join();
    return 0;
}
