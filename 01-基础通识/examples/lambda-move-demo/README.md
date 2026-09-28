# lambda-move-demo

各源码各有自己的 main，分别编译。依赖：GCC 10+（C++17），Linux，线程示例需 pthread。

从本卷目录执行 `cd examples/lambda-move-demo`，例如：

```bash
g++ -std=c++17 -Wall -Wextra -pthread sort.cpp -o /tmp/cpp-demo
/tmp/cpp-demo
```

- `sort.cpp`：先输出和 3，再看到 id 依次为 7、4、2、1、-1；比较器决定了降序规则。
- `mutable.cpp`：输出 1 0：被加一的是副本，外面的 a 仍是 0。
- `function.cpp`：输出 3 1；两种变量都能保存可调用对象，auto 并不是“自动推导函数的返回值”。
- `reference.cpp`：输出 20，引用参数修改了 main 中的整数。
- `rvalue-reference.cpp`：c 从 10 变为 20，地址由本次运行决定；这个修改本身没有发生资源移动。
- `move-construction.cpp`：区分引用绑定与真正移动；移动后内容不能预设为空。
- `move-overloads.cpp`：调用类别依次是右值、左值、右值、const 左值、const 右值。
- `forward.cpp`：先运行原版，再按紧邻的提示替换 Fun(t)，比较两次记录。只有后者会保留右值调用类别。

- `capture.cpp`：2 1 / 2 / 5 1，分别观察副本、引用、this 与 *this。
