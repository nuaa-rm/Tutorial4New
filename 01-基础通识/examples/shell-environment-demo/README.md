# Shell 变量与环境继承

演示普通 Shell 变量、导出的环境变量及父子进程之间的单向继承。依赖 Bash，无需安装其他包。

从本目录运行：

```bash
bash parent.sh
```

应得到：

```text
parent: local=armor exported=camera
child: local=unset exported=camera
child changed: exported=radar
parent after child: exported=camera
```

在 `parent.sh` 的 `RM_LOCAL=armor` 前加 `export`，再次运行，子进程的 local 会变成 armor。恢复后再将 `bash child.sh` 改为 `source child.sh`，最后一行会变为 radar：source 在当前 Shell 执行文件。每次只改一项，完成后恢复。
