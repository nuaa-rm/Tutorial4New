#include <iostream>
int f(int n) {
    std::cout << "enter " << n << '\n';
    int result = n == 1 ? 3 : 2 * f(n - 1) + 1;
    std::cout << "return " << result << '\n';
    return result;
}
int main() { f(4); }
