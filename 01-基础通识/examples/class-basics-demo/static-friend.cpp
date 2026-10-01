#include <iostream>

class ClassName {
    public:
        ClassName() = default;
        ~ClassName() = default;

        static void memberFunction() {
            std::cout << dataMember << "\n";
        } //静态成员函数
        static int dataMember;                  //静态数据成员，类内声明
        friend void FriendFunction(ClassName& obj); //友元函数声明
    private:
        int secret = 42;                        //私有数据成员
};

int ClassName::dataMember = 10; //静态数据成员在类外定义，且只定义一次

void FriendFunction(ClassName& obj){ //友元函数实现时，不可以添加类的作用域
    std::cout << "友元函数访问私有成员：" << obj.secret << std::endl;
}

int main() {
    ClassName obj1, obj2;
    std::cout << obj1.dataMember << std::endl;  //输出10
    std::cout << obj2.dataMember << std::endl;  //还是10，两个对象共享同一份
    obj1.dataMember = 20;                        //修改静态数据成员
    std::cout << obj1.dataMember << std::endl;  //输出20
    std::cout << obj2.dataMember << std::endl;  //obj2也输出20，说明静态数据成员被类的所有对象共享
    FriendFunction(obj1);
    return 0;
}
