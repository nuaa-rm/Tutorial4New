#!/usr/bin/env python3
"""自瞄链路与时间线，检查候选图及正文后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER
DIAGRAMS = {
'chain': r'''
\node[box,minimum width=4cm] (detect) at (0,0) {检测与空间解算\\像素点 → 相机系位置};
\node[box,minimum width=4cm] (track) at (5.3,0) {跟踪与预测\\状态 → 预计命中位置};
\node[box,minimum width=4cm] (control) at (10.6,0) {弹道与云台控制\\目标角 → 执行反馈};
\draw[flow] (detect)--(track);\draw[flow] (track)--(control);
\node[align=center] at (5.3,-1.4) {共同核对：目标身份、坐标系、时间戳与有效性\\
开火还要检查任务允许、状态质量与实际执行条件};
''',
'time': r'''
\draw[flow] (0,0)--(13,0);
\foreach \x/\label in {0/{采样 10 ms},4/{控制生效 45 ms},12/{预计命中 110 ms}} {
 \draw[thick,draw=teachingcyan] (\x,-.15)--(\x,.15);
 \node[above] at (\x,.3) {\label};
}
\draw[flow] (0,-1)--node[below]{35 ms：采样到控制}(4,-1);
\draw[flow] (4,-1)--node[below]{65 ms：教学飞行时间}(12,-1);
\draw[flow] (0,-2.3)--node[below]{状态仍在采样时刻：预测 100 ms}(12,-2.3);
\node at (6,-3.6) {状态已外推到 45 ms：从该时刻再预测 65 ms，不能重复加 35 ms};
'''
}
c=argparse.ArgumentParser(description=__doc__);c.add_argument('--output-dir',type=Path,required=True);c.add_argument('--publish-checked',action='store_true');a=c.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
for name,body in DIAGRAMS.items():
 with tempfile.TemporaryDirectory(prefix='aim-figure-') as t:
  p=Path(t);(p/'figure.tex').write_text(HEADER+body+'\\end{tikzpicture}\n\\end{document}\n')
  r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=p,capture_output=True,text=True);assert r.returncode==0,r.stdout[-3000:]
  suffix='revised' if a.publish_checked else 'candidate';shutil.copy2(p/'figure.pdf',a.output_dir/f'aim_{name}_{suffix}.pdf')
print(a.output_dir)
