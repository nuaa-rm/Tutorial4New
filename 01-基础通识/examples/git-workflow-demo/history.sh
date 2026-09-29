#!/usr/bin/env bash
set -eu
# 单独建仓库；不改动 demo.sh 的实验目录，也不推送改写过的历史。
lab=$(mktemp -d)
printf 'lab=%s\n' "$lab"
git init --initial-branch=main "$lab"
cd -- "$lab"
git config user.name 'Training Student'
git config user.email 'student@example.invalid'
git config commit.gpgsign false
printf 'vision project\n' > README.md
git add README.md
git commit -m 'Start vision project'

# 两条分支分别前进，修改不同文件，便于先观察无冲突的变基。
git switch -c feature-camera
printf 'camera\n' > camera.txt
git add camera.txt
git commit -m 'Add camera module'
git branch feature-before-rebase
git switch main
printf 'check timestamps\n' > review.txt
git add review.txt
git commit -m 'Add team review note'
printf '\nBEFORE REBASE\n'
git log --oneline --graph main feature-camera
git switch feature-camera
git rebase main
printf '\nAFTER REBASE\n'
git log --oneline --graph main feature-camera
printf '\nOLD AND NEW FEATURE COMMITS\n'
git rev-parse feature-before-rebase feature-camera
git switch main
git merge --ff-only feature-camera

# 实验分支有两个提交，主线只需要其中独立的标定修正。
git switch -c experiment
printf 'temporary debug output\n' > debug.txt
git add debug.txt
git commit -m 'Add experimental debug note'
printf 'camera_offset=2\n' > calibration.txt
git add calibration.txt
git commit -m 'Fix camera calibration offset'
fix_commit=$(git rev-parse HEAD)
git switch main
printf 'release checklist\n' > release.txt
git add release.txt
git commit -m 'Add release checklist'
git show --stat "$fix_commit"
git cherry-pick -x "$fix_commit"
printf '\nAFTER CHERRY-PICK\n'
git log --oneline --graph -6 main experiment
printf '\nMAIN FILES\n'
git ls-tree --name-only HEAD
printf '\nPICKED COMMIT MESSAGE\n'
git log -1 --format=%B
printf '保留实验目录以便检查：%s\n' "$lab"
