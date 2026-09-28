#include <iostream>
#include <functional>
int main() {
int a = 0;
auto f = [a]() mutable {
    return ++a;//如果不写mutable，编译器会报错
};
    std::cout << f() << " " << a << "\n";
}
