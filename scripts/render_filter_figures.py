#!/usr/bin/env python3
"""滤波关系图与声明条件的协方差示意；候选检查后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS = {
'motion': r'''
\draw[gray,->] (-6,0)--(6,0) node[right]{位置 $p$ / m};
\node[box,minimum width=2cm,minimum height=1.4cm] (b) at (-2,1) {滑块 B};
\draw[flow] (-2,2.2)--(1,2.2) node[midway,above]{速度 $v$ / (m/s)};
\node[box,dashed,minimum width=2cm,minimum height=1.4cm] at (3,1) {下一时刻};
\draw[<->,teachingcyan] (-2,-.6)--(3,-.6) node[midway,below]{$\Delta p\approx v\Delta t$};
\node[box,minimum width=12cm] at (0,-2) {状态 $[p,v]^T$；位置观测 $z=p+n$；不直接观测速度\\
短时间常速度模型；未知加速度造成过程偏差};
''',
'flow': r'''
\node[box,minimum width=4cm] (previous) at (-5,4) {上一时刻后验\\$\boldsymbol x_{k-1}^+,P_{k-1}^+$};
\node[box,minimum width=5cm] (prior) at (1,4) {预测：$F,Q$\\$\boldsymbol x_k^-,P_k^-$};
\draw[flow] (previous)--(prior);
\node[box,minimum width=5cm] (observation) at (-5,1.6) {当前观测 $\boldsymbol z_k$\\观测关系 $H$，噪声 $R$};
\node[box,minimum width=5cm] (residual) at (1,1.6) {比较：$\boldsymbol r=\boldsymbol z-H\boldsymbol x^-$\\$S=HP^-H^T+R$};
\draw[flow] (observation)--(residual); \draw[flow] (prior)--(residual);
\node[box,minimum width=5cm] (gain) at (1,-.8) {增益：$K=P^-H^TS^{-1}$\\$\boldsymbol x^+=\boldsymbol x^-+K\boldsymbol r$\\Joseph 形式更新 $P^+$};
\draw[flow] (residual)--(gain);
\node[box,minimum width=4cm] (next) at (-5,-.8) {当前后验\\交给下一时刻预测};
\draw[flow] (gain)--(next);
\node at (-2,-2.2) {均值和协方差一起递推；缺测时仅预测，不重复使用旧观测};
''',
'weights': r'''
\node[box,minimum width=13cm] at (0,5) {$\lambda=\alpha^2(n+\kappa)-n,\quad c=n+\lambda>0,\quad L_cL_c^T=cP$\\
$\chi_0=\boldsymbol x,\quad\chi_i=\boldsymbol x+(L_c)_{:i},\quad
\chi_{n+i}=\boldsymbol x-(L_c)_{:i}$};
\node[box,minimum width=13cm] at (0,2.8) {$\displaystyle
W_0^{(m)}=\frac{\lambda}{c},\quad
W_0^{(c)}=\frac{\lambda}{c}+1-\alpha^2+\beta$\\[2mm]
$\displaystyle W_i^{(m)}=W_i^{(c)}=\frac1{2c}\quad(i=1,\ldots,2n)$};
\node[box,minimum width=13cm] at (0,.3) {本项目默认 $n=2,\ \alpha=1,\ \kappa=0,\ \beta=2$\\
$\lambda=0,\ c=2$；5 个点；中心 $W^{(m)}=0,\ W^{(c)}=2$\\
另外 4 个点的两个权重均为 $1/4$；均值权重和为 1};
\node at (0,-1.4) {权重不是每个点的概率；协方差权重不必和为 1};
\node at (0,-2.2) {下三角因子取列；正定要求、分布先验与浮点误差仍需检查};
'''
}
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--output-dir',type=Path,required=True)
cli.add_argument('--font',type=Path)
cli.add_argument('--only-covariance',action='store_true')
cli.add_argument('--publish-checked',action='store_true')
args=cli.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
suffix='revised' if args.publish_checked else 'candidate'
head=HEADER.replace(r'\usepackage[UTF8',r'\usepackage{amsmath}'+'\n'+r'\usepackage[UTF8')
for kind,body in ({} if args.only_covariance else DIAGRAMS).items():
    with tempfile.TemporaryDirectory(prefix='filter-figure-') as t:
        folder=Path(t);(folder/'figure.tex').write_text(head+body+'\n'+chr(92)+'end{tikzpicture}\n'+chr(92)+'end{document}\n')
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=folder,check=True,stdout=subprocess.DEVNULL)
        shutil.copy2(folder/'figure.pdf',args.output_dir/f'filter_{kind}_{suffix}.pdf')
if args.font:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(str(args.font))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=str(args.font)).get_name(),
        'font.size':13,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':3})
    rng=np.random.default_rng(2026);a=rng.normal(size=400);b=rng.normal(size=400)
    fig,axes=plt.subplots(2,3,figsize=(10,6),layout='constrained')
    for ax,rho in zip(axes.reshape(-1)[:5],(-1.,-.8,0.,.8,1.)):
        x=a;y=rho*a+np.sqrt(1-rho**2)*b
        ax.scatter(x,y,s=5,color='#0091a0',alpha=.6)
        ax.set(title=f'理论相关 {rho:g}，两轴方差1',xlabel='X',ylabel='Y',xlim=(-3.5,3.5),ylim=(-3.5,3.5))
        ax.set_aspect('equal');ax.grid(alpha=.15)
    ax=axes[1,2];ax.scatter(2*a,b,s=5,color='#0091a0',alpha=.6)
    ax.set(title='理论相关0，方差4和1',xlabel='X',ylabel='Y',xlim=(-7,7),ylim=(-7,7))
    ax.set_aspect('equal');ax.grid(alpha=.15)
    fig.suptitle('声明的联合高斯模拟：种子2026，每组400点；相关不等于轴比',color='#0091a0',fontsize=13)
    fig.savefig(args.output_dir/f'filter_covariance_{suffix}.pdf');plt.close(fig)
print(args.output_dir)
