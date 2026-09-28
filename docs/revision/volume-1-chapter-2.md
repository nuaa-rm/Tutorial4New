# 卷一第二章：现代 C++ 基础修订记录

本章按 skill 的 20 项要求整理。正文、题解、项目代码、图片和当前环境下的运行验证已完成；本章通过不代表全书已经验收，第一章的真实安装、恢复、GUI 与板端验证仍见第一章记录。

## 语言与内容

继续以修订前 `c5543bb` 的 `Chapter1/11.tex`、`12.tex`、`13.tex` 为语言参照。保留原有类、模板、智能指针和数据结构的讲解顺序，新补内容先承接眼前的问题，再说明为什么这样写、运行后看哪里。示例附近用连贯段落带着操作，没有把正文改成参数与验收清单。

- 类：补齐缺少分号的代码；区分 static 成员的声明与定义、struct/class 的默认访问与继承权限、友元授予访问权；构造、复制、赋值和运算符示例不再混为一谈。加法返回新对象，基类有虚析构，C++20 指定初始化按声明顺序写。
- Lambda 与移动：纠正旧式异常说明、值捕获“自动深拷贝”、引用捕获寿命、this 与 *this 的区别；从表达式的值类别解释左值、右值、命名引用、std::move 与 std::forward，不把“有地址”“看起来像常量”当通用判断法。
- 智能指针：完整展示公共对象定义及四种独立程序；成员先初始化，避免析构读取未初始化值。区分循环引用、weak_ptr::lock 的临时所有权和共享数据的互斥保护。
- STL：说明 reserve 与 resize、容量增长的实现差异、list 的局部失效、容器适配器、树/二叉树/堆与红黑树。修正排序比较器、哈希平均与最坏复杂度及迭代器失效规则，错误写法只在 libstdc++ 调试模式下诊断。
- 并发：正文展示线程池和三个经典协作问题的完整程序；有界队列关闭后让消费者收尾，零容量和零工作线程拒绝构造。说明条件变量谓词、原子变量的范围、scoped_lock 的保证以及教学线程池的异常处理边界。死锁示例限时运行，正常退出不作为无死锁证明。
- 内存：把原先未进入正文的 `22_memory.tex` 接到多线程节末，补进程虚拟地址空间、存储期与对象寿命、递归调用与返回；删除“所有栈都是 2 MB”等不准确结论。用实际构造/析构与递归日志配合图示。

## 20 项检查

本章没有“不适用”或“未完成”项。对故意错误的写法采用可控的编译失败或调试诊断；不通过执行未定义行为来证明结论。

