#!/usr/bin/env python3
"""据本次实验结果画基线、失败和回滚；实际查看后发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--output-dir',type=Path,required=True);c.add_argument('--publish-checked',action='store_true');a=c.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True);suffix='revised' if a.publish_checked else 'candidate'
body=r'''
\node[box,text width=31mm] (base) at (0,0) {基线：限龄100 ms\\视觉年龄50 ms\\满足任务判据};
\node[box,text width=33mm] (trial) at (4.6,0) {只改限龄到200 ms\\无线电年龄150 ms\\违反100 ms判据};
\node[box,text width=31mm] (back) at (9.2,0) {回滚：限龄100 ms\\视觉年龄50 ms\\与基线记录一致};
\draw[flow] (base)--(trial);\draw[flow] (trial)--(back);
\node[align=center,font=\small] at (4.6,-1.7) {输入、程序与任务判据保持一致；三份记录都保留\\
人工消息的软件实验，真实同学复核与现场表现仍待验证};
'''
with tempfile.TemporaryDirectory(prefix='engineering-figure-') as t:
 p=Path(t);(p/'figure.tex').write_text(HEADER+body+'\\end{tikzpicture}\n\\end{document}\n');r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=p,capture_output=True,text=True);assert r.returncode==0,r.stdout[-3000:];shutil.copy2(p/'figure.pdf',a.output_dir/f'engineering_trial_{suffix}.pdf')
print(a.output_dir)
