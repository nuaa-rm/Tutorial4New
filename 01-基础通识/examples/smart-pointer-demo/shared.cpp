#include "objects.hpp"
#include <utility>

int main() {
    {
        std::shared_ptr<A> ptr1 = nullptr;
        {
            auto ptr2 = std::make_shared<A>();
            ptr2->setVal(1);
            ptr1 = ptr2;
            //ptr1 = std::move(ptr2);//看一下这两种写法有什么区别？
            std::cout << "ptr1对象的引用次数为：" << ptr1.use_count() << std::endl;
            std::cout << "ptr2对象的引用次数为：" << ptr2.use_count() << std::endl;
        }
        std::cout << "ptr2已经被析构了" << std::endl;
        std::cout << "但A对象还活着，引用次数为：" << ptr1.use_count() << std::endl;
    }//到这里A对象才被析构
    return 0;
}
