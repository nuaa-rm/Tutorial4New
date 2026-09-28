#include <iostream>
#include <mutex>
#include <shared_mutex>
#include <string>
#include <thread>
#include <unordered_map>

std::unordered_map<std::string, int> config{{"exposure", 10}};
std::shared_mutex config_mutex;

int read_config(const std::string& key) {
    std::shared_lock<std::shared_mutex> lock(config_mutex);
    return config.at(key);
}

void write_config(const std::string& key, int value) {
    std::unique_lock<std::shared_mutex> lock(config_mutex);
    config[key] = value;
}

int main() {
    std::thread reader1([] { std::cout << read_config("exposure") << '\n'; });
    std::thread reader2([] { std::cout << read_config("exposure") << '\n'; });
    std::thread writer([] { write_config("exposure", 12); });
    reader1.join();
    reader2.join();
    writer.join();
    return 0;
}
