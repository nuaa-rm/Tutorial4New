#!/usr/bin/env bash
set -eu
# 用自己创建的本地仓库模拟依赖；file 协议许可仅对指定命令生效。
lab=$(mktemp -d)
printf 'lab=%s\n' "$lab"
git init --initial-branch=main "$lab/helper"
cd -- "$lab/helper"
git config user.name 'Training Student'
git config user.email 'student@example.invalid'
git config commit.gpgsign false
printf 'camera-utils v1\n' > version.txt
git add version.txt
git commit -m 'Release camera helper v1'

git init --initial-branch=main "$lab/student"
cd -- "$lab/student"
git config user.name 'Training Student'
git config user.email 'student@example.invalid'
git config commit.gpgsign false
printf 'vision project\n' > README.md
git add README.md
git commit -m 'Start vision project'
git -c protocol.file.allow=always submodule add "$lab/helper" libs/helper
git diff --cached -- .gitmodules
git commit -m 'Pin camera helper v1'
printf '\nRECORDED SUBMODULE\n'
git ls-tree HEAD libs/helper

# 普通克隆先得到主仓库；初始化后才能读到子模块文件。
git clone "$lab/student" "$lab/teammate"
cd -- "$lab/teammate"
printf '\nBEFORE INITIALIZATION\n'
git submodule status
git -c protocol.file.allow=always submodule update --init --recursive
cat libs/helper/version.txt

# 先在依赖仓库提交 v2，再让主仓库记录这次提交。
cd -- "$lab/helper"
printf 'camera-utils v2\n' > version.txt
git add version.txt
git commit -m 'Release camera helper v2'
helper_v2=$(git rev-parse HEAD)
cd -- "$lab/student"
git -C libs/helper fetch origin
git -C libs/helper switch --detach "$helper_v2"
git diff --submodule=log
git add libs/helper
git commit -m 'Pin camera helper v2'

# 明确关闭自动递归，先观察主仓库记录与子模块工作区不同步的状态。
cd -- "$lab/teammate"
git -c submodule.recurse=false pull --ff-only
printf '\nAFTER PULL, BEFORE SUBMODULE UPDATE\n'
cat libs/helper/version.txt
git submodule status
git -c protocol.file.allow=always submodule update --init --recursive
printf '\nAFTER SUBMODULE UPDATE\n'
cat libs/helper/version.txt
git submodule status
printf '保留实验目录以便检查：%s\n' "$lab"
