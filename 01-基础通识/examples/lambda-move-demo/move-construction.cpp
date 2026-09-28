#include <iostream>
#include <string>
#include <utility>
class A {
public:
    A() : val("a0") { std::cout << "你调用了默认构造" << std::endl; }

    A(std::string a) : val(a) { std::cout << "你调用了含参构造" << std::endl; }

    A(const A &obj) {
        std::cout << "你调用了拷贝构造" << std::endl;
        this->val = obj.val;
    }

    A(A &&obj) noexcept {
        std::cout << "你调用了移动构造" << std::endl;
        this->val = std::move(obj.val);
    }

    A &operator=(const A &obj) {
        if (this == &obj)
            return *this;
        std::cout << "你调用了等号赋值" << std::endl;
        this->val = obj.val;

        return *this;
    }

    ~A() { std::cout << "对象被析构，val为：" << val << std::endl; }

    std::string val;
};

int main() {
    std::cout << "a1,";
    A a1("a1");
    std::cout << std::endl;

    std::cout << "a2,";
    A a2 = a1;
    std::cout << "val值为：" << a2.val << std::endl;
    std::cout << std::endl;

    a2 = a1;//区别上面的
    std::cout << std::endl;

    std::cout << "a3,";
    A a3(a2);
    std::cout << "val值为：" << a3.val << std::endl;
    std::cout << std::endl;

    std::cout << "a4,";
    A &a4 = a1;
    std::cout << "val值为：" << a4.val << std::endl;
    std::cout << std::endl;

    std::cout << "a5,";
    A &&a5 = std::move(a1);
    std::cout << "val值为：" << a5.val << std::endl;
    std::cout << std::endl;

    a2.val = "new a2";
    std::cout << "a1的val值为：" << a1.val << std::endl;
    a4.val = "new a4";
    std::cout << "a1的val值为：" << a1.val << std::endl;
    std::cout << "a5的val值为：" << a5.val << std::endl;
    std::cout << std::endl;

    std::cout << "a6,";
    A a6(std::move(a1));
    std::cout << "val值为：" << a6.val << std::endl;
    std::cout << "a1被传入移动构造后,";
    std::cout << "val值为：" << a1.val << std::endl;
    std::cout << std::endl;

    return 0;
}
