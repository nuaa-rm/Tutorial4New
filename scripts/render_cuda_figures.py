#!/usr/bin/env python3
"""CUDA 章节关系图；默认候选，实际检查后才能发布标记。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS = {
'host': r'''
\node[box,minimum width=5.5cm] (h) at (-3.8,3) {Host：CPU 与主机内存\\程序组织、输入与输出\\少量 CPU 核；L1/L2/L3 缓存};
\node[box,minimum width=6.3cm] (d) at (3.8,3) {Device：GPU 与设备内存\\多个 SM；大量 CUDA 线程\\寄存器、块内 Shared/L1、L2};
\draw[flow] (h.east) -- node[above] {上传 H2D} (d.west);
\node[box,minimum width=5.5cm] (out) at (-3.8,0) {Host 检查结果\\向量加法：输入 $A,B$，输出 $C$\\三个设备数组共 $3n\cdot4$ 字节};
\node[box,minimum width=6.3cm] (k) at (3.8,0) {Device 执行 kernel\\上传两个输入：$2n\cdot4$ 字节\\下载一个输出：$n\cdot4$ 字节};
\draw[flow] (h)--(out);\draw[flow] (d)--(k);
\draw[flow] (k.west) -- node[above] {下载 D2H} (out.east);
\node at (0,-1.5) {独立显卡的简化关系；不规定核心数量、缓存大小或所有平台的互连形式};
''',
'grid': r'''
\node at (0,3) {Grid：$n=10$，每块 4 线程，向上取整得到 3 块};
\foreach \b in {0,1,2} {
    \node[box,minimum width=3.7cm,minimum height=2.3cm] at ({(\b-1)*4.8},0.7) {};
    \node at ({(\b-1)*4.8},1.5) {Block \b};
    \foreach \t in {0,1,2,3} {
        \pgfmathtruncatemacro{\i}{4*\b+\t}
        \node at ({(\b-1)*4.8+(\t-1.5)*.8},.75) {$t_{\t}$};
        \ifnum\i<10
        \node[draw=cyan!70!black,fill=cyan!8,minimum width=.65cm] at ({(\b-1)*4.8+(\t-1.5)*.8},0) {\i};
        \else
        \node[draw=gray,fill=gray!15,minimum width=.65cm] at ({(\b-1)*4.8+(\t-1.5)*.8},0) {\i};
        \fi
    }
}
\node at (0,-1.2) {$i=\texttt{blockIdx.x}\cdot\texttt{blockDim.x}+\texttt{threadIdx.x}$};
\node at (0,-2) {浅青色 0--9 访问数组；灰色 10/11 仍启动，但由 $i<n$ 跳过访问};
''',
'reduction': r'''
\node[box,minimum width=12cm] (x) at (0,5) {示意：4 线程，最后一块只剩两个输入 1、2};
\node[box,minimum width=12cm] (a) at (0,3.7) {Shared 初始化：$[1,\ 2,\ 0,\ 0]$；无效线程写 0，再全块同步};
\node[box,minimum width=12cm] (b) at (0,2.2) {step=2：t0 加 t2，t1 加 t3，前半段为 $[1,\ 2]$；全块同步};
\node[box,minimum width=12cm] (c) at (0,.7) {step=1：t0 加 t1 得 3；全块同步，然后 t0 写 partial};
\draw[flow] (x)--(a);\draw[flow] (a)--(b);\draw[flow] (b)--(c);
\node at (0,-.6) {实际程序块大小 32--512 的二次幂；这里用 4 个位置画清机制};
\node at (0,-1.4) {各块输出一个 partial，最后由 Host 汇总；块内屏障不能同步不同块};
''',
'timing': r'''
\node at (0,5.5) {三个相同算子：乘 2 $\to$ 加 1 $\to$ 限幅；输出逐元素核对};
\node[box,minimum width=13cm] (a) at (0,4.1) {逐步往返：上传 $\to$ 核0 $\to$ 下载 $\to$ 上传 $\to$ 核1 $\to$ 下载\\$\to$ 上传 $\to$ 核2 $\to$ 下载；传输 $6n\cdot4$ 字节};
\node[box,minimum width=13cm] (b) at (0,2.2) {设备留存：上传 $\to$ 核0 $\to$ 核1 $\to$ 核2 $\to$ 下载\\传输 $2n\cdot4$ 字节；主机时钟包含这些动作及等待};
\node[box,minimum width=13cm] at (0,.3) {事件区间：begin $\to$ 核0 $\to$ 核1 $\to$ 核2 $\to$ end\\先等待 end 完成再读时间；不含上传与下载};
\node at (0,-1) {先预热，再报告奇数次重复的中位数；图示没有按时间比例绘制};
\node at (0,-1.8) {内存分配、输入生成、结果校验在计时外；相机采集、排队和前后处理另算};
'''
}


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--kind',choices=DIAGRAMS,required=True)
    cli.add_argument('--output-dir',type=Path,required=True)
    cli.add_argument('--publish-checked',action='store_true')
    args=cli.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    target=args.output_dir/f'cuda_{args.kind}_{"revised" if args.publish_checked else "candidate"}.pdf'
    head=HEADER.replace('\\usepackage[UTF8','\\usepackage{amsmath}\n\\usepackage[UTF8')
    with tempfile.TemporaryDirectory(prefix='cuda-figure-') as t:
        folder=Path(t)
        (folder/'figure.tex').write_text(head+DIAGRAMS[args.kind]+'\n'+chr(92)+'end{tikzpicture}\n'+chr(92)+'end{document}\n')
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=folder,check=True,stdout=subprocess.DEVNULL)
        shutil.copy2(folder/'figure.pdf',target)
    print(target)


if __name__=='__main__':main()
