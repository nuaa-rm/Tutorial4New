#!/usr/bin/env python3
"""核对实际入口的包含路径、标签引用和指定章题解覆盖；不替代内容或视觉验收。"""
import argparse
from collections import Counter
from pathlib import Path
import re

CODE = re.compile(r'\\begin\{(tbash|tcode|tcpp|tpython|lstlisting)\}.*?\\end\{\1\}', re.S)

def searchable(text):
    text = CODE.sub('', text)
    return re.sub(r'(?<!\\)%[^\n]*', '', text)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('volume', type=Path)
    parser.add_argument('--chapter', type=int, default=1)
    args = parser.parse_args()
    root = args.volume.resolve()
    loaded = []
    errors = []
    def expand(file, stack=()):
        file = file.resolve()
        if file in stack:
            errors.append(f'循环包含：{file}')
            return ''
        if not file.exists():
            errors.append(f'缺文件：{file}')
            return ''
        loaded.append(file)
        text = searchable(file.read_text())
        for pattern, extensions in [(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', ['', '.png', '.jpg', '.pdf']),
                                    (r'\\lstinputlisting(?:\[[^\]]*\])?\{([^}]+)\}', [''])]:
            for name in re.findall(pattern, text):
                if name.startswith(chr(92)):
                    # 封面等宏参数由真正的 TeX 编译验证。
                    continue
                if not any((base / (name + ext)).exists() for base in [root, root/'images', root/'figures'] for ext in extensions):
                    errors.append(f'资源不存在：{name}，引用文件：{file}')
        def child(match):
            name = match.group(1)
            path = root / name
            if not path.suffix:
                path = path.with_suffix('.tex')
            return expand(path, stack + (file,))
        return re.sub(r'\\(?:input|include)\{([^}]+)\}', child, text)
    text = expand(root / 'main.tex')
    counts = Counter(re.findall(r'\\label\{([^}]+)\}', text))
    errors += [f'重复标签：{label}' for label, count in counts.items() if count > 1]
    refs = set(re.findall(r'\\(?:ref|pageref|eqref|autoref)\{([^}]+)\}', text))
    errors += [f'未定义引用：{label}' for label in sorted(refs - counts.keys())]
    chapters = re.split(r'\\chapter\{[^}]*\}', text)[1:]
    if args.chapter > len(chapters):
        errors.append('指定章不存在')
    else:
        chapter = chapters[args.chapter-1].split(r'\chapter*')[0]
        answer = (root/'answers.tex').read_text()
        exercises = re.findall(r'\\begin\{exercise\}\s*\\label\{([^}]+)\}', chapter)
        exercise_count = len(re.findall(r'\\begin\{exercise\}', chapter))
        if len(exercises) != exercise_count:
            errors.append('随堂练习存在无标签题目')
        problemsets = re.findall(r'\\begin\{problemset\}(.*?)\\end\{problemset\}', chapter, re.S)
        problems = []
        for problemset in problemsets:
            items = re.split(r'\\item\b', problemset)[1:]
            for item in items:
                labels = re.findall(r'\\label\{([^}]+)\}', item)
                if not labels:
                    errors.append('章末习题存在无标签题目')
                problems += labels
        for label in exercises + problems:
            if r'\ref{'+label+'}' not in answer:
                errors.append(f'题解未引用题目：{label}')
        print(f'第 {args.chapter} 章：{exercise_count} 道随堂练习，{len(problems)} 道章末习题，{len(problemsets)} 个习题集')
    print(f'入口包含 {len(loaded)} 个文件；{len(counts)} 个标签，{len(refs)} 个被引用标签')
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('包含路径、资源存在性、标签唯一性、引用与题解定位检查通过。内容覆盖与运行/PDF 检查须另行记录。')

if __name__ == '__main__':
    main()
