#!/usr/bin/env python3
"""雷达站数据流与理想高度偏差；正文实际检查后发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

c = argparse.ArgumentParser(description=__doc__)
c.add_argument('--output-dir', type=Path, required=True)
c.add_argument('--publish-checked', action='store_true')
a = c.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)
suffix = 'revised' if a.publish_checked else 'candidate'
figures = {
'radar_chain': r'''
\node[box,text width=29mm] (vision) at (0,1.4) {相机检测与映射\\场地坐标};
\node[box,dashed,text width=29mm] (radio) at (0,-.8) {可选无线电解析\\场地坐标};
\node[box,text width=30mm] (choice) at (4.3,.3) {先查身份、坐标\\质量与观测年龄\\再按策略选源};
\node[box,text width=29mm] (send) at (8.6,.3) {按适用协议广播\\有效坐标或失效};
\draw[flow] (vision.east)--(choice.west);
\draw[flow,dashed] (radio.east)--(choice.west);
\draw[flow] (choice)--(send);
\node[box,dashed,text width=30mm] (event) at (0,-3) {可选计数／任务事件};
\node[box,text width=30mm] (order) at (4.3,-3) {独立有序处理\\按协议确认／去重};
\draw[flow,dashed] (event)--(order);
\node[align=left,font=\footnotesize,text width=35mm] at (8.6,-3) {事件不能被最新坐标覆盖；\\可选源退出后主路仍能回退};
''',
'radar_plane': r'''
\draw[flow] (0,0)--(7,0) node[right] {地面 $x$（m）};
\draw[flow] (0,0)--(0,5.8) node[above] {高度 $z$（m）};
\coordinate (C) at (2,5);\coordinate (P) at (3,1);\coordinate (Q) at (3.25,0);
\draw[thick,teachingcyan] (C)--(Q);
\draw[dashed,teachingcyan] (P)--(3,0);
\fill[teachingcyan] (C) circle(2pt) node[above right] {相机 $(2,5)$};
\fill[teachingcyan] (P) circle(2pt) node[right] {高处点 $(3,1)$};
\fill[teachingcyan] (3,0) circle(2pt);
\fill[red!70!black] (Q) circle(2pt);
\draw[flow] (3,-.5)--(3.25,-.5);
\node[align=left] at (5.2,-1.2) {真实地面投影 $x=3$\\沿同一视线落地 $x=3.25$};
\node[align=left,font=\footnotesize,text width=45mm] at (5.7,3.9) {教学相机的 $x$--$z$ 截面；\\高处点与地面点像素不同，\\地面单应只知道射线落地位置。};
'''}
for name, body in figures.items():
 with tempfile.TemporaryDirectory(prefix='radar-figure-') as t:
  p=Path(t); (p/'figure.tex').write_text(HEADER+body+'\\end{tikzpicture}\n\\end{document}\n')
  r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=p,capture_output=True,text=True)
  assert r.returncode==0,r.stdout[-3000:]
  shutil.copy2(p/'figure.pdf',a.output_dir/f'{name}_{suffix}.pdf')
print(a.output_dir)
