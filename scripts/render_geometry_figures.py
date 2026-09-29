#!/usr/bin/env python3
"""几何章投影、P3P和BA图；实际查看候选及正文尺寸后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS = {
"model": r'''
\coordinate (O) at (-4,0); \coordinate (P) at (4,2);
\draw[gray,->] (O)--(5,0) node[right]{$Z$};
\draw[gray,->] (O)--(-4,3) node[above]{$X$};
\draw[teachingcyan,thick] (-1.5,-.5)--(-1.5,2.6);
\node[align=center] at (-.5,2.8) {$Z=1$\\归一化平面};
\draw[flow] (O)--(P);
\fill[teachingcyan] (O) circle (2pt) node[below left]{光心 $O$};
\fill[teachingcyan] (P) circle (2pt) node[right]{$P_c=(X,Y,Z)^T$};
\fill[teachingcyan] (-1.5,.625) circle (2pt) node[above right]{$x=X/Z$};
\draw[dashed,gray] (P)--(4,0);
\node at (1,-.9) {仅画 $X/Z$ 截面；$y=Y/Z$ 同理；有效点 $Z>0$};
\node[box,minimum width=4cm] (world) at (-5,-2.4) {世界/物体点 $P$\\先用 $T_{cw}$ 变到相机系};
\node[box,minimum width=3.8cm] (normal) at (0,-2.4) {相机点 $(X,Y,Z)$\\除深度得到 $(x,y)$};
\node[box,minimum width=4cm] (pixel) at (5,-2.4) {用 $K$ 得到 $(u,v)$\\$u=f_xx+c_x$};
\draw[flow] (world)--(normal); \draw[flow] (normal)--(pixel);
\node[align=center] at (0,-4) {无畸变模型；$f_x$ 的单位是 pixel\\
虚拟平面用于推导，不代表传感器的安装位置};
''',
"p3p": r'''
\begin{scope}[yscale=.58]
\coordinate (O) at (0,4.5);
\coordinate (a) at (-1.4,1.15); \coordinate (b) at (0,.95); \coordinate (c) at (1.2,1.45);
\coordinate (A) at (-2.52,-1.53); \coordinate (B) at (0,-2.955); \coordinate (C) at (2.64,-2.21);
\fill[teachingcyan!6] (-2.4,1)--(1.8,1.8)--(2.2,.3)--(-2,.1)--cycle;
\draw[teachingcyan] (-2.4,1)--(1.8,1.8)--(2.2,.3)--(-2,.1)--cycle;
\node[align=left] at (4.5,1.2) {去畸变后\\得到单位射线\\$\boldsymbol a,\boldsymbol b,\boldsymbol c$};
\foreach \n/\p in {A/a,B/b,C/c} {
 \draw[flow] (O)--(\n);
 \fill[teachingcyan] (\p) circle (2pt) node[above left]{$\p$};
 \fill[teachingcyan] (\n) circle (2pt) node[below]{$\n$};
}
\fill[teachingcyan] (O) circle (2pt) node[above]{光心 $O$};
\draw[thick,gray] (A)--(B)--(C)--cycle;
\node[align=left] at (-4.7,.4) {$OA=l_A$\\$OB=l_B$\\$OC=l_C$};
\end{scope}
\node[box,minimum width=12cm] at (0,-3.2) {$l_A^2+l_B^2-2l_Al_B(\boldsymbol a^T\boldsymbol b)=|AB|^2$\\
其他两边同理；射线夹角与空间边长已知，三个距离待求};
\node at (0,-4.6) {$l_A,l_B,l_C$ 不必相同；图像与空间三角形一般不相似};
''',
"graph": r'''
\node[box,minimum width=3cm] (c0) at (-5,3) {相机0位姿\\固定为参考};
\node[box,minimum width=3cm] (c1) at (0,3) {相机1位姿\\参与优化};
\node[box,minimum width=3cm] (c2) at (5,3) {相机2位姿\\参与优化};
\node[box,minimum width=3cm] (p0) at (-3,-1) {路标 $P_0$\\三维点};
\node[box,minimum width=3cm] (p1) at (3,-1) {路标 $P_1$\\三维点};
\foreach \c in {c0,c1,c2} \foreach \p in {p0,p1} {
 \draw[thick,draw=teachingcyan!70] (\c.south)--(\p.north);
}
\node[align=center] at (0,-2) {每边：$e_{ij}=z_{ij}-\pi(T_{cw,i}P_j)$；线的交叉不表示顶点};
\node[box,minimum width=13cm] at (0,-3.5) {这里画5顶点、6观测边；每边有2个像素残差分量\\
固定参考消掉整体刚体自由度；单目尺度还需单独约束};
\node at (0,-5) {实际项目：3相机、20点、60观测；首点已知深度作为尺度锚};
'''
}
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument("--output-dir",type=Path,required=True)
cli.add_argument("--publish-checked",action="store_true")
args=cli.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
suffix="revised" if args.publish_checked else "candidate"
head=HEADER.replace(r"\usepackage[UTF8",r"\usepackage{amsmath}"+"\n"+r"\usepackage[UTF8")
for kind,body in DIAGRAMS.items():
    with tempfile.TemporaryDirectory(prefix="geometry-figure-") as t:
        folder=Path(t)
        (folder/"figure.tex").write_text(head+body+"\n"+chr(92)+"end{tikzpicture}\n"+chr(92)+"end{document}\n")
        subprocess.run(["xelatex","-interaction=nonstopmode","-halt-on-error","figure.tex"],
            cwd=folder,check=True,stdout=subprocess.DEVNULL)
        shutil.copy2(folder/"figure.pdf",args.output_dir/f"geometry_{kind}_{suffix}.pdf")
print(args.output_dir)
