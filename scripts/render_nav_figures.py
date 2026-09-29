#!/usr/bin/env python3
"""重绘导航概念图；候选图完成独立和正文视觉检查后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS={
'framework':r'''
\node[box,minimum width=5cm] (goal) at (0,5) {任务目标与定位输入};
\node[box,minimum width=5cm] (bt) at (0,3.3) {BT Navigator：组织导航任务\\NavigateToPose 等 action};
\draw[flow] (goal)--(bt);
\node[box,minimum width=4cm] (plan) at (-5,1.2) {Planner Server\\ComputePathToPose：生成路径};
\node[box,minimum width=4cm] (control) at (0,1.2) {Controller Server\\FollowPath：跟踪路径};
\node[box,minimum width=4cm] (behavior) at (5,1.2) {Behavior Server\\旋转、等待、后退等行为};
\draw[flow] (bt.south west)--(plan.north);
\draw[flow] (bt.south)--(control.north);
\draw[flow] (bt.south east)--(behavior.north);
\node[box,minimum width=4cm] (global) at (-5,-.5) {全局代价地图\\地图＋障碍＋膨胀等};
\node[box,minimum width=4cm] (local) at (0,-.5) {局部代价地图\\附近环境与车体外形};
\draw[flow] (global)--(plan);\draw[flow] (local)--(control);
\node[box,minimum width=4cm] (tf) at (5,-.5) {定位 / TF / 里程计\\提供带时间的坐标关系};
\node[box,minimum width=14cm] (inputs) at (0,-2.1) {地图与传感器观测支撑环境表达；TF 支撑规划、控制与环境转换};
\draw[flow] (inputs.north west)--(global.south west);
\draw[flow] (inputs.north)--(local.south);
\node[box,minimum width=14cm] at (0,-3.5) {控制与行为输出速度 → 执行接口 → 底盘运动 → 新观测\\
本章直接调用规划/控制 action；软件积分替代真实底盘};
\node at (0,-4.7) {实线表示核心关系；还有平滑、航点等服务器，按版本与任务选择};
''',
'frames':r'''
\node[box,minimum width=4.8cm] (map) at (0,4.5) {map：全局参考\\允许定位修正引起跳变};
\node[box,minimum width=4.8cm] (odom) at (0,2) {odom：局部参考\\连续、平滑，但长期可漂移};
\node[box,minimum width=4.8cm] (base) at (0,-.5) {base\_link：固连车体};
\draw[flow] (map)--node[right,align=left]{全局定位发布\\map→odom}(odom);
\draw[flow] (odom)--node[right,align=left]{里程计发布\\odom→base\_link}(base);
\node[box,minimum width=3.3cm] (laser) at (-4,-3) {laser\_link};
\node[box,minimum width=3.3cm] (camera) at (0,-3) {camera\_link};
\node[box,minimum width=3.3cm] (imu) at (4,-3) {imu\_link};
\draw[flow] (base.south)--(-4,-1.7)--(laser.north);
\draw[flow] (base.south)--(camera.north);
\draw[flow] (base.south)--(4,-1.7)--(imu.north);
\node[align=center] at (0,-4.2) {固定安装外参由静态 TF / robot\_state\_publisher 等提供\\
单一子坐标系只能有一个父坐标系；动态查询还要满足时间范围};
''',
'slam':r'''
\node[box,minimum width=3cm] (sensor) at (-5,1.5) {传感器输入\\图像、IMU 等};
\node[box,minimum width=3cm] (front) at (0,1.5) {前端 / 视觉里程计\\估计相邻运动};
\node[box,minimum width=3cm] (back) at (5,1.5) {后端优化\\轨迹与路标一致性};
\draw[flow] (sensor)--(front);\draw[flow] (front)--(back);
\node[box,minimum width=4cm] (loop) at (0,-.8) {回环检测（若有）\\认出曾经到过的位置};
\draw[flow] (front)--(loop);\draw[flow] (loop.east)-|(back.south);
\node[box,minimum width=4cm] (mapping) at (5,-2.5) {建图输出\\地图与可用位姿};
\draw[flow] (back.east)--++(1.1,0)|-(mapping.east);
\node[align=center] at (-3,-2.5) {前端、后端和地图会互相提供数据\\这是概念流程，不是特定节点接口图};
\node at (0,-4) {里程计未必有全局回环；真实系统还要处理时间、外参、退化与尺度};
'''
}
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--output-dir',type=Path,required=True)
cli.add_argument('--publish-checked',action='store_true')
args=cli.parse_args();suffix='revised' if args.publish_checked else 'candidate'
args.output_dir.mkdir(parents=True,exist_ok=True)
for kind,body in DIAGRAMS.items():
 with tempfile.TemporaryDirectory(prefix='nav-figure-') as t:
  folder=Path(t);(folder/'figure.tex').write_text(HEADER+body+'\n'+chr(92)+'end{tikzpicture}\n'+chr(92)+'end{document}\n')
  result=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','figure.tex'],cwd=folder,capture_output=True,text=True)
  assert result.returncode==0,result.stdout[-3000:]
  shutil.copy2(folder/'figure.pdf',args.output_dir/f'nav_{kind}_{suffix}.pdf')
print(args.output_dir)
