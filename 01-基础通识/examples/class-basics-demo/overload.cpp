#include <iostream>

class ClassName {
public:
    ClassName() = default;
    ~ClassName() = default;

    int CalSum(int a,int b){
        return a+b;
    }

    double CalSum(double a,double b){
        return a+b;
    }
};

int main() {
    ClassName obj;
    std::cout << obj.CalSum(1,2) << std::endl;
    std::cout << obj.CalSum(1.5,2.5) << std::endl;
    return 0;
}
