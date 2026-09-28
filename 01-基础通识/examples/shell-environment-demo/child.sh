#!/usr/bin/env bash
set -eu
printf 'child: local=%s exported=%s\n' "${RM_LOCAL-unset}" "$RM_EXPORTED"
# 子进程改自己的环境，不会改回父进程。
export RM_EXPORTED=radar
printf 'child changed: exported=%s\n' "$RM_EXPORTED"
