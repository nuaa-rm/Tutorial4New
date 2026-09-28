#include <iostream>
#include <functional>

template<class T>
T function(T a){
    return a;
}

int main() {
    //调用的时候实际上分为两步，实例化和调用
    function<int>(10);
    function<double>(20.0);
    //在编译器可以推导出类型的时候可以不加<>
    auto a = function(1.0);
    std::cout << a << "\n";
    //在无法推导的时候，要先进行实例化
    std::function<int(int)> ptr = function<int>;
    std::cout << ptr(10) << "\n";
    return 0;
}
