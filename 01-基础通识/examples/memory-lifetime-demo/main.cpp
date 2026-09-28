#include <iostream>
#include <memory>
#include <string>
#include <utility>
struct Object {
    std::string name;
    explicit Object(std::string value) : name(std::move(value)) {
        std::cout << "construct " << name << '\n';
    }
    ~Object() { std::cout << "destroy " << name << '\n'; }
};
std::unique_ptr<Object> create() {
    Object local("local");
    return std::make_unique<Object>("dynamic");
}
int main() {
    auto owner = create();
    std::cout << "use " << owner->name << '\n';
    owner.reset();
    std::cout << "owner empty=" << (owner == nullptr) << '\n';
}
