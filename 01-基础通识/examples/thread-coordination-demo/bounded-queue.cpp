#include <condition_variable>
#include <iostream>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <thread>

class BoundedQueue {
private:
    std::queue<int> queue_;
    const std::size_t capacity_;
    std::mutex mtx_;
    std::condition_variable not_empty_;
    std::condition_variable not_full_;
    bool closed_ = false;

public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {
        if (capacity == 0) throw std::invalid_argument("empty queue");
    }

    bool push(int value) {
        std::unique_lock<std::mutex> lock(mtx_);
        not_full_.wait(lock, [this] {
            return queue_.size() < capacity_ || closed_;
        });
        if (closed_) return false;
        queue_.push(value);
        not_empty_.notify_one();
        return true;
    }

    bool pop(int& value) {
        std::unique_lock<std::mutex> lock(mtx_);
        not_empty_.wait(lock, [this] {
            return !queue_.empty() || closed_;
        });
        if (queue_.empty()) return false;
        value = queue_.front();
        queue_.pop();
        not_full_.notify_one();
        return true;
    }

    void close() {
        {
            std::lock_guard<std::mutex> lock(mtx_);
            closed_ = true;
        }
        not_empty_.notify_all();
        not_full_.notify_all();
    }
};

int main() {
    BoundedQueue queue(3);
    std::thread producer([&] {
        for (int i = 0; i < 10; ++i) queue.push(i);
        queue.close();
    });
    std::thread consumer([&] {
        int value = 0;
        while (queue.pop(value)) std::cout << "consume " << value << '\n';
    });
    producer.join();
    consumer.join();
    return 0;
}
