#include <iostream>
#include <utility>
using namespace std;
void Fun(int&) { cout << "左值引用" << endl; }
void Fun(const int&) { cout << "const 左值引用" << endl; }
void Fun(int&&) { cout << "右值引用" << endl; }
void Fun(const int&&) { cout << "const 右值引用" << endl; }
template<typename T>
void PerfectForward(T&& t)
{
    Fun(t);
    //Fun(std::forward<T>(t));//使用完美转发
}
int main() {
    PerfectForward(10);           // 右值
    int a = 1;
    PerfectForward(a);            // 左值
    PerfectForward(std::move(a)); // 右值
    const int b = 8;
    PerfectForward(b);            // const 左值
    PerfectForward(std::move(b)); // const 右值
    return 0;
}
