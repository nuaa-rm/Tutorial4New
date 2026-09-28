#include <iostream>
#include <utility>
using namespace std;
void Fun(int&) { cout << "左值引用" << endl; }
void Fun(const int&) { cout << "const 左值引用" << endl; }
void Fun(int&&) { cout << "右值引用" << endl; }
void Fun(const int&&) { cout << "const 右值引用" << endl; }

int main() {
    Fun(10);           // 右值
    int a = 1;
    Fun(a);            // 左值
    Fun(std::move(a)); // 右值
    const int b = 8;
    Fun(b);      // const 左值
    Fun(std::move(b)); // const 右值
    return 0;
}
