#include <iostream>
#include <utility>

void func(int&& a){
    std::cout << "a的地址：" << &a << std::endl;
    a *= 2;
}

int main() {
    int&& c = 10;
    std::cout << "c的值为：" << c << std::endl;
    func(std::move(c)); //c本身是左值，需要move转换为右值才能传入
    std::cout << "经过函数之后，c的值为：" << c << std::endl;
    std::cout << "c的地址为" << &c << std::endl;
    return 0;
}
