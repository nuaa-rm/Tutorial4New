#include <iostream>
#include <queue>
#include <stack>
int main() {
    std::queue<int> queue;
    std::stack<int> stack;
    std::priority_queue<int> priority;
    for (int x : {1, 3, 2}) {
        queue.push(x); stack.push(x); priority.push(x);
    }
    while (!queue.empty()) {
        std::cout << queue.front() << ' '; queue.pop();
    }
    std::cout << '\n';
    while (!stack.empty()) {
        std::cout << stack.top() << ' '; stack.pop();
    }
    std::cout << '\n';
    while (!priority.empty()) {
        std::cout << priority.top() << ' '; priority.pop();
    }
    std::cout << '\n';
}
