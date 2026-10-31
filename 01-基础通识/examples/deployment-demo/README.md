# 部署心跳小项目

这个小项目用一个只输出时间戳的 Python 进程，演示运行目录、版本标记、日志、终端会话与 systemd 服务的关系。不访问相机、串口、网络或机器人控制设备。

依赖：Python 3；服务操作需要有 systemd 用户管理器的 Linux 登录环境。教材操作以 Ubuntu 22.04 为例；容器、WSL 和没有用户总线的 SSH 会话可能无法运行 `systemctl --user`。

## 先在前台运行

从本目录执行：

```bash
python3 heartbeat.py --count 3 --interval 0.2
python3 heartbeat.py --count 5 --interval 0.2 --fail-after 2
```

第一条打印启动信息与 `heartbeat=1` 到 `heartbeat=3`，正常退出，状态码为 0。第二条在第 2 次输出后打印模拟失败，状态码为 1。启动信息包含 PID、环境变量 `RM_DEMO_VERSION`（未设置时为 `manual-v1`）及当前工作目录。可在命令之后单独运行 `echo $?` 检查状态码。

不传 `--count` 会持续输出，用 Ctrl+C 停止；`--interval` 是秒，`--fail-after` 是输出次数，不是秒。状态码只表示这个练习进程的退出情况，心跳持续输出不能证明相机或算法工作正确。

## 放进 tmux

Ubuntu 缺少工具时先安装 `sudo apt install tmux htop`。在机器人 SSH 会话里执行：

```bash
tmux new -s rm-debug
python3 heartbeat.py
```

先按 Ctrl+B，松开，再按 D，离开 tmux。重新 SSH 进入后运行 `tmux attach -t rm-debug`，应看到序号继续增长。按 Ctrl+C 停止程序，再运行 `exit` 关闭这个窗口。该功能保留的是当前主机上的会话，不能抵抗关机、重启、进程崩溃或系统终止用户会话。

## 作为用户服务启动

以下命令从本目录执行。先确认 `~/rm-deploy-demo` 没有同名旧实验，目标 service 名也未用于自己的程序；如已有内容，先另选目录并同步修改 service，不能直接覆盖。若前面的部署步骤已把本项目放在 `~/rm-deploy-demo`，跳过下面的 `cp heartbeat.py` 一行，避免把文件复制给自身。

```bash
mkdir -p ~/rm-deploy-demo ~/.config/systemd/user
cp heartbeat.py ~/rm-deploy-demo/
cp rm-heartbeat.service ~/.config/systemd/user/
systemd-analyze --user verify ~/.config/systemd/user/rm-heartbeat.service
systemctl --user daemon-reload
systemctl --user start rm-heartbeat.service
systemctl --user status rm-heartbeat.service --no-pager
journalctl --user -u rm-heartbeat.service -n 10 --no-pager
```

预期服务是 `active (running)`；日志中有 `version=service-v1`、`cwd=/home/你的用户/rm-deploy-demo` 和连续心跳。`%h` 由 systemd 展开为用户家目录；`-u` 让 Python 输出不等缓冲区积满才写入日志。服务使用绝对解释器路径，不依赖交互终端的 `.bashrc`。这份 unit 的 `[Install]` 允许以后设置随用户管理器启动，本实验只 `start`，没有启用自启动。

修改 unit 后先 `daemon-reload`，再 `restart`；只改 Python 源码则重启服务即可。想观察失败重启，可以在自己复制的 unit 的 `ExecStart` 行末加 `--fail-after 2`，再重载、重启并观察日志。服务每次失败等待 2 秒，但 30 秒内启动最多 3 次，超过后可能进入 `start-limit-hit`。修复配置、停止服务后可用 `systemctl --user reset-failed rm-heartbeat.service` 清掉失败记录，再按需启动。不要让故障重启循环长期运行。

```bash
systemctl --user stop rm-heartbeat.service
systemctl --user is-active rm-heartbeat.service
```

停止后应返回 `inactive`，日志不再新增心跳。用 `journalctl --user -u rm-heartbeat.service -f` 跟随日志时，Ctrl+C 只是停止看日志；要停程序仍用 `systemctl --user stop`。

## 清理与适用范围

本实验没有 `enable`，因此不需要 `disable`。先停止服务，只删除你刚复制的这一个 unit，再重载：

```bash
systemctl --user stop rm-heartbeat.service
systemctl --user reset-failed rm-heartbeat.service
rm ~/.config/systemd/user/rm-heartbeat.service
systemctl --user daemon-reload
```

最后检查 `~/rm-deploy-demo`，按需删除这次复制的 `heartbeat.py`，空目录可用 `rmdir ~/rm-deploy-demo` 移除。保留原始教材工程，不用递归删除来清理练习。

用户服务受用户管理器生命周期影响。`enable` 不等于“开机无人登录也能运行”；`loginctl enable-linger` 会改变用户管理器的启动和保留策略，真实无人值守部署应由队内维护者决定使用系统服务还是 lingering，并验证设备权限、启动顺序、日志容量与重启恢复。本例没有配置 lingering，也没有替你启动真实机器人程序。

软件检查：前台有限次数、失败退出与 unit 静态检查可独立完成；服务实际重启、跨 SSH 会话、重启系统和目标硬件验证应单独记录。

官方查阅入口：[tmux 入门](https://github.com/tmux/tmux/wiki/Getting-Started)、[systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)、[systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html)。
