# smart-pointer-demo

各源码各有自己的 main，分别编译。依赖：GCC 10+（C++17；designated.cpp 用 C++20），Linux，线程示例需 pthread。

从本卷目录执行 `cd examples/smart-pointer-demo`，例如：

```bash
g++ -std=c++17 -Wall -Wextra -pthread unique.cpp -o /tmp/cpp-demo
/tmp/cpp-demo
```

- `unique.cpp`：原 ptr1 为空，ptr2 读到 1；后来创建的值为 2，两个对象都在作用域结束时析构。
- `shared.cpp`：内部两个计数都是 2，内部指针销毁后外部计数为 1；移出作用域后对象才析构。
- `cycle.cpp`：第一段两个对象正常析构；第二段计数都为 2，却没有析构提示，这是故意保留的小规模泄漏示范，仅在临时练习程序中运行。
- `weak.cpp`：强引用计数分别为 1、2，临时 lock 后又 reset，离开作用域两个对象都会析构。
