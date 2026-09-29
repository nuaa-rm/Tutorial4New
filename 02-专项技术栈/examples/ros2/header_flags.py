"""从一个源码的编译命令生成指定外部头文件的 clangd 配置片段。"""
import argparse
import json
from pathlib import Path
import re
import shlex

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("database", type=Path)
parser.add_argument("source", type=Path)
parser.add_argument("headers", type=Path, nargs="+")
args = parser.parse_args()
entries = json.loads(args.database.read_text())
matches = [e for e in entries if
           (Path(e["directory"]) / e["file"]).resolve()
           == args.source.resolve()]
if len(matches) != 1:
    parser.error("源码必须唯一对应一条编译命令，请核对路径和数据库")
entry = matches[0]
words = iter(entry.get("arguments") or shlex.split(entry["command"]))
next(words)  # 跳过编译器；这里只读取参数，不执行命令。
flags = []
for word in words:
    prefix = next((p for p in ("-isystem", "-iquote", "-I")
                   if word.startswith(p)), None)
    if prefix:
        value = word[len(prefix):] or next(words, None)
        if not value:
            parser.error("头文件路径参数缺少对应路径")
        path = (Path(entry["directory"]) / value).resolve()
        flags.extend([prefix, str(path)])
    elif word in ("-D", "-U"):
        value = next(words, None)
        if not value:
            parser.error("宏参数缺少对应内容")
        flags.extend([word, value])
    elif word.startswith(("-D", "-U", "-std=")):
        flags.append(word)
config = {
    "If": {"PathMatch": [re.escape(str(h.resolve()))
                         for h in args.headers]},
    "CompileFlags": {"Add": flags},
}
# JSON 也是合法的 YAML；只输出片段，由你选择安装位置。
print(json.dumps(config, indent=2))
