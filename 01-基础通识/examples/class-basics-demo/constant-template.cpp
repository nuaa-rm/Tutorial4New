#include <iostream>
template<int N>
int getConst(){
    return N;
}

int main() {
    int v = getConst<42>();
    std::cout << v << "\n"; //v = 42
    return 0;
}
