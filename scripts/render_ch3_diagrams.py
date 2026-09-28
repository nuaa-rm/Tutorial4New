#!/usr/bin/env python3
"""重绘第三章的编译阶段与模块查找图；候选图检查后才发布。"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
from render_ch1_diagrams import HEADER

DIAGRAMS = {
    'build-stages': r'''
\node[box,minimum width=6cm] (source) at (0,5) {源文件 hello.cpp 与包含的头文件};
\node[box,minimum width=6cm] (pre) at (0,3) {预处理：展开包含、宏和条件编译\\hello.ii（预处理后的文本）};
\node[box,minimum width=6cm] (compile) at (0,1) {编译：检查语法与语义，生成汇编\\hello.s（汇编代码）};
\node[box,minimum width=6cm] (assemble) at (0,-1) {汇编：生成可重定位目标文件\\hello.o（机器代码、符号、重定位信息）};
\node[box,minimum width=6cm] (link) at (0,-3) {链接：解析符号、处理重定位\\hello（可执行文件）};
\node[box,minimum width=2.7cm] (library) at (-5,-3) {其他目标文件\\静态库 / 共享库};
\draw[flow] (source) -- node[right]{g++ -E} (pre);
\draw[flow] (pre) -- node[right]{g++ -S} (compile);
\draw[flow] (compile) -- node[right]{g++ -c} (assemble);
\draw[flow] (assemble) -- node[right]{g++（完成链接）} (link);
\draw[flow] (library) -- (link);
\node at (0,-4.2) {箭头只标出阶段选择；完整的输入与输出命令见正文};
''',
    'cmake-module': r'''
\node[box,minimum width=10cm] (entry) at (0,3.6) {armor-demo/CMakeLists.txt\\将 cmake/ 加入 CMAKE\_MODULE\_PATH};
\node[box,minimum width=10cm] (include) at (0,1.8) {include(Function)\\查找并载入 cmake/Function.cmake};
\node[box,minimum width=10cm] (function) at (0,0) {Function.cmake 定义 print\_var(var)\\检查变量是否已定义，再打印变量名与值};
\node[box,minimum width=10cm] (call) at (0,-1.8) {返回 CMakeLists.txt，调用 print\_var(...)\\配置日志：编译器路径、Debug、未定义变量提示};
\draw[flow] (entry) -- (include);
\draw[flow] (include) -- (function);
\draw[flow] (function) -- (call);
\node at (0,-3) {这些语句在 CMake 配置阶段执行，不是在 C++ 程序运行时执行};
''',
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--publish-checked', action='store_true')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ch3-diagrams-') as folder:
        build = Path(folder)
        for name, body in DIAGRAMS.items():
            source = build / (name + '.tex')
            source.write_text(HEADER + body + '\n\\end{tikzpicture}\n\\end{document}\n')
            subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', source.name],
                           cwd=build, check=True, stdout=subprocess.DEVNULL)
            target = args.output_dir / (name + ('_revised' if args.publish_checked else '_candidate') + '.pdf')
            shutil.copy2(source.with_suffix('.pdf'), target)
            print(target)

if __name__ == '__main__':
    main()
