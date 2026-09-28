#include <iostream>
#include <mutex>
#include <shared_mutex>
#include <thread>
#include <vector>

int score = 0;
std::shared_mutex score_mutex;

void reader(int id) {
    std::shared_lock<std::shared_mutex> lock(score_mutex);
    std::cout << "reader " << id << ": " << score << '\n';
}

void writer(int value) {
    std::unique_lock<std::shared_mutex> lock(score_mutex);
    score = value;
}

int main() {
    std::vector<std::thread> readers;
    for (int i = 0; i < 3; ++i) readers.emplace_back(reader, i);
    std::thread writer_thread(writer, 100);
    for (auto& reader_thread : readers) reader_thread.join();
    writer_thread.join();
    return 0;
}
