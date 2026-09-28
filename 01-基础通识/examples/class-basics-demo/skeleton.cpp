#include <iostream>
class ClassName{        //类名
    public:             //修饰限定符public
        ClassName();    //构造函数
        ~ClassName();   //析构函数
        void memberFunction();  //成员函数
    private:                    //修饰限定符private
        int dataMember;         //数据成员
        void privateFunction(); //私有成员函数
};  //注意：类定义结束的花括号后面有一个分号
ClassName::ClassName() : dataMember(1) {}
ClassName::~ClassName() = default;
void ClassName::memberFunction() { std::cout << dataMember << "\n"; }
void ClassName::privateFunction() {}
int main() { ClassName object; object.memberFunction(); }
