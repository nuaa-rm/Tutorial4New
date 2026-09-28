#!/usr/bin/env python3
"""在工程副本验证第三章的构建、变体与 OpenCV 窗口；不改教材原文件。"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

PROJECT = Path(__file__).resolve().parents[1] / '01-基础通识/examples/build-pipeline-demo'

def gui_worker(binary, sample, screenshot):
    env = os.environ.copy()
    env.pop('WAYLAND_DISPLAY', None)
    env['QT_QPA_PLATFORM'] = 'xcb'
    process = subprocess.Popen([binary, sample], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, env=env)
    try:
        window = ''
        for _ in range(50):
            found = subprocess.run(['xdotool', 'search', '--onlyvisible', '--name', '^Armor image$'],
                                   capture_output=True, text=True)
            if found.returncode == 0:
                window = found.stdout.splitlines()[0]
                break
            if process.poll() is not None:
                break
            time.sleep(0.1)
        assert window, '没有找到图像窗口'
        time.sleep(0.3)
        subprocess.run(['xwd', '-silent', '-id', window, '-out', screenshot], check=True)
        # 只发按下事件；程序在 waitKey 返回后关闭窗口，继续发抬起事件会碰到已销毁的窗口。
        subprocess.run(['xdotool', 'keydown', '--window', window, 'space'], check=True)
        out, err = process.communicate(timeout=5)
        print(out, end='')
        print(err, end='', file=sys.stderr)
        assert process.returncode == 0, process.returncode
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--screenshot', type=Path, required=True)
    args = ap.parse_args()
    args.output = args.output.resolve()
    args.screenshot = args.screenshot.resolve()
    records = []
    def run(name, command, cwd, expect=0, contains=()):
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=45)
        records.append({'step': name, 'command': command, 'exit': result.returncode,
                        'stdout': result.stdout, 'stderr': result.stderr})
        assert (result.returncode == 0 if expect == 0 else result.returncode != 0), records[-1]
        for value in contains:
            assert value in result.stdout + result.stderr, (name, value, records[-1])
        return result
    with tempfile.TemporaryDirectory(prefix='build-chapter-check-') as folder:
        work = Path(folder) / 'lab'
        shutil.copytree(PROJECT, work)
        stages = work / 'stages'
        for phase, command in [('preprocess', ['g++', '-std=c++17', '-E', 'hello.cpp', '-o', 'hello.ii']),
                               ('compile', ['g++', '-std=c++17', '-S', 'hello.ii', '-o', 'hello.s']),
                               ('assemble', ['g++', '-c', 'hello.s', '-o', 'hello.o']),
                               ('link', ['g++', 'hello.o', '-o', 'hello'])]:
            run(phase, command, stages)
        assert 'ARMOR_ID' not in (stages/'hello.ii').read_text()
        run('four-stage-output', ['./hello'], stages, contains=('armor=3', 'function=main'))
        original = (stages/'hello.cpp').read_text()
        (stages/'hello.cpp').write_text(original.replace('ARMOR_ID 3', 'ARMOR_ID 7'))
        run('old-binary', ['./hello'], stages, contains=('armor=3',))
        run('one-step', ['g++', '-std=c++17', '-Wall', '-Wextra', 'hello.cpp', '-o', 'hello'], stages)
        run('new-binary', ['./hello'], stages, contains=('armor=7',))
        (stages/'hello.cpp').write_text(original.replace("<< '\\n';", "<< '\\n'", 1))
        run('syntax-error', ['g++', '-std=c++17', '-S', 'hello.cpp', '-o', 'bad.s'], stages,
            expect=1, contains=('expected',))
        def configure_build(directory, build='build', options=()):
            run('configure-'+build, ['cmake', '-S', '.', '-B', build, '-DCMAKE_BUILD_TYPE=Debug', *options], directory)
            return run('build-'+build, ['cmake', '--build', build, '--parallel', '2'], directory)
        hello = work/'hello-cmake'
        configure_build(hello)
        run('cmake-hello', ['./build/hello'], hello, contains=('armor=3',))
        p = hello/'CMakeLists.txt'
        p.write_text(p.read_text().replace('(hello ', '(armor_hello '))
        configure_build(hello, 'build-rename')
        run('renamed-target', ['./build-rename/armor_hello'], hello, contains=('armor=3',))
        armor = work/'armor-demo'
        run('manual-multifile', ['g++','-std=c++17','-I','include','src/main.cpp','src/armor.cpp','-o','armor_manual'], armor)
        run('manual-score', ['./armor_manual'], armor, contains=('score=30',))
        run('missing-header', ['g++','-std=c++17','src/main.cpp','src/armor.cpp','-o','bad'], armor, expect=1, contains=('armor.hpp',))
        run('missing-implementation', ['g++','-std=c++17','-I','include','src/main.cpp','-o','bad'], armor, expect=1, contains=('undefined reference',))
        final = (armor/'CMakeLists.txt').read_text()
        (armor/'CMakeLists.txt').write_text((armor/'cmake/Multifile.cmake').read_text())
        configure_build(armor)
        run('multifile', ['./build/armor_demo'], armor, contains=('score=30',))
        configure_build(armor, options=('-DSAVE_OUTPUT=ON',))
        run('macro-on', ['./build/armor_demo'], armor, contains=('score=30','save output enabled'))
        source = armor/'src/armor.cpp'
        original = source.read_text()
        source.write_text(original.replace('id * 10', 'id * 20'))
        run('incremental-multifile', ['cmake','--build','build','--parallel','2'], armor)
        run('double-score', ['./build/armor_demo'], armor, contains=('score=60',))
        configure_build(armor, options=('-DSAVE_OUTPUT=OFF',))
        assert run('macro-off', ['./build/armor_demo'], armor).stdout.strip() == 'score=60'
        source.write_text(original)
        (armor/'CMakeLists.txt').write_text((armor/'cmake/Static.cmake').read_text())
        configure_build(armor, 'build-lib')
        assert (armor/'build-lib/libarmor.a').exists()
        run('static-library', ['./build-lib/armor_demo'], armor, contains=('score=30',))
        unchanged = run('unchanged-build', ['cmake','--build','build-lib','--verbose'], armor).stdout
        assert 'Building CXX object' not in unchanged
        time.sleep(1)
        source.write_text(original.replace('id * 10','id * 20'))
        changed = run('changed-library', ['cmake','--build','build-lib','--verbose'], armor).stdout
        assert 'Building CXX object CMakeFiles/armor.dir/src/armor.cpp.o' in changed
        assert 'Building CXX object CMakeFiles/armor_demo.dir/src/main.cpp.o' not in changed
        run('changed-score', ['./build-lib/armor_demo'], armor, contains=('score=60',))
        source.write_text(original)
        static = (armor/'CMakeLists.txt').read_text()
        (armor/'CMakeLists.txt').write_text(static.replace('armor STATIC','armor SHARED'))
        configure_build(armor, 'build-shared')
        assert (armor/'build-shared/libarmor.so').exists()
        run('shared-library', ['./build-shared/armor_demo'], armor, contains=('score=30',))
        (armor/'CMakeLists.txt').write_text(final)
        configured = run('module-log', ['cmake','-S','.','-B','build-final','-DCMAKE_BUILD_TYPE=Debug'], armor,
                         contains=('CMAKE_BUILD_TYPE = [Debug]','NOT_DEFINED_YET is not defined'))
        run('final-build', ['cmake','--build','build-final','--parallel','2'], armor)
        for prefix in ['stage', 'stage-check']:
            run('install-'+prefix, ['cmake','--install','build-final','--prefix',str(armor/prefix)], armor)
            run('installed-'+prefix, ['./'+prefix+'/bin/armor_demo'], armor, contains=('score=30',))
        (armor/'CMakeLists.txt').write_text(final.replace('armor PUBLIC','armor PRIVATE'))
        run('scope-configure', ['cmake','-S','.','-B','build-private'], armor)
        run('scope-header-failure', ['cmake','--build','build-private','--parallel','2'], armor, expect=1, contains=('armor.hpp',))
        (armor/'CMakeLists.txt').write_text(final+'\nset(EMPTY_VALUE "")\nprint_var(EMPTY_VALUE)\n')
        run('empty-variable', ['cmake','-S','.','-B','build-empty'], armor,
            contains=('EMPTY_VALUE = []','NOT_DEFINED_YET is not defined'))
        cv = work/'opencv-demo'
        cv_config = cv/'CMakeLists.txt'
        good_config = cv_config.read_text()
        cv_config.write_text(good_config.replace('find_package(OpenCV REQUIRED)',
                                                'find_package(RMTrainingMissingPackage REQUIRED)'))
        run('missing-package', ['cmake','-S','.','-B','build-missing'], cv, expect=1,
            contains=('RMTrainingMissingPackage', 'Configuring incomplete'))
        cv_config.write_text(good_config)
        run('restore-package', ['cmake','-S','.','-B','build-missing'], cv)
        configure_build(cv)
        for name, command, code in [('no-argument',['./build/image_viewer'],1),
                                    ('missing-image',['./build/image_viewer','missing.png'],2)]:
            result = run(name, command, cv, expect=1)
            assert result.returncode == code
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
        def window(sample, screenshot, size):
            run('opencv-window-'+size, ['xvfb-run','-a','-s','-screen 0 800x600x24',
                sys.executable, str(Path(__file__).resolve()), '--gui-worker',
                str(cv/'build/image_viewer'), str(sample), str(screenshot)], cv,
                contains=('size='+size,))
        window(cv/'test.ppm', args.screenshot.with_name('opencv-two-pixels.xwd'), '2x2')
        large = cv/'large.ppm'
        with large.open('w') as output:
            output.write('P3\n320 240\n255\n')
            for y in range(240):
                for x in range(320):
                    output.write(('255 0 0' if x<160 else '0 255 0')+'\n' if y<120
                                 else ('0 0 255' if x<160 else '255 255 255')+'\n')
        window(large, args.screenshot, '320x240')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    versions = {name: subprocess.run(command, capture_output=True, text=True).stdout.strip().splitlines()[0]
                for name, command in [('gcc',['g++','--version']),('cmake',['cmake','--version']),
                                      ('opencv',['pkg-config','--modversion','opencv4'])]}
    args.output.write_text(json.dumps({'versions':versions,'records':records},ensure_ascii=False,indent=2)+'\n')
    print(f'{len(records)} 次命令符合预期；日志：{args.output}')

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--gui-worker':
        gui_worker(*sys.argv[2:])
    else:
        main()
