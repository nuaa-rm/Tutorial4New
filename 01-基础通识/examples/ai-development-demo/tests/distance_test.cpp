#include "distance.hpp"
#include <cmath>
#include <iostream>

int main() {
    const int input[] = {0, 1000, 1500, -500};
    const double expected[] = {0.0, 1.0, 1.5, -0.5};
    int failures = 0;
    for (int i = 0; i < 4; ++i) {
        const double actual = millimeters_to_meters(input[i]);
        if (!std::isfinite(actual) || std::abs(actual - expected[i]) > 1e-9) {
            std::cerr << "FAIL mm=" << input[i] << " expected="
                      << expected[i] << " actual=" << actual << '\n';
            ++failures;
        }
    }
    std::cout << "failures=" << failures << '\n';
    return failures == 0 ? 0 : 1;
}
