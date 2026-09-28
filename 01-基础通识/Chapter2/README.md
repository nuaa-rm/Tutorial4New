# 第二章入口

当前正文从本卷 main.tex 按以下顺序引入：

- 21.tex：类、静态与友元、构造、重载、继承和模板。
- 22_core.tex：lambda、引用、移动和转发。
- 22_smartptr.tex：独占、共享、弱引用与循环引用。
- 22_stl.tex：数据结构、容器、迭代器与失效。
- 22_thread.tex：线程、同步、异步结果和经典并发问题；末尾引入22_memory.tex，说明进程内存与对象寿命。

22.tex、22_advanced.tex、22_iterator.tex 是拆分前的历史稿，当前没有正文调用方；保留用于对照，不与拆分后的正文重复编译。编辑现行正文时按上面的文件定位，不再维护旧稿中的同一段内容。

题解统一在本卷 answers.tex。正文演示源码在本卷 examples 下六个对应项目中，通过 lstinputlisting 引入；images 中已检查的第二章矢量图带 revised 标记。scripts/verify_ch2_examples.py 在临时目录编译运行，不把产物放进教材源码目录。
