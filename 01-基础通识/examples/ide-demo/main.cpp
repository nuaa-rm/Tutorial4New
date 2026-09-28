#include <iostream>

int add_score(int current, int bonus) {
    int result = current + bonus;
    return result;
}

int main() {
    int score = 60;
    int bonus = 15;
    int total = add_score(score, bonus);
    std::cout << "total = " << total << '\n';
    return 0;
}
