#!/usr/bin/env bash
set -eu
# 远程也放在本地临时目录；不访问账号，不改变用户全局配置。
lab=$(mktemp -d)
printf 'lab=%s\n' "$lab"
git init --bare --initial-branch=main "$lab/remote.git"
git clone "$lab/remote.git" "$lab/student"
cd -- "$lab/student"
git config user.name 'Training Student'
git config user.email 'student@example.invalid'
printf 'camera\n' > modules.txt
git add modules.txt
git commit -m 'Record camera module'
git push -u origin main
printf 'radar\n' >> modules.txt
printf '\nWORKTREE DIFF\n'
git diff -- modules.txt
git add modules.txt
printf '\nSTAGED DIFF\n'
git diff --cached -- modules.txt
git commit -m 'Record radar module'
git push
git clone "$lab/remote.git" "$lab/teammate"
printf '\nTEAMMATE CONTENT\n'
cat "$lab/teammate/modules.txt"
printf '\nCOMMIT COUNT\n'
git -C "$lab/teammate" rev-list --count HEAD
printf '保留实验目录以便检查：%s\n' "$lab"
