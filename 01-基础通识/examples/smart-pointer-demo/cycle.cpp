#define STRONG_CYCLE
#include "objects.hpp"
#include <utility>
int main() {
    {
        std::shared_ptr<A> pA(new A);
        std::shared_ptr<B> pB(new B);

        std::cout << pA.use_count() << std::endl;
        std::cout << pB.use_count() << std::endl;
    }
    std::cout << "上面是符合我们预期的" << std::endl << std::endl;
    {
        std::shared_ptr<A> pA(new A);
        std::shared_ptr<B> pB(new B);

        pA->B_ptr = pB;
        pB->A_ptr = pA;

        std::cout << pA.use_count() << std::endl;
        std::cout << pB.use_count() << std::endl;
    }
    std::cout << "咦？这是什么情况呢？为什么没有被析构呢？" << std::endl;
    return 0;
}
