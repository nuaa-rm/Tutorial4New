# 对象寿命

依赖 C++17 的 GCC。

```bash
cd examples/memory-lifetime-demo
g++ -std=c++17 -Wall -Wextra main.cpp -o /tmp/memory-lifetime
/tmp/memory-lifetime
```

应依次出现 construct local、construct dynamic、destroy local、use dynamic、destroy dynamic、owner empty=1。reset 后不能再解引用。

recursion.cpp 用相同命令替换源码名编译，应先进入4、3、2、1，再返回3、7、15、31；改成f(3)则最后返回15。
