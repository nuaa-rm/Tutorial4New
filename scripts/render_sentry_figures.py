#!/usr/bin/env python3
"""卷三复用已整理框架图，并绘制纸面开放/封路情景；检查后发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

ROOT = Path(__file__).resolve().parents[1]
c = argparse.ArgumentParser(description=__doc__)
c.add_argument('--output-dir', type=Path, required=True)
c.add_argument('--publish-checked', action='store_true')
a = c.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)
suffix = 'revised' if a.publish_checked else 'candidate'
shutil.copy2(ROOT/'02-专项技术栈/images/nav_framework_revised.pdf',
             a.output_dir/f'sentry_framework_{suffix}.pdf')
body = r'''
\foreach \shift/\name in {0/{先走到上方通道},8/{新障碍封住唯一通道}} {
 \begin{scope}[xshift=\shift cm]
  \draw[step=1,draw=teachingcyan!50] (0,0) grid (6,6);
  \fill[teachingcyan!55] (3,0) rectangle (4,5);
  \node at (3,6.7) {\name};
  \foreach \v in {0,...,5} {
   \node[font=\footnotesize] at (\v+.5,-.4) {\v};
   \node[font=\footnotesize] at (-.4,\v+.5) {\v};
  }
  \node[box,minimum height=6mm] at (.5,.5) {起};
  \node[box,minimum height=6mm] at (5.5,5.5) {终};
  \draw[flow] (.5,1)--(.5,5.5)--(5,5.5);
 \end{scope}
}
\fill[red!50] (11,5) rectangle (12,6);
\node[align=center] at (7,-1.6) {格号用于纸面演练，不是实际地图米坐标；浅红格为新增障碍\\
旧路线仍能画出来，但封路后不能把它继续当可执行路线};
'''
with tempfile.TemporaryDirectory(prefix='sentry-figure-') as t:
 p=Path(t);(p/'figure.tex').write_text(HEADER+body+'\\end{tikzpicture}\n\\end{document}\n')
 r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=p,capture_output=True,text=True);assert r.returncode==0,r.stdout[-3000:]
 shutil.copy2(p/'figure.pdf',a.output_dir/f'sentry_grid_{suffix}.pdf')
print(a.output_dir)
