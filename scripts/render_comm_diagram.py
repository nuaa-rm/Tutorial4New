#!/usr/bin/env python3
"""重绘字节流分片图，候选图经正文尺寸检查后才发布 revised。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

BODY = r'''
\node[box,minimum width=11cm] (wire) at (0,4.5) {连续字节流：02 41 42 03 58 59 5A\\两个载荷：AB 与 XYZ；长度字节不属于载荷};
\node[box,minimum width=3.2cm] (c1) at (-4,2.5) {输入块 1\\02 41};
\node[box,minimum width=3.2cm] (c2) at (0,2.5) {输入块 2\\42 03 58};
\node[box,minimum width=3.2cm] (c3) at (4,2.5) {输入块 3\\59 5A};
\draw[flow] (wire.south) -- (c1.north);
\draw[flow] (wire.south) -- (c2.north);
\draw[flow] (wire.south) -- (c3.north);
\node[box,minimum width=3.2cm] (p1) at (-4,0.5) {尚未收齐\\缓存：02 41\\输出：空列表};
\node[box,minimum width=3.2cm] (p2) at (0,0.5) {收齐第一帧\\缓存：03 58\\输出：[AB]};
\node[box,minimum width=3.2cm] (p3) at (4,0.5) {收齐第二帧\\缓存：空\\输出：[XYZ]};
\draw[flow] (c1) -- (p1);\draw[flow] (c2) -- (p2);\draw[flow] (c3) -- (p3);
\draw[flow] (p1.east) -- (p2.west);\draw[flow] (p2.east) -- (p3.west);
\node at (0,-1) {横向箭头表示上一轮缓存继续使用；总输出为 [AB, XYZ]};
\node at (0,-1.7) {输入块是本次固定实验安排，不代表 TCP 每次 recv 的固定边界};
'''

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output-dir',type=Path,required=True)
    cli.add_argument('--publish-checked',action='store_true')
    args=cli.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='comm-diagram-') as temp:
        folder=Path(temp)
        (folder/'figure.tex').write_text(HEADER+BODY+'\n\\end{tikzpicture}\n\\end{document}\n')
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=folder,check=True,stdout=subprocess.DEVNULL)
        target=args.output_dir/('comm_stream'+('_revised' if args.publish_checked else '_candidate')+'.pdf')
        shutil.copy2(folder/'figure.pdf',target)
        print(target)

if __name__=='__main__':main()
