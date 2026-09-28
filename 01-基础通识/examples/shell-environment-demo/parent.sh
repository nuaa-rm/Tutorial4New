#!/usr/bin/env bash
set -eu
# 先进入脚本目录，避免从其他目录启动时找不到子脚本。
cd -- "$(dirname -- "$0")"
RM_LOCAL=armor
export RM_EXPORTED=camera
printf 'parent: local=%s exported=%s\n' "$RM_LOCAL" "$RM_EXPORTED"
bash child.sh
printf 'parent after child: exported=%s\n' "$RM_EXPORTED"
