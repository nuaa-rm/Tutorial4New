"""打开教材入口，核对章名和显示版本，保存可复查资料卡。"""
import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import re


def audit(root, item):
    card = {"key": item["key"], "checked_on": date.today().isoformat(),
            "owner": item["owner"] or None, "method": "本机文件检查"}
    if not item["entry"]:
        return card | {"status": "未取得入口"}
    volume = root / item["volume"]
    entry = volume / item["entry"]
    card["entry"] = str(entry.resolve())
    if not entry.is_file():
        return card | {"status": "本机未取得文件"}
    content = entry.read_bytes()
    card["sha256"] = hashlib.sha256(content).hexdigest()
    main = volume / "main.tex"
    if not main.is_file():
        return card | {"status": "未取得主文件"}
    text = main.read_text()
    card["main_sha256"] = hashlib.sha256(main.read_bytes()).hexdigest()
    position = text.find(r"\input{" + item["entry"] + "}")
    if position < 0:
        return card | {"status": "入口未被主文件引用"}
    chapters = re.findall(r"\\chapter\{([^}]+)\}", text[:position])
    version = re.search(r"\\version\{([^}]+)\}", text)
    card["chapter"] = chapters[-1] if chapters else None
    card["book_version"] = version.group(1) if version else None
    same = (card["chapter"] == item["chapter"] and
            card["book_version"] == item["version"])
    card["status"] = "入口与声明一致" if same else "章名或版本不一致"
    return card


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("key")
    here = Path(__file__).resolve()
    parser.add_argument("--catalog", type=Path, default=here.with_name("catalog.csv"))
    parser.add_argument("--root", type=Path, default=here.parents[3])
    args = parser.parse_args()
    with args.catalog.open(newline="") as file:
        items = {item["key"]: item for item in csv.DictReader(file)}
    if args.key not in items:
        parser.error("没有这个索引名称，请先检查catalog.csv")
    print(json.dumps(audit(args.root, items[args.key]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
