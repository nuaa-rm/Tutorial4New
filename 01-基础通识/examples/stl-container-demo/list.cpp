#include <iostream>
#include <list>
#include <iterator>
int main() {
    std::list<int> values{1, 2, 3};
    auto second = std::next(values.begin());
    values.erase(values.begin());
    std::cout << *second << '\n';
    for (int x : values) std::cout << x << ' ';
    std::cout << '\n';
}
