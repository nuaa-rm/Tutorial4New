#include <mutex>
#include <thread>

std::mutex first;
std::mutex second;

void left_to_right() {
    std::lock_guard<std::mutex> a(first);
    std::lock_guard<std::mutex> b(second);
}

void right_to_left() {
    std::lock_guard<std::mutex> b(second);
    std::lock_guard<std::mutex> a(first);
}

int main() {
    std::thread one(left_to_right);
    std::thread two(right_to_left);
    one.join();
    two.join();
    return 0;
}
