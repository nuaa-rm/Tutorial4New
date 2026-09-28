#include <condition_variable>
#include <functional>
#include <iostream>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <thread>
#include <vector>

class ThreadPool {
private:
    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex mtx_;
    std::condition_variable cv_;
    bool stopping_ = false;

public:
    explicit ThreadPool(std::size_t count) {
        if (count == 0) throw std::invalid_argument("empty pool");
        for (std::size_t i = 0; i < count; ++i) {
            workers_.emplace_back([this] {
                while (true) {
                    std::function<void()> task;
                    {
                        std::unique_lock<std::mutex> lock(mtx_);
                        cv_.wait(lock, [this] {
                            return stopping_ || !tasks_.empty();
                        });
                        if (stopping_ && tasks_.empty()) return;
                        task = std::move(tasks_.front());
                        tasks_.pop();
                    }
                    task();
                }
            });
        }
    }

    ~ThreadPool() {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            stopping_ = true;
        }
        cv_.notify_all();
        for (auto& worker : workers_) worker.join();
    }

    void enqueue(std::function<void()> task) {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            if (stopping_) throw std::runtime_error("thread pool is stopping");
            tasks_.push(std::move(task));
        }
        cv_.notify_one();
    }
};

int main() {
    ThreadPool pool(3);
    for (int i = 0; i < 8; ++i) {
        pool.enqueue([i] {
            std::cout << "task " << i << " is running\n";
        });
    }
    return 0;       // 析构函数等待任务完成并回收线程
}
