#include <iostream>
#include <functional>
int main() {
//使用function承接返回值
std::function<int(int,int)> add = [](int a,int b){return a+b;};
int result = add(1,2);//调用lambda表达式
//也可以使用auto关键字自动推导返回类型
auto sub = [](int a,int b){return a-b;};
    std::cout << result << " " << sub(3, 2) << "\n";
}
