#!/usr/bin/env python3
"""相机章矢量图；默认候选，实际查看正文尺寸后才能标记。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS = {
'gamma': r'''
\draw[->] (0,0)--(6.4,0) node[right]{输入 $x$};
\draw[->] (0,0)--(0,6.3) node[above]{输出 $y$};
\draw[gray,dashed] (0,0)--(6,6);
\draw[teachingcyan,very thick,domain=0:1,samples=80] plot ({6*\x},{6*pow(\x,1/2.2)});
\draw[teachingcyan!60!black,thick,domain=0:1,samples=80] plot ({6*\x},{6*pow(\x,2.2)});
\node[anchor=west] at (6.6,5.4) {$y=x^{1/2.2}$：提亮暗部};
\node[anchor=west] at (6.6,4.6) {$y=x$：不变};
\node[anchor=west] at (6.6,3.8) {$y=x^{2.2}$：压暗};
\fill[teachingcyan] (1.308,3) circle(2pt);
\draw[dashed,gray] (1.308,0)--(1.308,3)--(0,3);
\node[anchor=west] at (6.6,2.7) {旧图的 $0.218\to0.5$ 近似映射};
\node[anchor=west] at (6.6,1.9) {本项目 $\gamma=2.2$，指数为 $1/\gamma$};
\node at (3,-.55) {0\hspace{4.9cm}1};
\node[anchor=west] at (0,-1.6) {原坡道};
\node[anchor=west] at (1.6,-1.6) {\includegraphics[width=10.5cm,height=.65cm]{RAMP}};
\node[anchor=west] at (0,-2.5) {LUT 输出};
\node[anchor=west] at (1.6,-2.5) {\includegraphics[width=10.5cm,height=.65cm]{MAPPED}};
\node at (6,-3.3) {坡道来自实际运行；简单幂律不是完整 sRGB 编码};
''',
'focus': r'''
\foreach \dy/\a/\name in {0/1.2/大光圈,-4.6/.6/小光圈} {
 \begin{scope}[yshift=\dy cm]
 \draw[gray,->] (-5,0)--(4.7,0);
 \draw[teachingcyan,very thick] (0,-1.5)--(0,1.5);
 \node[above] at (0,1.5) {镜头 / 入瞳};
 \fill[teachingcyan] (-4.5,0) circle(2pt);
 \node[below] at (-4.5,-.1) {同一物点};
 \foreach \sgn in {-1,1} {
  \draw[teachingcyan,thick] (-4.5,0)--(0,{\sgn*\a})--(3,0)--(4,{-\sgn*\a/3});
 }
 \draw[dashed,gray] (3,-1.6)--(3,1.6);
 \node[above] at (3,1.6) {严格合焦平面};
 \draw[black,thick] (2.3,-1.5)--(2.3,1.5);
 \draw[teachingcyan!65!black,very thick] (2.3,{-.7*\a/3})--(2.3,{.7*\a/3});
 \node[below,align=center] at (2.3,-1.5) {固定传感器平面\\弥散圆直径取决于光束宽度};
 \node[box] at (-3,1.35) {\name};
 \end{scope}
}
\node[align=center] at (.1,-8.3) {同样失焦量，小光圈的几何模糊较小；图示不按真实比例\\
物方可接受范围是景深，像方可接受范围是焦深；极小光圈还受衍射影响};
''',
'dof': r'''
\draw[gray,->] (-6,2)--(6,2) node[right]{物距 $s$};
\draw[teachingcyan,line width=3pt] (-3.5,2)--(4.5,2);
\foreach \x/\label in {-3.5/近界,0/对焦距离,4.5/远界} {
 \draw (\x,1.8)--(\x,2.2); \node[above] at (\x,2.3) {\label};
}
\draw[<->,teachingcyan] (-3.5,1)--(0,1) node[midway,above]{前景深 $\Delta_1$};
\draw[<->,teachingcyan] (0,.1)--(4.5,.1) node[midway,above]{后景深 $\Delta_2$};
\node[box,minimum width=13cm] at (0,-1.7) {$\displaystyle
\Delta_1=\frac{Nc\,s(s-f)}{f^2+Nc(s-f)},\qquad
\Delta_2=\frac{Nc\,s(s-f)}{f^2-Nc(s-f)}$\\[2mm]
有限远界要求 $f^2>Nc(s-f)$；否则远界为无穷};
\node[box,minimum width=13cm] at (0,-4.1) {$\displaystyle
\mathrm{DOF}=\frac{2f^2Nc\,s(s-f)}{f^4-N^2c^2(s-f)^2}$\\[2mm]
$\displaystyle s\gg f:\quad \mathrm{DOF}\approx
\frac{2f^2Nc\,s^2}{f^4-N^2c^2s^2}$};
\node at (0,-5.6) {长度单位统一；$N$ 为光圈数，$c$ 为容许弥散圆，不预设为一像元};
\node at (0,-6.3) {沿用薄透镜几何关系；示意不按距离比例绘制，不计算多片镜头与衍射};
'''
}

cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--output-dir', type=Path, required=True)
cli.add_argument('--format-dir', type=Path, required=True)
cli.add_argument('--publish-checked', action='store_true')
args=cli.parse_args()
args.output_dir.mkdir(parents=True,exist_ok=True)
head=HEADER.replace(r'\usepackage[UTF8', r'\usepackage{amsmath,graphicx}'+'\n'+r'\usepackage[UTF8')
for name, content in DIAGRAMS.items():
    content=content.replace('RAMP',str((args.format_dir/'ramp.png').resolve()))
    content=content.replace('MAPPED',str((args.format_dir/'mapped.png').resolve()))
    with tempfile.TemporaryDirectory(prefix='camera-figure-') as t:
        folder=Path(t)
        (folder/'figure.tex').write_text(head+content+'\n'+chr(92)+'end{tikzpicture}\n'+chr(92)+'end{document}\n')
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],
                       cwd=folder,check=True,stdout=subprocess.DEVNULL)
        target=args.output_dir/f'camera_{name}_{"revised" if args.publish_checked else "candidate"}.pdf'
        shutil.copy2(folder/'figure.pdf',target)
        print(target)
