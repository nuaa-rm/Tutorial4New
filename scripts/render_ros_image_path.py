#!/usr/bin/env python3
"""生成大图像通信路径图；查看候选图及正文尺寸后再发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

BODY = r'''
\definecolor{copyorange}{RGB}{164,93,36}
\tikzset{
  process/.style={draw=teachingcyan!60,dashed,rounded corners=3pt},
  shared/.style={box,fill=teachingcyan!14,minimum width=3.3cm},
  copying/.style={flow,draw=copyorange,dashed},
  pathlabel/.style={font=\footnotesize,fill=white,inner sep=1.5pt}}

% 1. 消息所有权在同一进程内交接。
\node[anchor=west,font=\small\bfseries] at (-7.15,6.45) {1\quad 进程内传递};
\draw[process] (-7.15,3.75) rectangle (7.15,6.05);
\node at (0,5.7) {同一个进程：ROS2 组件容器};
\node[box,minimum width=3.1cm] (source) at (-4.8,4.9) {Source 组件\\持有 UniquePtr};
\node[box,minimum width=4.2cm] (intra) at (0,4.9) {rclcpp 进程内通道\\转移消息所有权};
\node[box,minimum width=3.1cm] (sink) at (4.8,4.9) {Sink 组件\\接过 UniquePtr};
\draw[flow] (source)--(intra);
\draw[flow] (intra)--(sink);
\node[font=\footnotesize] at (0,4.08) {交接前后使用同一份消息与像素缓冲区};

% 2. Fast DDS 的 SHM transport 共享传输缓冲区，两端历史各存一份数据。
\node[anchor=west,font=\small\bfseries] at (-7.15,3.15) {2\quad Fast DDS 的 SHM transport：共享传输缓冲区};
\draw[process] (-7.15,-.65) rectangle (-2.65,2.75);
\draw[process] (2.65,-.65) rectangle (7.15,2.75);
\node at (-4.9,2.4) {发布进程};
\node at (4.9,2.4) {订阅进程};
\node[box,minimum width=3.1cm] (pubapp) at (-4.9,1.6) {发布端应用\\应用图像缓冲区};
\node[box,minimum width=3.1cm] (writer) at (-4.9,.1) {DDS 写端\\发送历史};
\node[shared,minimum height=1.2cm] (transport) at (0,.1) {共享传输缓冲区\\序列化数据};
\node[box,minimum width=3.1cm] (reader) at (4.9,.1) {DDS 读端\\接收历史};
\node[box,minimum width=3.1cm] (subapp) at (4.9,1.6) {订阅端应用\\应用图像缓冲区};
\draw[flow] (pubapp)--node[pathlabel,right]{序列化} (writer);
\draw[copying] (writer)--node[pathlabel,above]{复制写入} (transport);
\draw[copying] (transport)--node[pathlabel,above]{复制读出} (reader);
\draw[flow] (reader)--node[pathlabel,left]{反序列化} (subapp);

% 3. 共享样本路径涵盖 Fast DDS Data Sharing 和 Cyclone DDS/iceoryx。
\node[anchor=west,font=\small\bfseries] at (-7.15,-1.05) {3\quad 完整的跨进程零拷贝：共享同一份样本};
\draw[process] (-7.15,-4.85) rectangle (-2.65,-1.45);
\draw[process] (2.65,-4.85) rectangle (7.15,-1.45);
\node at (-4.9,-1.8) {发布进程};
\node at (4.9,-1.8) {订阅进程};
\node[box,minimum width=3.1cm] (loanpub) at (-4.9,-2.6) {发布端应用\\填充借出样本};
\node[box,minimum width=3.1cm] (loanwriter) at (-4.9,-4.1) {DDS 写端\\管理共享样本};
\node[shared,minimum height=2.2cm] (pool) at (0,-3.35) {共享样本池\\同一份消息数据};
\node[align=center,font=\footnotesize] at (0,-1.8) {Fast DDS：Data Sharing\\Cyclone DDS：iceoryx};
\node[box,minimum width=3.1cm] (loanreader) at (4.9,-4.1) {DDS 读端\\引用共享样本};
\node[box,minimum width=3.1cm] (loansub) at (4.9,-2.6) {订阅端应用\\借出读取 / 归还};
\draw[flow] (loanpub.east)--node[pathlabel,above]{直接填充} ([yshift=6mm]pool.west);
\draw[flow] ([yshift=6mm]pool.east)--node[pathlabel,above]{直接读取} (loansub.west);
\draw[flow] (loanwriter.east)--node[pathlabel,below]{样本引用} ([yshift=-6mm]pool.west);
\draw[flow] ([yshift=-6mm]pool.east)--node[pathlabel,below]{样本引用} (loanreader.west);
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
