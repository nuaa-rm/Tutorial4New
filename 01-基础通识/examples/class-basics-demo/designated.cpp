//类型名 对象名{.成员名1 = 初始值1, .成员名2 = 初始值2, ...};
#include <iostream>
struct Foo { int a; int b; };
int main() {
    Foo foo{.a = 1, .b = 3};
    std::cout << foo.a << " " << foo.b << "\n";
}
