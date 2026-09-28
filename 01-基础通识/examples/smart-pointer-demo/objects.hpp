#pragma once
#include <iostream>
#include <memory>
class A;
class B;
class A{
public:
    A(){std::cout << "你调用了A的默认构造函数" << std::endl;}
    ~A(){std::cout << "A对象已被析构，val值为：" << val << std::endl;}
    int getVal(){return val;};
    void setVal(int val){this->val = val;}
    std::shared_ptr<B> B_ptr;
private:
    int val = 0;
};

class B{
public:
    B(){std::cout << "你调用了B的默认构造函数" << std::endl;}
    ~B(){std::cout << "B对象已被析构，val值为：" << val << std::endl;}
    int getVal(){return val;};
    void setVal(int val){this->val = val;}
#ifdef STRONG_CYCLE
    std::shared_ptr<A> A_ptr;
#else
    std::weak_ptr<A> A_ptr;
#endif
    // 默认使用weak_ptr，强引用版本只用于演示泄漏
private:
    int val = 0;
};