| 项 | 状态 | 位置或依据 |
| --- | --- | --- |
| 1 章首提要 | 通过 | `main.tex` 第二章 introduction：可验证学习目标、建议学时与本卷边界。 |
| 2 核心小节示例 | 通过 | 下表列出对应关系；44 个正文独立程序包含前提、完整代码、运行命令和结果解读。 |
| 3 复杂概念项目 | 通过 | 六个概念目录位于本卷 examples；源码、公共头文件及各 README 齐全。 |
| 4 正文讲清项目 | 通过 | 每个项目在对应知识点旁展示目录/文件组成，核心代码用 lstinputlisting 直接引入；解释执行顺序、关键语句和输出。智能指针公共头文件完整展示。 |
| 5 命令语法参数 | 通过 | 项目介绍解释 g++、-std、-Wall/-Wextra、-pthread、-o，逐例给出工作目录与运行命令；C++20 指定初始化另用 c++20，调试失效迭代器解释 GCC 条件。 |
| 6 随堂练习 | 通过 | 27 道有标签的 exercise，核心能力覆盖见下表；模板、引用/移动、容器和经典协作的合并练习明确列出分项任务。 |
| 7 难点归纳 | 通过 | 构造/赋值及 static/友元、捕获方式、引用/移动、智能指针、迭代器、同步/经典问题、内存均有 conclusion 或对应对比表。 |
| 8 易错提示 | 通过 | 引用悬空、未初始化访问、重复接管裸指针、循环引用、无效迭代器、非严格排序、数据竞争、线程销毁、等待/锁与死锁有紧邻提示。错误代码的运行条件和教学项目边界写明。 |
| 9 本章小结 | 通过 | `main.tex` 第二章小结把类、Lambda、引用/移动、所有权、容器、并发与内存连起来，并指向下一章多文件构建。 |
| 10 章末习题 | 通过 | 12 题覆盖基础、提高和 Armor 综合实践；保留原有 10 题并补模板与内存，避免遗漏本章两块核心内容。容器题同时检查查询、适配器和安全删除。 |
| 11 本章验收 | 通过 | 六项独立演示任务要求重新构建、解释预测、修改运行参数、保存核对记录；与有标准答案的习题分工清楚。 |
| 12 答案定位 | 通过 | `answers.tex` 有全部 27+12 个答案；题解以 ref 指向题目，按正文顺序排列。开放实践有可行代码或判断标准，26 个完整答案程序参与实际构建。 |
| 13 作者语言习惯 | 通过 | 参照原 11/12/13 的段落推进、条件说明与操作中的原因解释；不保留原文错误结论，也不为模仿而虚构经历。 |
| 14 图片实际检查 | 通过 | 实际查看 14 张原图及上下文，重绘并查看独立图与正文排版尺寸，统一字体、青色线框、箭头、术语与信息密度。 |
| 15 图片标记与引用 | 通过 | 14 张通过检查后发布为 `_revised.pdf`，includegraphics 与生成脚本路径已同步。旧图保留为历史资源。 |
| 16 文件组织 | 通过 | 编号文件继续沿用；`Chapter2/README.md` 列清实际入口、主题与未启用历史文件，六个项目以概念命名。没有为了外观一致批量移动文件。 |
| 17 包含与引用 | 通过 | 从卷入口展开 23 个文件、156 个标签、102 个被引用标签，无重复/循环包含、失效路径、重复标签、未定义引用；27+12 题解定位检查通过。 |
| 18 源码和格式 | 通过 | 命令、类型、路径与数学复杂度各用对应环境；表格列宽、图片图注、标题、行号与短代码分页协调。短答案在标题前留空间，长程序自然跨页。第一章两处长文本同时作断行修正。 |
| 19 示例实际运行 | 通过 | Ubuntu 24.04.5 / GCC 13.3.0 构建并运行全部 70 个正文/答案程序，无编译警告或非预期失败；10 个关键变体另行核验，详见下文和 evidence。 |
| 20 编译和 PDF | 通过 | 卷入口 XeLaTeX 编译至引用稳定，203 页；无 Overfull、未定义引用或重复标签警告。实际查看目录 7–8、正文 76–139、题解 176–201；未修改共享模板。最后的短代码分页修正另复查受影响页面。 |

## 核心能力与项目覆盖

