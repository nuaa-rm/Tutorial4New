#!/usr/bin/env python3
"""重绘深度学习教学矢量图，真实训练曲线只读取运行记录。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

DIAGRAMS = {
'lenet': r'''
\node[box,minimum width=12cm] (a) at (0,6) {本章 LeNet 风格实现：输入 $N\times1\times28\times28$};
\node[box,minimum width=12cm] (b) at (0,4.5) {Conv $1\to6$, $5\times5$ + ReLU：$N\times6\times24\times24$\\MaxPool $2\times2$, stride 2：$N\times6\times12\times12$};
\node[box,minimum width=12cm] (c) at (0,2.7) {Conv $6\to16$, $5\times5$ + ReLU：$N\times16\times8\times8$\\MaxPool $2\times2$, stride 2：$N\times16\times4\times4$};
\node[box,minimum width=12cm] (d) at (0,1) {Flatten：$N\times256$\\Linear $256\to120$ + ReLU $\to84$ + ReLU $\to10$ logits};
\draw[flow] (a)--(b);\draw[flow] (b)--(c);\draw[flow] (c)--(d);
\node[box,minimum width=12cm] at (0,-1) {原图的 32 输入尺寸链：$32\to28\to14\to10\to5$，展平 $16\times5\times5=400$\\原版 LeNet-5 的激活、汇聚及输出形式不同，不能直接替换成本章代码};
''',
'conv': r'''
\node at (-4.5,2) {输入 $X$};\node at (0,2) {核 $W$（不翻转）};\node at (4.5,2) {互相关输出};
\node[box] (a) at (-4.5,0.6) {$\begin{matrix}0&1&2\\3&4&5\\6&7&8\end{matrix}$};
\node[box] (b) at (0,0.6) {$\begin{matrix}0&1\\2&3\end{matrix}$};
\node[box] (c) at (4.5,0.6) {$\begin{matrix}19&25\\37&43\end{matrix}$};
\draw[flow] (a)--(b);\draw[flow] (b)--(c);
\node at (0,-1) {左上输出：$0\cdot0+1\cdot1+3\cdot2+4\cdot3=19$};
\node at (0,-1.7) {单通道、stride 1、padding 0；PyTorch Conv2d 使用互相关约定};
''',
'pool': r'''
\node at (-4.5,2) {输入};\node at (0,2) {最大池化};\node at (4.5,2) {平均池化};
\node[box] (a) at (-4.5,0.6) {$\begin{matrix}0&1&2\\3&4&5\\6&7&8\end{matrix}$};
\node[box] (b) at (0,0.6) {$\begin{matrix}4&5\\7&8\end{matrix}$};
\node[box] (c) at (4.5,0.6) {$\begin{matrix}2&3\\5&6\end{matrix}$};
\draw[flow] (a)--(b);\draw[flow] (a.south)--++(0,-0.5)-|(c.south);
\node at (0,-1) {$2\times2$ 窗口、stride 1；最大与平均分别计算};
\node at (0,-1.7) {两个输出均直接来自左侧输入；stride 改为 2 时只剩左上窗口};
''',
'yolo': r'''
\node[box,minimum width=14cm] (a) at (0,7.5) {历史 YOLOv5s（v1.0）参考：$608\times608\times3$ 输入\\Focus $\to$ Conv/BN/LeakyReLU（CBL）$\to$ BottleneckCSP：$304\to152$};
\node[box] (p3) at (-4.8,5.6) {下采样 + CSP\\P3：$76\times76$};
\node[box] (p4) at (0,5.6) {下采样 + CSP\\P4：$38\times38$};
\node[box] (p5) at (4.8,5.6) {下采样 + SPP + CSP\\P5：$19\times19$};
\draw[flow] (a.south) -- (p3.north);\draw[flow] (p3)--(p4);\draw[flow] (p4)--(p5);
\node[box] (f4) at (0,3.6) {Conv + 上采样 + Concat\\合并 P4 + CSP：$38\times38$};
\node[box] (f3) at (-4.8,1.5) {Conv + 上采样 + Concat\\合并 P3 + CSP：$76\times76$};
\draw[flow] (p5.south) |- (f4.east);\draw[flow] (p4)--(f4);
\draw[flow] (f4.south) |- (f3.east);\draw[flow] (p3)--(f3);
\node[box] (g4) at (0,-0.6) {下采样 + Concat\\合并 f4 + CSP：$38\times38$};
\node[box] (g5) at (4.8,-2.7) {下采样 + Concat\\合并 P5 + CSP：$19\times19$};
\draw[flow] (f3.south) |- (g4.west);\draw[flow] (f4)--(g4);
\draw[flow] (g4.south) |- (g5.west);\draw[flow] (p5.east)--++(1,0)|-(g5.east);
\node[box] (h3) at (-4.8,-4.7) {预测 Conv\\$76\times76\times255$};
\node[box] (h4) at (0,-4.7) {预测 Conv\\$38\times38\times255$};
\node[box] (h5) at (4.8,-4.7) {预测 Conv\\$19\times19\times255$};
\draw[flow] (f3.west)--++(-1,0)|-(h3.west);\draw[flow] (g4)--(h4);\draw[flow] (g5)--(h5);
\node[box,minimum width=14cm] (out) at (0,-6.5) {Detect 解码 $\to$ 分数筛选 $\to$ NMS $\to$ 框/类别/分数\\255 = 3 anchors $\times$ (4 框量 + 1 objectness + 80 classes)};
\draw[flow] (h3.south)--(out.north -| h3.south);\draw[flow] (h4)--(out);\draw[flow] (h5.south)--(out.north -| h5.south);
\node[box,minimum width=14cm] at (0,-8.5) {Focus：按奇偶行列切片后沿通道拼接；CBL：Conv + BN + LeakyReLU\\CSP：分支、瓶颈残差/无残差、Concat 后 Conv；SPP：5/9/13 MaxPool 与原分支 Concat\\这是历史结构示意；最新 YOLO 实现、类别数与输出格式须查所用提交};
'''
}


def diagram(kind, target):
    from render_ch1_diagrams import HEADER
    HEADER = HEADER.replace('\\usepackage[UTF8', '\\usepackage{amsmath}\n\\usepackage[UTF8')
    with tempfile.TemporaryDirectory(prefix='dl-figure-') as temp:
        folder=Path(temp)
        (folder/'figure.tex').write_text(HEADER + DIAGRAMS[kind] + '\n' + chr(92) + 'end{tikzpicture}\n' + chr(92) + 'end{document}\n')
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=folder,check=True,stdout=subprocess.DEVNULL)
        shutil.copy2(folder/'figure.pdf', target)


def plot(kind, target, font_path, metrics):
    import json
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(str(font_path))
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=str(font_path)).get_name(),
        'font.size':14,'pdf.fonttype':3,'axes.unicode_minus':False,
        'axes.spines.top':False,'axes.spines.right':False})
    cyan, gray, orange='#0091a0','#6a7380','#bf6b22'
    fig, axes=plt.subplots(1,3 if kind=='fit' else 2,figsize=(10,4),layout='constrained')
    if kind=='fit':
        x=np.array([-1.,-.5,0.,.5,1.]);y=x*x+np.array([0.,.15,-.2,.15,0.])
        v=np.array([-.75,-.25,.25,.75]);z=v*v;grid=np.linspace(-1,1,201)
        for ax,d in zip(axes,(1,2,4)):
            f=np.polynomial.Polynomial.fit(x,y,d)
            ax.plot(grid,f(grid),color=cyan,label='拟合')
            ax.scatter(x,y,color=orange,marker='x',label='训练点')
            ax.scatter(v,z,color=gray,s=22,label='验证点')
            ax.set_title(f'{d} 阶\n训练 {np.mean((f(x)-y)**2):.4f} / 验证 {np.mean((f(v)-z)**2):.4f}', fontsize=13)
            ax.set(xlabel='x',ylabel='y',ylim=(-.35,1.2))
        axes[0].legend(fontsize=12)
    else:
        data=json.loads(metrics.read_text());history=data['history'];epochs=[r['epoch'] for r in history]
        for ax,key,title in zip(axes,('loss','accuracy'),('交叉熵损失','准确率')):
            for split,color,label in [('train',cyan,'训练'),('valid',orange,'验证')]:
                ax.plot(epochs,[r[split][key] for r in history],marker='o',color=color,label=label)
            ax.set(title=title,xlabel='轮次');ax.set_xticks(epochs);ax.legend()
        fig.suptitle(f"实际 MNIST / CPU / {data['epochs']} 轮 / 最终测试准确率 {data['test']['accuracy']:.4f}",color=cyan)
    for ax in axes:ax.grid(alpha=.15)
    fig.savefig(target);plt.close(fig)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--kind',choices=[*DIAGRAMS,'fit','curve'],required=True)
    cli.add_argument('--output-dir',type=Path,required=True)
    cli.add_argument('--font',type=Path)
    cli.add_argument('--metrics',type=Path)
    cli.add_argument('--publish-checked',action='store_true')
    args=cli.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    target=args.output_dir/f'dl_{args.kind}_{"revised" if args.publish_checked else "candidate"}.pdf'
    if args.kind in DIAGRAMS:diagram(args.kind,target)
    else:
        if not args.font:cli.error('曲线需要 --font')
        if args.kind=='curve' and not args.metrics:cli.error('curve 需要真实 --metrics')
        plot(args.kind,target,args.font,args.metrics)
    print(target)


if __name__=='__main__':main()
