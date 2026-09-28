#include <iostream>
struct Object {
    int value = 1;
    auto pointer_reader() { return [this] { return value; }; }
    auto copy_reader() { return [*this] { return value; }; }
};
int main() {
    int a = 1;
    auto copy = [a]() mutable { return ++a; };
    std::cout << copy() << ' ' << a << '\n';
    auto reference = [&a] { ++a; };
    reference();
    std::cout << a << '\n';
    Object object;
    auto pointer = object.pointer_reader();
    auto snapshot = object.copy_reader();
    object.value = 5;
    std::cout << pointer() << ' ' << snapshot() << '\n';
}
