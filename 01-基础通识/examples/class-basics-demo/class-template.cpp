#include <iostream>

template<class T1,class T2>
class A{
public:
    A() = default;
    ~A() = default;
    T1 val;
    T2 id;
    void print(){
        std::cout << val << " " << id << std::endl;
    }
};

int main() {
    A<int, double> a; //实例化时填具体类型
    a.val = 1;
    a.id = 2.5;
    a.print();
    return 0;
}
