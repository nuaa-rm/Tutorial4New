# 类、继承与模板

每个 cpp 是独立程序。依赖 GCC 10+；在本目录执行：

```bash
g++ -std=c++17 -Wall -Wextra overload.cpp -o /tmp/cpp-demo
/tmp/cpp-demo
```

输出3、4，来自整数和小数两个重载。其余源码名、运行命令与预期输出见正文2.1各示例；designated.cpp 必须换成 `-std=c++20`，应输出1 3。继承示例先构造基类，再构造派生类；operators.cpp 输出a:2 b:4，输入对象不变。构造示例的三个member最后为10、2、10。每个文件各有main，不要把它们拼在一起。
