#!/usr/bin/env python3
"""重绘 ROS2 分层与通信关系图；实际检查候选图后再发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS = {
    'ros2_arch': r'''
\node[box,minimum width=11cm] (app) at (0,5) {机器人应用：相机采集、识别、决策等节点};
\node[box,minimum width=5cm] (cpp) at (-3,3.2) {rclcpp：C++ 客户端库\\本章使用的接口与执行器};
\node[box,minimum width=5cm] (py) at (3,3.2) {rclpy：Python 客户端库\\其他语言也可有客户端库};
\node[box,minimum width=11cm] (rcl) at (0,1.4) {rcl：公共客户端基础\\名称、时间、服务等基础机制};
\node[box,minimum width=11cm] (rmw) at (0,-0.4) {rmw：中间件接口\\发布 / 订阅、QoS、发现与通信图事件};
\node[box,minimum width=3.4cm] (fast) at (-3.8,-2.2) {Fast DDS\\\texttt{rmw\_fastrtps\_cpp}};
\node[box,minimum width=3.4cm] (cyclone) at (0,-2.2) {Cyclone DDS\\\texttt{rmw\_cyclonedds\_cpp}};
\node[box,minimum width=3.4cm] (zenoh) at (3.8,-2.2) {Zenoh\\\texttt{rmw\_zenoh\_cpp}};
\draw[flow] (app.south) -- (cpp.north);
\draw[flow] (app.south) -- (py.north);
\draw[flow] (cpp.south) -- (rcl.north);
\draw[flow] (py.south) -- (rcl.north);
\draw[flow] (rcl) -- (rmw);
\draw[flow] (rmw.south) -- (fast.north);
\draw[flow] (rmw.south) -- (cyclone.north);
\draw[flow] (rmw.south) -- (zenoh.north);
\node[align=center] at (0,-3.5) {图中列出本章比较的中间件；ROS2 还支持其他实现\\Fast DDS 与 Cyclone DDS 基于 DDS；Zenoh 不属于 DDS 实现};
''',
    'ros2_node': r'''
\node[box,minimum width=3.4cm,minimum height=2.6cm] (camera) at (-4.6,2.8) {节点 A\\图像发布者\\参数服务端};
\node[box,minimum width=3.4cm,minimum height=2.6cm] (detect) at (4.6,2.8) {节点 B\\图像订阅者\\参数服务客户端};
\node[box,minimum width=3.4cm] (topic) at (0,3.7) {话题 /image\\连续的图像消息};
\node[box,minimum width=3.4cm] (request) at (0,1.9) {服务：查询参数\\请求 / 响应};
\node[box,minimum width=3.4cm] (record) at (4.6,6) {节点 C\\图像订阅者 / 记录};
\draw[flow] ([yshift=8mm]camera.east) -- (topic.west);
\draw[flow] (topic.east) -- ([yshift=8mm]detect.west);
\draw[flow] (topic.north) -- (0,5) -- (4.6,5) -- (record.south);
\draw[flow] ([yshift=-5mm]detect.west) -- node[below]{请求} (request.east);
\draw[flow] (request.west) -- ([yshift=-5mm]camera.east);
\draw[flow] ([yshift=-10mm]camera.east) -- (-2.7,0.6) -- node[below]{响应返回客户端} (2.7,0.6) -- ([yshift=-10mm]detect.west);
\node at (0,-1.8) {话题可以连接多个订阅者；服务是一次请求对应一次响应};
\node at (0,-2.5) {回调由执行器调度；节点是否装入组件容器是另一个维度};
''',
}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--publish-checked',action='store_true')
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ros-diagrams-') as folder:
        build=Path(folder)
        for name,body in DIAGRAMS.items():
            source=build/(name+'.tex')
            source.write_text(HEADER+body+'\n\\end{tikzpicture}\n\\end{document}\n')
            subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',source.name],cwd=build,check=True,stdout=subprocess.DEVNULL)
            target=args.output_dir/(name+('_revised' if args.publish_checked else '_candidate')+'.pdf')
            shutil.copy2(source.with_suffix('.pdf'),target)
            print(target)

if __name__=='__main__':main()
