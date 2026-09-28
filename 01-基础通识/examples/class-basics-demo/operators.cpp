#include <iostream>

class ClassName {
public:
    ClassName():a(1),b(2) {}

    ClassName operator+(const ClassName& obj) const {
        ClassName result;
        result.a = this->a + obj.a; //this指向当前对象
        result.b = this->b + obj.b;
        return result; //加法返回新对象，两个输入保持原值
    }

    //重载流插入运算符，思考一下为什么是这样写？
    friend std::ostream& operator<<(std::ostream& out, const ClassName& obj);

    int a;
    int b;
};

std::ostream& operator<<(std::ostream& out, const ClassName& obj){
    out << "a:" << obj.a << " b:" << obj.b << std::endl;
    return out;
}

int main() {
    ClassName obj1;
    ClassName res = obj1 + obj1;
    std::cout << res;
    return 0;
}
