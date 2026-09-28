#include <iostream>
class Shape {//这个基类只含有纯虚函数，又叫做抽象类
public:
    Shape() = delete;
    Shape(double A):Area(A)
    {std::cout << "基类的构造函数已经被调用" << std::endl;}
    virtual ~Shape() = default; //允许通过基类指针安全析构
    virtual double calArea() = 0; //纯虚函数
    double Area;
};
class Rectangle
        : public Shape{
public:
    Rectangle() = delete;
    Rectangle(double a,double b):Shape(a*b),a(a),b(b)
    {std::cout << "Rectangle类的构造函数已经被调用，面积为" << Area << std::endl;}
    double a;
    double b;
    double calArea() override{  //重写基类的函数
        return a*b;
    }
};
class Circle
        : public Shape{
public:
    Circle() = delete;
    explicit Circle(double r):Shape(3.14*r*r),r(r)
    {std::cout << "Circle类的构造函数已经被调用，面积：" << Area << std::endl;}
    double r;
    double calArea() override{
        return 3.14*r*r;
    }
};
int main() {
    Circle circle(1.0);
    Rectangle rect(1.0,2.0);
    return 0;
}
