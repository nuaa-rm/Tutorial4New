#!/usr/bin/env python3
"""整理卷三概览图；候选图完成正文检查后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

BODY = r'''
\node[box,minimum width=3.2cm] (sensor) at (0,0) {相机 / 传感器\\图像、量测};
\node[box,minimum width=3.2cm] (state) at (4.3,0) {识别、估计\\定位或融合};
\node[box,minimum width=3.7cm] (aim) at (9,1.7) {自瞄\\目标角与有效性};
\node[box,minimum width=3.7cm] (nav) at (9,0) {导航\\路径与速度};
\node[box,minimum width=3.7cm] (radar) at (9,-1.7) {雷达\\场地坐标与身份};
\draw[flow] (sensor)--(state);
\draw[flow] (state.east)--(aim.west);
\draw[flow] (state)--(nav);
\draw[flow] (state.east)--(radar.west);
\node[align=center] at (4.5,-3) {中间模块随任务选择，不代表共用一个进程\\
每条箭头都要核对：数据含义、单位、坐标系、时间与有效性};
'''
cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument('--output-dir', type=Path, required=True)
cli.add_argument('--publish-checked', action='store_true')
a = cli.parse_args()
a.output_dir.mkdir(parents=True, exist_ok=True)
suffix = 'revised' if a.publish_checked else 'candidate'
with tempfile.TemporaryDirectory(prefix='overview-figure-') as t:
    folder = Path(t)
    (folder/'figure.tex').write_text(HEADER + BODY + '\\end{tikzpicture}\n\\end{document}\n')
    result = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', 'figure.tex'],
                            cwd=folder, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout[-3000:]
    shutil.copy2(folder/'figure.pdf', a.output_dir/f'overview_dataflow_{suffix}.pdf')
print(a.output_dir)
