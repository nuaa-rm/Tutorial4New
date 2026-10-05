#!/usr/bin/env python3
"""生成大图像通信路径图；查看候选图及正文尺寸后再发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

BODY = r'''
\node[anchor=west] at (-6.7,6.1) {跨进程：先检查 RMW 的实际传输路径};
\node[box,minimum width=3.0cm] (a) at (-4.8,4.9) {相机节点\\应用图像缓冲区};
\node[box,minimum width=3.0cm] (b) at (-1.2,4.9) {发送端 DDS\\历史 / 传输缓冲区};
\node[box,minimum width=3.0cm] (c) at (2.4,4.9) {接收端 DDS\\历史 / 传输缓冲区};
\node[box,minimum width=3.0cm] (d) at (6.0,4.9) {识别节点\\应用图像缓冲区};
\draw[flow] (a)--(b);
\draw[flow] (b)--(c);
\draw[flow] (c)--(d);
\node[align=center] at (0.6,3.45) {序列化、缓存及复制次数由实现与配置决定\\
共享内存传输（SHM）可以减少网络开销，仍可能复制样本};
\node[anchor=west] at (-6.7,1.95) {同一组件容器 + 进程内通信：本章首先验证的路径};
\draw[teachingcyan,dashed,rounded corners] (-6.65,-0.1) rectangle (7.7,1.5);
\node[box,minimum width=3.2cm] (e) at (-4.5,.75) {Source 组件\\持有 UniquePtr};
\node[box,minimum width=3.9cm] (f) at (.6,.75) {rclcpp 进程内通道\\移动所有权，保留像素地址};
\node[box,minimum width=3.2cm] (g) at (5.65,.75) {Sink 组件\\接过 UniquePtr};
\draw[flow] (e)--(f); \draw[flow] (f)--(g);
\node at (.6,-.65) {此图限定一对一且没有进程外订阅者；图像生成与算法处理仍有成本};
\node[anchor=west] at (-6.7,-2.1) {跨进程的完整零拷贝：三段条件都要满足};
\node[box,minimum width=3.0cm] (h) at (-4.8,-3.3) {发布端应用\\借出样本};
\node[box,minimum width=3.0cm] (i) at (-1.2,-3.3) {DDS 写端\\共享样本池};
\node[box,minimum width=3.0cm] (j) at (2.4,-3.3) {DDS 读端\\访问同一批样本};
\node[box,minimum width=3.0cm] (k) at (6.0,-3.3) {订阅端应用\\借出读取 / 归还};
\draw[flow] (h)--(i); \draw[flow] (i)--(j); \draw[flow] (j)--(k);
\node[align=center] at (.6,-4.75) {两端 DDS 经 Data Sharing 访问共享历史；消息布局与生命周期须分别核实\\
本章 loan\_probe 只验证发布端能力；普通 Image 不因此获得跨进程零拷贝};
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--publish-checked', action='store_true')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ros-image-path-figure-') as temporary:
        build = Path(temporary)
        source = build / 'paths.tex'
        source.write_text(HEADER + BODY + '\n\\end{tikzpicture}\n\\end{document}\n')
        subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', source.name],
                       cwd=build, check=True, stdout=subprocess.DEVNULL)
        suffix = 'revised' if args.publish_checked else 'candidate'
        target = args.output_dir / f'ros2_image_paths_{suffix}.pdf'
        shutil.copy2(source.with_suffix('.pdf'), target)
        print(target)


if __name__ == '__main__':
    main()
