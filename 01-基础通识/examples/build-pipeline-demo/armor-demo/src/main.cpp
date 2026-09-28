#include "armor.hpp"
#include <iostream>

int main() {
    std::cout << "score=" << armor_score(3) << '\n';
#ifdef SAVE_OUTPUT
    std::cout << "save output enabled\n";
#endif
    return 0;
}
