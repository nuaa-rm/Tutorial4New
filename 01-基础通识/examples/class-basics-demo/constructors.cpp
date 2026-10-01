#include<iostream>
#include<string>
class ClassName {
public:
    ClassName():member("Default") //初始化列表
    {std::cout << "你调用了默认构造函数" << std::endl;}
    ClassName(const std::string& str)
    {std::cout << "你调用了含参构造函数，参数是" << str << std::endl;member=str;}
    ClassName(const ClassName &obj) //这里必须是引用传参，思考一下为什么
    {std::cout << "你调用了复制构造函数" << std::endl;
    this->member = obj.member;}
    ClassName(ClassName&& obj) //移动构造函数
    {std::cout << "你调用了移动构造函数" << std::endl;
    this->member = std::move(obj.member);}
    ~ClassName() = default;

    std::string member;
};

int main() {
    ClassName obj1;
    std::cout << "obj1:" << obj1.member << std::endl;
    obj1.member = "Modified";
    std::cout << "obj1 after modification:" << obj1.member << std::endl;

    std::string str = "Hello World";
    ClassName obj2(str);
    std::cout << "obj2:" << obj2.member << std::endl;
   
    ClassName obj3(obj1);
    std::cout << "obj3:" << obj3.member << std::endl;

    ClassName obj4(std::move(obj1));
    std::cout << "obj4:" << obj4.member << std::endl;
    std::cout << "obj1 after move:" << obj1.member << std::endl; //移动后obj1的状态不确定，可能为空或未定义

    return 0;
}
