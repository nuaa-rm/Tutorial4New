#!/usr/bin/env python3
"""重建卷一第 1 章矢量插图。候选图先生成到临时目录，核对后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADER = r'''\documentclass[tikz,border=6pt]{standalone}
\usepackage[UTF8,fontset=fandol]{ctex}
\usetikzlibrary{arrows.meta,positioning}
\definecolor{teachingcyan}{RGB}{0,145,160}
\tikzset{box/.style={draw=teachingcyan,fill=teachingcyan!6,rounded corners=2pt,
  align=center,minimum height=10mm,font=\small},
  flow/.style={-{Stealth[length=2mm]},thick,draw=teachingcyan},
  every node/.style={font=\small}}
\begin{document}
\begin{tikzpicture}
'''
DIAGRAMS = {
    'linux-directory': r'''
\node[box] (root) at (0,3) {根目录 /};
\node[box] (home) at (-4,1.5) {/home};
\node[box] (usr) at (0,1.5) {/usr};
\node[box] (etc) at (3,1.5) {/etc};
\node[box] (var) at (5,1.5) {/var};
\node[box] (dev) at (-6,1.5) {/dev};
\draw[thick,draw=teachingcyan] (root.south) -- (0,2.3) -- (-6,2.3);
\draw[thick,draw=teachingcyan] (0,2.3) -- (5,2.3);
\foreach \n in {home,usr,etc,var,dev} \draw[flow] (\n.north |- 0,2.3) -- (\n.north);
\node[box] (alice) at (-4,0) {alice\quad bob\quad eve};
\node[box] (bins) at (0,0) {bin\quad sbin\quad lib\quad local};
\draw[flow] (home) -- (alice); \draw[flow] (usr) -- (bins);
\node at (0,-1) {其余常见目录：/boot、/root、/run、/tmp、/opt 等};
\node[box] (links) at (0,-2) {/bin $\rightarrow$ /usr/bin\quad /sbin $\rightarrow$ /usr/sbin\\
/lib $\rightarrow$ /usr/lib\quad（常见 usr-merge 布局）};
''',
    'mount': r'''
\node[box] (device) at (-3,2) {分区设备节点\\/dev/sdb1};
\node[box] (filesystem) at (3,2) {该分区的文件系统\\a.txt\quad b.txt};
\draw[flow] (device) -- node[above]{标识} (filesystem);
\node[box] (root) at (-3,0) {Linux 目录树\\/};
\node[box] (point) at (3,0) {挂载点\\/media/alice/USB};
\draw[flow] (root) -- node[above]{目录路径} (point);
\draw[flow] (filesystem) -- node[right]{挂载后访问} (point);
\node at (0,-1.3) {文件路径：/media/alice/USB/a.txt；不直接向 /dev/sdb1 写文本};
''',
    'shell': r'''
\node[box,minimum width=10cm] (user) at (0,3.8) {用户：输入命令或点击界面};
\node[box,minimum width=4cm] (shell) at (-3,2.2) {Shell（如 Bash）\\解释命令，启动程序};
\node[box,minimum width=4cm] (app) at (3,2.2) {其他应用\\编辑器、图形程序等};
\node[box,minimum width=10cm] (kernel) at (0,0.4) {内核 Kernel：进程、文件系统、设备驱动与网络};
\node[box,minimum width=10cm] (hardware) at (0,-1.3) {硬件：CPU、内存、磁盘、显示器等};
\draw[flow] (user) -- (shell); \draw[flow] (user) -- (app);
\draw[flow] (shell) -- node[above]{可启动} (app);
\draw[flow] (shell) -- node[left]{系统调用} (kernel);
\draw[flow] (app) -- node[right]{系统调用} (kernel);
\draw[flow] (kernel) -- (hardware);
''',
    'git-workflow': r'''
\node[box,minimum width=2.7cm] (work) at (0,1.3) {工作区\\编辑后的文件};
\node[box,minimum width=2.7cm] (index) at (5,1.3) {暂存区\\准备提交的快照};
\node[box,minimum width=2.7cm] (local) at (10,1.3) {本地仓库\\提交历史};
\node[box,minimum width=2.7cm] (remote) at (10,-2) {远程仓库\\交换提交};
\draw[flow] (work) -- node[above,font=\footnotesize]{git add} (index);
\draw[flow] (index) -- node[above,font=\footnotesize]{git commit} (local);
\draw[flow] ([xshift=5mm]local.south) -- node[right]{git push} ([xshift=5mm]remote.north);
\draw[flow] ([xshift=-5mm]remote.north) -- node[left]{git fetch} ([xshift=-5mm]local.south);
\draw[flow] (local.north) -- ++(0,1) -| node[pos=0.25,above]{switch / restore（按实际状态使用）} (work.north);
\draw[flow] (remote.west) -- (0,-2) -- node[left]{git clone} (work.south);
\node at (3,-3) {git diff：工作区与暂存区；git diff --cached：暂存区与当前提交};
''',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--publish-checked', action='store_true', help='仅在候选图及正文尺寸已检查后使用')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='textbook-diagrams-') as folder:
        build = Path(folder)
        for name, body in DIAGRAMS.items():
            source = build / (name + '.tex')
            source.write_text(HEADER + body + '\n\\end{tikzpicture}\n\\end{document}\n')
            subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', source.name],
                           cwd=build, check=True, stdout=subprocess.DEVNULL)
            target = args.output_dir / (name + ('_revised' if args.publish_checked else '_candidate') + '.pdf')
            shutil.copy2(source.with_suffix('.pdf'), target)
            print(target)


if __name__ == '__main__':
    main()
