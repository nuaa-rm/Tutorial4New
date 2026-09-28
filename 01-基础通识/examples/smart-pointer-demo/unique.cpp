#include "objects.hpp"
#include <utility>

int main() {
    {
        std::unique_ptr<A> ptr1 = std::make_unique<A>();
        ptr1->setVal(1);
        //std::unique_ptr<A> ptr2 = ptr1;会报错，独占指针不允许拷贝
        std::unique_ptr<A> ptr2 = std::move(ptr1);
        if(ptr1 == nullptr){
            std::cout << "ptr1是一个空指针" << std::endl;
        }
        std::cout << "ptr2的val值为：" << ptr2->getVal() << std::endl;
        ptr1 = std::make_unique<A>();
        ptr1->setVal(2);
    }//离开作用域，ptr1和ptr2管理的对象被自动析构
    return 0;
}
