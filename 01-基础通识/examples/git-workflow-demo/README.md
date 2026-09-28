# 四个 Git 区域与本地远程

依赖 Git 2.28+、Bash、mktemp。演示工作区、暂存区、本地提交、远程仓库，以及另一份克隆怎样收到已推送的提交。

从本目录运行 `bash demo.sh`。脚本自动新建临时目录，使用 bare 仓库模拟远程，只有练习仓库的作者配置会变化，不联网。

`WORKTREE DIFF`、`STAGED DIFF` 都应出现新增 `radar`，但代表不同阶段；`TEAMMATE CONTENT` 应依次显示 camera、radar；`COMMIT COUNT` 为 2。空仓库第一次克隆时的警告是演示前提，不是失败。

终端打印的 lab 路径用于事后检查。若要清理，先检查这个目录确实属于本实验，再用 `rm -ri -- 实际路径` 逐项确认。不要删自己的教材或项目仓库。
