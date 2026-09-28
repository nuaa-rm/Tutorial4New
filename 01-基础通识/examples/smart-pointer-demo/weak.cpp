#include "objects.hpp"
#include <utility>
int main() {
    {
        std::shared_ptr<A> pA(new A);
        std::shared_ptr<B> pB(new B);

        pA->B_ptr = pB;
        pB->A_ptr = pA; //weak_ptr不增加引用计数

        std::cout << pA.use_count() << std::endl;
        std::cout << pB.use_count() << std::endl;

        std::shared_ptr<A> PtrA = pB->A_ptr.lock(); //升级为shared_ptr再使用
        if(PtrA != nullptr)
            PtrA->setVal(1234);
        PtrA.reset();
    }//这次两个对象都能正常析构了
    return 0;
}
