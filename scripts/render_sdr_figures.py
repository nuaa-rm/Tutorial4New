#!/usr/bin/env python3
"""生成 SDR 流程图与真实离线计算曲线，候选图实际查看后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def chain(target):
    from render_ch1_diagrams import HEADER
    body = r'''
\node[box,minimum width=11cm] (hw) at (0,5) {硬件采集：天线 $\rightarrow$ 射频滤波/下变频 $\rightarrow$ ADC\\采样前的滤波损失、饱和与接线问题不能靠回放补回};
\node[box,minimum width=11cm] (iq) at (0,3.4) {IQ：$I+jQ$ 复数样本 $+$ 采样与调谐元数据\\实机 RX 或合成文件从这里进入数字处理};
\node[box,minimum width=11cm] (sync) at (0,1.8) {数字接收：补偿已知频偏 $\rightarrow$ 前导相关 $\rightarrow$ 相位补偿\\起点与相位参考先确定，本例频偏/符号率不做盲估计};
\node[box,minimum width=11cm] (frame) at (0,0.2) {符号求均值 $\rightarrow$ 正负判决 $\rightarrow$ 比特/字节 $\rightarrow$ CRC/命令\\失败则拒收；成功才交付米值坐标与序号};
\node[box,minimum width=11cm] (upper) at (0,-1.4) {上层使用：坐标系、时间、来源与新鲜度 $\rightarrow$ 通信/融合\\CRC 不替代身份、时效或坐标系检查};
\draw[flow] (hw)--(iq);\draw[flow] (iq)--(sync);\draw[flow] (sync)--(frame);\draw[flow] (frame)--(upper);
'''
    with tempfile.TemporaryDirectory(prefix='sdr-figure-') as temp:
        folder=Path(temp)
        (folder/'figure.tex').write_text(HEADER+body+'\n\\end{tikzpicture}\n\\end{document}\n')
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=folder,check=True,stdout=subprocess.DEVNULL)
        shutil.copy2(folder/'figure.pdf',target)


def replay(target, font_path):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(str(font_path))
    font=font_manager.FontProperties(fname=str(font_path)).get_name()
    plt.rcParams.update({'font.family':font,'font.size':11,'axes.unicode_minus':False,
                         'pdf.fonttype':3,'axes.spines.top':False,'axes.spines.right':False})
    sys.path.insert(0,str(ROOT/'02-专项技术栈/examples/sdr/iq-replay-demo'))
    from synth import synthesize
    from decode import decode
    iq,metadata=synthesize()
    _,details=decode(iq,metadata)
    assert details['start']==19
    fig,axes=plt.subplots(3,1,figsize=(8.8,7.5),layout='constrained')
    cyan='#0091a0';gray='#6a7380'
    n=np.arange(180)
    axes[0].plot(n,iq[:180].real,color=cyan,lw=1.2,label='I（实部）')
    axes[0].plot(n,iq[:180].imag,color=gray,lw=1,label='Q（虚部）')
    axes[0].axvline(19,color='#bf6b22',ls='--',lw=1)
    axes[0].set(title='① 原始 IQ：频偏和相位使 I/Q 持续旋转',xlabel='样本下标',ylabel='幅值（归一化）')
    axes[0].legend(loc='upper right',ncol=2)
    correlation=abs(details['correlation'])/128
    # 图和代码一样，仅显示能够容纳完整帧的候选起点。
    candidates=len(iq)-640+1
    axes[1].plot(np.arange(candidates),correlation[:candidates],color=cyan,marker='.',lw=1.3)
    axes[1].axvline(19,color='#bf6b22',ls='--',lw=1,label='最大值起点 19')
    axes[1].set(title='② 补偿已知频偏后：前导相关峰',xlabel='候选帧起点（样本下标）',ylabel='相关模 / 128')
    axes[1].legend(loc='upper right')
    means=details['means'].real
    markers,_,_=axes[2].stem(np.arange(len(means)),means,linefmt=cyan,markerfmt='.',basefmt=' ')
    markers.set_color(cyan)
    axes[2].axhline(0,color=gray,lw=1)
    axes[2].axvspan(-.5,15.5,color=cyan,alpha=.1,label='16 比特前导')
    axes[2].set(title='③ 对齐并补偿相位后：每符号 8 样本的实部均值',xlabel='符号下标（0–15 前导，16–79 帧）',ylabel='符号均值')
    axes[2].legend(loc='upper right')
    for ax in axes:ax.grid(alpha=.16)
    fig.savefig(target)
    plt.close(fig)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--kind',choices=['chain','replay'],required=True)
    cli.add_argument('--output-dir',type=Path,required=True)
    cli.add_argument('--font',type=Path)
    cli.add_argument('--publish-checked',action='store_true')
    args=cli.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    target=args.output_dir/f'sdr_{args.kind}_{"revised" if args.publish_checked else "candidate"}.pdf'
    if args.kind=='chain':chain(target)
    else:
        if not args.font or not args.font.exists():cli.error('replay 需要可读取的中文 --font 路径')
        replay(target,args.font)
    print(target)


if __name__=='__main__':main()
