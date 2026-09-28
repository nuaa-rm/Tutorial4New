#include <iostream>

void func(int& A){//可以试一下把引用去掉
    A *= 2;
}

int main() {
    int a = 10;
    func(a);
    std::cout << a << std::endl; //输出20
    return 0;
}
