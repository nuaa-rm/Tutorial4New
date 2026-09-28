#!/usr/bin/env python3
"""卷一第二章矢量图：先检查 candidate，再用 --publish-checked 发布。"""
from pathlib import Path
import argparse,subprocess,tempfile,shutil
from render_ch1_diagrams import HEADER
DIAGRAMS={
'inheritance':r'''
\node[box] (a) at (-4,0) {Animals\\动物基类};
\node[box] (m) at (0,0) {Mammals\\哺乳动物派生类\\run()};
\node[box] (d) at (4,1) {Dog\\run()};
\node[box] (c) at (4,-1) {Cat\\run()};
\draw[flow] (a) -- (m); \draw[flow] (m) -- (d); \draw[flow] (m) -- (c);
\node at (0,-2.2) {箭头从基类指向派生类；每个实例仍包含基类子对象};
''',
'array-layout':r'''
\foreach \x/\value in {0/1,1/2,2/3,3/4,4/5} {
 \node[box,minimum width=1.8cm] at (2*\x,0) {\value};
 \node at (2*\x,-.9) {下标 \x};
}
\node at (4,1) {相邻元素连续存储，可按下标访问};
''',
'linked-list':r'''
\node at (-1,2.4) {单向}; \node at (-1,0) {双向}; \node at (-1,-2.4) {循环};
\foreach \row/\y in {a/2.4,b/0,c/-2.4} {
 \foreach \x/\v in {0/1,1/2,2/3} \node[box] (\row\x) at (3*\x,\y) {数据 \v\\链接};
}
\draw[flow] (a0) -- (a1); \draw[flow] (a1) -- (a2);
\node at (8,2.4) {nullptr}; \draw[flow] (a2) -- (7.2,2.4);
\draw[flow,<->] (b0) -- (b1); \draw[flow,<->] (b1) -- (b2);
\draw[flow] (c0) -- (c1); \draw[flow] (c1) -- (c2);
\draw[flow] (c2.south) -- ++(0,-.6) -| (c0.south);
\node at (3,-4) {节点不必相邻；list 是双向链表，forward\_list 是单向链表};
''',
'queue-operations':r'''
\node[box] (front) at (0,0) {a1\\队头};
\node[box] (a) at (3,0) {a2}; \node[box] (back) at (6,0) {an\\队尾};
\draw[flow] (front) -- node[above]{先取出} (-3,0);
\draw[flow] (9,0) -- node[above]{新元素入队} (back);
\node at (3,-1.5) {先进先出 FIFO；queue 读取 front()，pop() 删除队头};
''',
'queue-states':r'''
\node[box,minimum width=8cm] (a) at (0,3) {初始：A\quad B\quad C\quad D};
\node[box,minimum width=8cm] (b) at (0,1) {A 出队后：B\quad C\quad D};
\node[box,minimum width=8cm] (c) at (0,-1) {E 入队后：B\quad C\quad D\quad E};
\draw[flow] (a) -- (b); \draw[flow] (b) -- (c);
\node at (0,-2.2) {这里展示逻辑次序，不固定底层数组的下标或容量};
''',
'priority-queue':r'''
\node[box] (input) at (0,3.5) {依次插入 1、3、2};
\node[box] (heap) at (0,1.7) {最小堆：堆顶 1};
\node[box] (after) at (0,-.1) {再插入 0：堆顶变成 0};
\draw[flow] (input) -- (heap);\draw[flow] (heap) -- (after);
\node at (0,-1.2) {逐次取出：0、1、2、3；内部存储不等于有序队列};
\node at (0,-2) {std::priority\_queue 默认最大值优先，最小值优先需更改比较器};
''',
'stack-operations':r'''
\node[box,minimum width=4cm] (top) at (0,2) {an\quad 栈顶};
\node[box,minimum width=4cm] at (0,.6) {a2};
\node[box,minimum width=4cm] at (0,-.8) {a1\quad 栈底};
\draw[flow] (-4,3.5) -- node[left]{push} (top.north west);
\draw[flow] (top.north east) -- node[right]{pop} (4,3.5);
\node at (0,-2) {后进先出 LIFO；top() 读取，pop() 删除，不返回元素};
''',
'stack-states':r'''
\foreach \x/\title/\values in {0/初始/1、7、2,1/压入8/8、1、7、2,2/压入2/2、8、1、7、2} {
 \node[box,minimum width=3.1cm,minimum height=2cm] (a\x) at (4*\x,1) {\title\\栈顶 $\downarrow$ 栈底\\\values};
}
\draw[flow] (a0) -- (a1);\draw[flow] (a1) -- (a2);
\node[box,minimum width=3.1cm,minimum height=2cm] (b) at (4,-2.4) {连续 pop 三次\\剩余 7、2};
\draw[flow] (a2.south) -- ++(0,-.7) -| (b.north);
''',
' tree-overview':r'''
\node[box] (r) at (0,3) {树结构};
\node[box] (b) at (-4,1) {二叉树\\每个节点至多两个孩子};
\node[box] (t) at (4,1) {一般树与森林\\孩子数量不限};
\node[box] (bb) at (-4,-1.5) {遍历：前序／中序／后序\\有序搜索：二叉搜索树\\平衡规则：AVL、红黑树};
\node[box] (tt) at (4,-1.5) {遍历、表示与转换\\应用：目录层级、并查集等};
\draw[flow] (r) -- (b);\draw[flow] (r) -- (t);
\draw[flow] (b) -- (bb);\draw[flow] (t) -- (tt);
''',
' tree-levels':r'''
\foreach \name/\x/\y in {A/0/3,B/-3/1.5,C/0/1.5,D/3/1.5,E/-4.3/0,F/-1.7/0,G/0/0,H/1.7/0,I/3/0,J/4.3/0,K/-4.8/-1.5,L/-3.8/-1.5,M/1.7/-1.5} {
 \node[circle,draw=teachingcyan,fill=teachingcyan!6] (\name) at (\x,\y) {\name};
}
\foreach \a/\b in {A/B,A/C,A/D,B/E,B/F,C/G,D/H,D/I,D/J,E/K,E/L,H/M} \draw[flow] (\a) -- (\b);
\foreach \y/\lv in {3/1,1.5/2,0/3,-1.5/4} \node at (6,\y) {第 \lv 层};
\node at (0,-2.5) {按节点层数计，高度为 4；这不是二叉树};
''',
'heap-examples':r'''
\foreach \offset/\label in {0/满足最大堆,6/不满足最大堆} {
 \node[circle,draw=teachingcyan] (r\offset) at (\offset,2) {20};
 \node[circle,draw=teachingcyan] (l\offset) at (\offset-1, .5) {18};
 \node[circle,draw=teachingcyan] (p\offset) at (\offset+1, .5) {10};
 \node[circle,draw=teachingcyan] (a\offset) at (\offset-1.7,-1) {15};
 \node[circle,draw=teachingcyan] (b\offset) at (\offset-.3,-1) {\ifnum\offset=0 8\else 19\fi};
 \draw[flow] (r\offset) -- (l\offset);\draw[flow] (r\offset) -- (p\offset);
 \draw[flow] (l\offset) -- (a\offset);\draw[flow] (l\offset) -- (b\offset);
 \node at (\offset,-2) {\label};
}
\node at (3,-3) {两者形状均为完全二叉树；右图的 18 小于孩子 19，违反堆性质};
''',
'heap-order':r'''
\foreach \name/\x/\y/\v in {a/0/3/9,b/-1.5/1.5/8,c/1.5/1.5/9,d/-2.2/0/4,e/-.8/0/6,f/.8/0/7,g/2.2/0/2,h/6/3/0,i/4.5/1.5/7,j/7.5/1.5/4,k/3.8/0/7,l/5.2/0/9,m/6.8/0/5,n/8.2/0/8} {
 \node[circle,draw=teachingcyan,fill=teachingcyan!6] (\name) at (\x,\y) {\v};
}
\foreach \a/\b in {a/b,a/c,b/d,b/e,c/f,c/g,h/i,h/j,i/k,i/l,j/m,j/n} \draw[flow] (\a) -- (\b);
\node at (0,-1) {最大堆：9、8、9、4、6、7、2};
\node at (6,-1) {最小堆：0、7、4、7、9、5、8};
\node at (3,-2) {数组按层次顺序保存；不保证从左到右整体有序};
''',
'process-memory':r'''
\foreach \y/\title in {0/代码段（通常可执行）、只读数据段,1.4/静态数据（如 data、bss）,2.8/动态分配（堆、映射等）,4.2/线程栈与其他映射} {
 \node[box,minimum width=8cm] at (0,\y) {\title};
}
\node at (0,5.3) {一个进程的虚拟地址空间（简化示意）};
\node at (0,-1.2) {每个线程有自己的栈；位置、大小和方向由实现与环境决定};
''',
'recursion-stack':r'''
\node[box,minimum width=4.6cm] (a) at (0,4.5) {main：调用 f(4)};
\node[box,minimum width=4.6cm] (b) at (0,3) {f(4)：等待 f(3) 返回};
\node[box,minimum width=4.6cm] (c) at (0,1.5) {f(3)：等待 f(2) 返回};
\node[box,minimum width=4.6cm] (d) at (0,0) {f(2)：等待 f(1) 返回};
\node[box,minimum width=4.6cm] (e) at (0,-1.5) {f(1)：返回 3};
\foreach \u/\v/\val in {e/d/3,d/c/7,c/b/15,b/a/31} {
 \draw[flow] (\u.east) -- ++(1,0) |- node[pos=.25,right]{返回 \val} (\v.east);
}
\draw[flow] (-4,5) -- node[left]{逐层调用} (-4,-1.5);
\node at (0,-2.7) {$f(1)=3$；$f(n)=2f(n-1)+1$，$n>1$};
'''}
DIAGRAMS={k.strip():v for k,v in DIAGRAMS.items()}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--publish-checked',action='store_true');args=ap.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='ch2-diagrams-') as temp:
  for name,body in DIAGRAMS.items():
   folder=Path(temp);src=folder/(name+'.tex');src.write_text(HEADER+body+'\n\\end{tikzpicture}\n\\end{document}\n')
   subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',src.name],cwd=folder,check=True,stdout=subprocess.DEVNULL)
   target=args.output_dir/(name+('_revised' if args.publish_checked else '_candidate')+'.pdf');shutil.copy2(src.with_suffix('.pdf'),target);print(target)
if __name__=='__main__':main()
