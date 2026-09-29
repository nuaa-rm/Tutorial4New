# Git 离线实验：区域、提交历史与子模块

依赖 Git 2.28+、Bash、mktemp。三个脚本各自创建独立的临时目录，不必先运行另一个脚本；不联网，也不改变用户全局配置。

从本目录运行：

```bash
bash demo.sh
bash history.sh
bash submodule.sh
```

- `demo.sh` 用 bare 仓库模拟远程，演示工作区、暂存区、本地提交、远程仓库与另一份克隆。`WORKTREE DIFF`、`STAGED DIFF` 都应出现新增 radar，但代表不同阶段；`TEAMMATE CONTENT` 应依次显示 camera、radar；`COMMIT COUNT` 为 2。空仓库第一次克隆时的警告是演示前提，不是失败。
- `history.sh` 先让 main 与 feature-camera 分别提交，再变基并快进合并。`AFTER REBASE` 的功能提交在主线提交之后，两个功能提交编号不同；feature-before-rebase 保留原位置。随后从 experiment 优选标定修正，主线有 calibration.txt，没有 debug.txt；最后的提交说明记录来源编号。
- `submodule.sh` 把 helper 仓库加入 student 的 libs/helper，并从 student 克隆 teammate。`RECORDED SUBMODULE` 显示模式 160000 与依赖提交编号；初始化前的状态以 `-` 开头。初始化后文件为 v1；拉取主仓库的新提交后，子模块文件仍为 v1，状态以 `+` 开头；执行子模块更新后文件为 v2，状态首字符为空格。

子模块脚本中的 `-c protocol.file.allow=always` 仅用于本实验自己创建的可信本地依赖，许可只在当前命令中生效。实际协作应在 `.gitmodules` 使用队友能访问的 SSH/HTTPS 地址；不要把实验临时路径上传到真实项目。子模块默认检出指定提交，出现 detached HEAD 属于预期；要修改依赖时，应先在依赖仓库切到分支。

终端打印的 lab 路径用于事后检查。若要清理，先检查这个目录确实属于本实验，再用 `rm -ri -- 实际路径` 逐项确认。不要删自己的教材或项目仓库。
