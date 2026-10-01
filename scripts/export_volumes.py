#!/usr/bin/env python3
"""编译三卷教材，并导出每卷 PDF 和完整的 examples 目录。"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOLUMES = ("01-基础通识", "02-专项技术栈", "03-RM视觉概述")


def auxiliary_digest(build: Path) -> bytes:
    """目录、编号和交叉引用的中间文件稳定后才结束编译。"""
    digest = hashlib.sha256()
    for path in sorted(build.rglob("*")):
        if path.is_file() and path.suffix in {".aux", ".toc", ".out", ".lof", ".lot"}:
            digest.update(str(path.relative_to(build)).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.digest()


def compile_volume(name: str, build: Path, engine: str) -> Path:
    build.mkdir()
    previous = None
    for attempt in range(1, 7):
        print(f"[{name}] 第 {attempt} 次编译……", flush=True)
        result = subprocess.run(
            [engine, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
             f"-output-directory={build}", "main.tex"],
            cwd=ROOT / name, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        if result.returncode:
            raise RuntimeError(f"{name} 编译失败：\n" + "\n".join(result.stdout.splitlines()[-60:]))
        current = auxiliary_digest(build)
        if attempt >= 2 and current == previous:
            break
        previous = current
    else:
        raise RuntimeError(f"{name} 编译 6 次后目录和引用仍未稳定，未导出。")

    pdf = build / "main.pdf"
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise RuntimeError(f"{name} 未生成有效 PDF。")
    log = (build / "main.log").read_text(encoding="utf-8", errors="replace")
    if "There were undefined references" in log or "There were undefined citations" in log:
        raise RuntimeError(f"{name} 仍有未定义的引用，请修复后重新导出。")
    return pdf


def export(output: Path, overwrite: bool) -> None:
    engine = shutil.which("xelatex")
    if not engine:
        raise RuntimeError("找不到 xelatex，请先安装 XeLaTeX 和教材所需的 TeX Live 宏包。")
    for name in VOLUMES:
        source = ROOT / name
        if not (source / "main.tex").is_file() or not (source / "examples").is_dir():
            raise RuntimeError(f"{source} 缺少 main.tex 或 examples 目录。")
        destination = output / name
        if destination.is_symlink():
            raise RuntimeError(f"拒绝覆盖符号链接：{destination}")
        if destination.exists() and (not overwrite or not destination.is_dir()):
            raise RuntimeError(f"{destination} 已存在；覆盖旧卷目录请加 --overwrite。")
    # 不允许把导出目录放进教材源目录，避免覆盖源文件或递归复制。
    for name in VOLUMES:
        source = ROOT / name
        if output == source or source in output.parents or output in source.parents:
            raise RuntimeError("导出位置不能与教材源目录重叠。")

    output.mkdir(parents=True, exist_ok=True)
    # 暂存目录与导出目录位于同一文件系统，方便通过重命名发布。
    with tempfile.TemporaryDirectory(prefix=".textbook-export-", dir=output.parent) as temporary:
        stage = Path(temporary)
        for name in VOLUMES:
            pdf = compile_volume(name, stage / f"build-{name}", engine)
            bundle = stage / name
            bundle.mkdir()
            shutil.copy2(pdf, bundle / f"{name}.pdf")
            shutil.copytree(ROOT / name / "examples", bundle / "examples")

        # 三卷全部编译和复制成功后才替换旧结果；发布失败时恢复旧卷目录。
        published = []
        backups = []
        try:
            for name in VOLUMES:
                destination = output / name
                if destination.exists():
                    backup = stage / f"backup-{name}"
                    destination.rename(backup)
                    backups.append((backup, destination))
                (stage / name).rename(destination)
                published.append(destination)
        except OSError:
            for destination in reversed(published):
                shutil.rmtree(destination)
            for backup, destination in reversed(backups):
                backup.rename(destination)
            raise
    print(f"\n导出完成：{output}")
    for name in VOLUMES:
        print(f"  {name}/\n    {name}.pdf\n    examples/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "导出",
                        help="导出位置（默认：仓库根目录下的 导出）")
    parser.add_argument("--overwrite", action="store_true",
                        help="替换导出位置中已有的三个卷目录（包含旧 examples）")
    args = parser.parse_args()
    try:
        export(args.output.expanduser().resolve(), args.overwrite)
    except (OSError, RuntimeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
