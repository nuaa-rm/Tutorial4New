# thread-coordination-demo

各源码各有自己的 main，分别编译。依赖：GCC 10+（C++17；designated.cpp 用 C++20），Linux，线程示例需 pthread。

从本卷目录执行 `cd examples/thread-coordination-demo`，例如：

```bash
g++ -std=c++17 -Wall -Wextra -pthread lifecycle.cpp -o /tmp/cpp-demo
/tmp/cpp-demo
```

- `lifecycle.cpp`：first 按序打印 1 2 3，等待两个线程结束后输出 value = 1。
- `mutex.cpp`：输出 200000，两个线程的整个自增操作都在锁内。
- `shared-lock.cpp`：读者可能读到 10 或 12，写入与读取不会同时进入；多次流插入仍可能交错，输出次序不是锁相容性的证据。
- `atomic.cpp`：看到停止提示与 counter = 200000；yield 是轮询让步，不等于条件变量的休眠等待。
- `condition.cpp`：输出 data is ready。即使生产者先完成，消费者也会依据 ready 条件继续，不依赖通知被“记住”。
- `promise.cpp`：输出 answer = 42，future 取得工作线程设置的值。
- `async.cpp`：输出 144，get 等待结果后取回平方值。
- `pool.cpp`：0 到 7 的任务各执行一次，输出片段可能交错；析构会等待已有任务处理完。这个教学实现约定任务不向外抛异常，线程创建失败时也未做完整恢复。
- `bounded-queue.cpp`：依次消费 0 到 9，然后退出；close 唤醒等待者，剩余元素仍会被取完。
- `readers-writers.cpp`：每个读者读到 0 或 100，读取有共享锁，更新有独占锁；谁先执行由调度决定。
- `philosophers.cpp`：每位哲学家吃两次后所有线程退出，输出可能交错；共同获取两锁避免这一组资源的循环等待。
- `deadlock.cpp`：可能正常退出，也可能被 timeout 以状态 124 停止。没有卡死只说明本次没碰到那个交错顺序，不能证明正确。

deadlock.cpp 是错误示范，只用 `timeout 2s /tmp/cpp-demo` 限时运行。正常退出也不能证明无死锁。pool.cpp 是教学实现：不允许销毁期间继续调用接口，任务须自行处理异常，线程创建失败恢复未实现。不要直接用作生产线程池。
