# stl-container-demo

各源码各有自己的 main，分别编译。依赖：GCC 10+（C++17），Linux，线程示例需 pthread。

从本卷目录执行 `cd examples/stl-container-demo`，例如：

```bash
g++ -std=c++17 -Wall -Wextra -pthread vector.cpp -o /tmp/cpp-demo
/tmp/cpp-demo
```

- `vector.cpp`：最终 size 为 1、capacity 不小于 10；reserve 预留空间而 clear 没有释放这份容量。
- `map.cpp`：先输出 90 和 0，再按键顺序输出 alice:90、bob:85；unordered_map 不保证遍历顺序。
- `iterate.cpp`：按容器顺序输出 1 到 9，最后是 0；end 是尾后位置，不能解引用。
- `modify.cpp`：最后输出 5 4 3 2 1 0；比较器使用严格的大于，erase 才真正缩小了容器。
- `erase.cpp`：最后剩下 1 3 5 7 9；删除分支接住返回值后不用再自增。

- `list.cpp`：2 / 2 3，删除节点不会使其他节点位置失效。
- `adapters.cpp`：1 3 2 / 2 3 1 / 3 2 1，比较先进先出、后进先出与最大值优先。