| 正文与项目 | 示例内容与练习标签（省略共同前缀 ex:v1-cpp-） |
| --- | --- |
| `21.tex`；`examples/class-basics-demo` | 完整类、指定初始化、static/友元、重载、构造/复制/赋值、运算符、继承/多态、函数/类/非类型参数模板；point、count、overload、constructors、operators、inheritance、template。 |
| `22_core.tex`；`examples/lambda-move-demo` | 排序、mutable、函数包装、值/引用/this/*this 捕获、引用绑定、移动构造、重载与转发；capture、sort、reference。reference 的分项同时核验按值/引用传递、实际移动构造和五种转发调用。 |
| `22_smartptr.tex`；`examples/smart-pointer-demo` | unique_ptr 返回/移动、shared_ptr 计数/移动、强循环与 weak 解除循环；unique、shared、weak。 |
| `22_stl.tex`；`examples/stl-container-demo` | vector 容量、list 删除、FIFO/LIFO/优先出队、map/unordered_map、迭代/排序/安全删除；capacity、adapters、parentheses、words、erase。数据结构图与适配器运行比较用于理解机制，不要求学生实现整棵红黑树。 |
| `22_thread.tex`；`examples/thread-coordination-demo` | 生命周期/引用传参、互斥、共享锁、原子、条件变量、promise/future、async、线程池、有界队列、读者写者、哲学家与限时死锁；thread-print、counter、shared-lock、atomic、condition、async、pool、classic。classic 明确检查三个问题与公平性限制。 |
| `22_memory.tex`；`examples/memory-lifetime-demo` | 自动/动态对象寿命、owner.reset、递归进入/返回；memory。内存图、函数返回后悬空的解释与实际析构日志共用一项综合练习。 |

项目中的每个 cpp 单独编译，不要求初学者额外学习工程框架。统一使用简短的 g++ 命令，是因为这一章的目标是观察 C++ 行为；多文件依赖与 CMake 留到第三章展开。

## 运行证据与判断边界

- 全量执行：在用户的 Distrobox `ubuntu2404` 中运行 `python3 scripts/verify_ch2_examples.py --output /tmp/ch2-runtime-final.json`。GCC 为 `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`。44 个正文程序与 26 个答案程序共 70 个，全部编译，运行退出状态均符合预期。记录：`evidence/volume-1-chapter-2-runtime.json`。程序输出逐项检查后支持正文的构造/计数/排序/删除/计数器/结果传递/递归结论。
- 关键变体：Arch GCC 16.2.1 下运行 `scripts/verify_ch2_variants.py`，核验指定初始化次序和仅返回类型不同的重载编译失败；完美转发的五种调用、对象捕获改成 9、shared_ptr 移动后的 1/0 计数、带重复元素的 FIFO/LIFO/最大与最小优先队列；无效迭代器被调试模式诊断；容量 1 的双消费者收齐 0–19；两工作线程执行八任务且各执行一次。记录：`evidence/volume-1-chapter-2-variants.json`。
- 递归实测依次进入 4、3、2、1，返回 3、7、15、31，与图中 f(1)=3、f(n)=2f(n-1)+1 一致。
- 并发日志允许不同线程的行交错；不把输出顺序当同步保证。共享锁可能读到写入前或后的值。限时死锁程序本次正常退出，这只记录该次调度；正文与题解从持锁顺序解释风险，不宣称它不会死锁。
- 保留的数据竞争错误分支需要显式启用 `DEMO_DATA_RACE`，本轮不执行未定义行为来获得某个“错数”；练习要求先解释竞争。失效迭代器用 libstdc++ 调试模式诊断。线程池用于讲协作，没有承诺工作线程创建失败或任意任务异常下的生产级恢复。

技术修正核对了 C++ 标准草案的 [指定初始化](https://eel.is/c++draft/dcl.init.aggr)、[Lambda 捕获](https://eel.is/c++draft/expr.prim.lambda.capture)、[值类别](https://eel.is/c++draft/basic.lval)、[转发](https://eel.is/c++draft/forward)、[vector 修改与失效](https://eel.is/c++draft/vector.modifiers)、[static 成员](https://eel.is/c++draft/class.static.data)、[存储期](https://eel.is/c++draft/basic.stc)、[无序容器要求](https://eel.is/c++draft/unord.req)，调试诊断条件见 [GCC libstdc++ 调试模式文档](https://gcc.gnu.org/onlinedocs/libstdc++/manual/debug_mode_using.html)。这些是语言与库结论的依据；运行证据只代表上述环境与输入。

## 图片与 LaTeX 整理

| 原图（images/） | 正文新图（images/） |
| --- | --- |
| `A111.png` | `inheritance_revised.pdf` |
| `数组.png` | `array-layout_revised.pdf` |
| `链表1.png` | `linked-list_revised.pdf` |
| `队列1.png` | `queue-operations_revised.pdf` |
| `队列2.png` | `queue-states_revised.pdf` |
| `优先队列1.png` | `priority-queue_revised.pdf` |
| `堆栈1.png` | `stack-operations_revised.pdf` |
| `堆栈2.png` | `stack-states_revised.pdf` |
| `树1.png` | `tree-overview_revised.pdf` |
| `树2.png` | `tree-levels_revised.pdf` |
| `最大堆.png` | `heap-examples_revised.pdf` |
| `堆1.png` | `heap-order_revised.pdf` |
| `系统内存.png` | `process-memory_revised.pdf` |
| `栈递归.jpg` | `recursion-stack_revised.pdf` |

生成脚本为 `scripts/render_ch2_diagrams.py`，默认输出候选图，实际查看后才用 `--publish-checked` 发布。重绘统一字体与青色矢量风格，保留必要数据与关系；同时纠正容易误解的分类、堆序和地址示意。优先队列图明确内部存储不保证排序，内存图不承诺固定地址/大小/方向；树保留 A–M 的四层关系，递归保留原始数值。正文所有引用已切换，旧图用于历史追溯。

没有重命名或移动 .tex 文件。实际包含顺序见 `Chapter2/README.md`；历史 `22.tex`、`22_advanced.tex`、`22_iterator.tex` 未启用，避免重复维护同一正文。小项目直接引入源码，题目和题解用标签互相定位。结构脚本只能检查路径/包含/定位，不替代内容、运行和视觉验收。

最终 PDF 中无越界、缺文件或引用未定义问题；保留共享模板原有的楷体粗体/仿宋斜体字体替代提示，本次实际版面检查未发现可读性问题。未修改共享模板或其他卷。
