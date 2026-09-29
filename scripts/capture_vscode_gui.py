#!/usr/bin/env python3
"""在独立 Xvfb 和临时配置中操作 VS Code，逐行接收 JSON 并保存真实截图。

先查看截图再发送下一步，不自动选择命令面板的第一项。
例：{"keys":"ctrl+shift+p", "text":"CMake: Build", "name":"build-menu"}
确认选项后：{"keys":"Down Return", "name":"built", "wait":3}
鼠标操作：{"click":[150,156], "name":"locals"}；退出：{"quit":true}。
输出目录必须不存在，防止覆盖旧证据；不会修改个人 VS Code 设置。
"""
import argparse
import json
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import time


def profile_pids(profile):
    """只查本次临时配置的参数，不输出其他进程的命令行。"""
    result = []
    for path in Path("/proc").iterdir():
        if not path.name.isdecimal():
            continue
        try:
            argv = [p.decode(errors="replace") for p in (path/"cmdline").read_bytes().split(b"\0") if p]
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if ("--user-data-dir="+str(profile) in argv or
                any(a == "--user-data-dir" and i+1 < len(argv) and argv[i+1] == str(profile)
                    for i, a in enumerate(argv))):
            result.append(int(path.name))
    return result


def stop_group(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--code", default="/run/host/usr/share/code/code")
    parser.add_argument("--extensions", type=Path, required=True)
    parser.add_argument("--font", default="Maple Mono NF CN")
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir()  # 不覆盖先前的证据。
    project = root/"project"
    shutil.copytree(Path(__file__).resolve().parents[1]/"01-基础通识/examples/ide-demo", project)
    user = root/"user-data"
    (user/"User").mkdir(parents=True)
    settings = {"workbench.startupEditor":"none", "workbench.colorTheme":"Default Light Modern",
                "update.mode":"none", "extensions.autoUpdate":False,
                "extensions.autoCheckUpdates":False, "telemetry.telemetryLevel":"off",
                "cmake.useCMakePresets":"never", "cmake.configureOnOpen":False,
                "cmake.buildDirectory":"${workspaceFolder}/build-vscode",
                "terminal.integrated.fontFamily":args.font}
    (user/"User/settings.json").write_text(json.dumps(settings, indent=2)+"\n")
    rfd, wfd = os.pipe()
    xvfb = subprocess.Popen(["Xvfb", "-displayfd", str(wfd), "-screen", "0", "1600x1000x24"],
                            pass_fds=(wfd,), start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(wfd)
    code = None
    try:
        if not select.select([rfd], [], [], 10)[0]:
            raise TimeoutError("Xvfb 未提供显示编号")
        display = os.read(rfd, 100).decode().strip()
        if not display:
            raise RuntimeError("Xvfb 启动失败")
        env = dict(os.environ, DISPLAY=":"+display, XDG_SESSION_TYPE="x11",
                   QT_QPA_PLATFORM="xcb", XDG_CONFIG_HOME=str(root/"xdg-config"),
                   XDG_CACHE_HOME=str(root/"xdg-cache"), XDG_STATE_HOME=str(root/"xdg-state"))
        env.pop("WAYLAND_DISPLAY", None)
        with (root/"code.txt").open("w") as log, (root/"actions.jsonl").open("w") as actions:
            code = subprocess.Popen(["dbus-run-session", "--", args.code,
                "--user-data-dir", str(user), "--shared-data-dir", str(root/"shared-data"),
                "--extensions-dir", str(args.extensions), "--locale", "en", "--disable-gpu",
                "--ozone-platform=x11", "--new-window", "--goto", str(project/"main.cpp")+":11",
                str(project)], env=env, start_new_session=True, stdout=log, stderr=subprocess.STDOUT)

            def run(argv):
                subprocess.run(argv, env=env, check=True, capture_output=True)

            def shot(name):
                if not name or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in name):
                    raise ValueError("截图名只使用字母、数字、横线或下划线")
                path = root/(name+".xwd")
                run(["xwd", "-root", "-silent", "-out", str(path)])
                print(json.dumps({"snapshot":name, "path":str(path)}), flush=True)

            time.sleep(8)
            print(json.dumps({"ready":True, "display":display, "folder":str(root)}), flush=True)
            shot("startup")
            for line in sys.stdin:
                item = json.loads(line)
                actions.write(json.dumps(item)+"\n")
                actions.flush()
                if item.get("quit"):
                    break
                if "keys" in item:
                    run(["xdotool", "key", *item["keys"].split()])
                if "text" in item:
                    run(["xdotool", "type", "--clearmodifiers", item["text"]])
                if "click" in item:
                    x, y = item["click"]
                    run(["xdotool", "mousemove", str(x), str(y), "click", "1"])
                time.sleep(item.get("wait", 1))
                shot(item["name"])
    finally:
        os.close(rfd)
        if code is not None:
            stop_group(code)
        # Electron 启动器可能先退出；仅清理显式使用本次临时配置的进程。
        owned = profile_pids(user)
        for pid in owned:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        deadline = time.monotonic()+3
        while profile_pids(user) and time.monotonic() < deadline:
            time.sleep(.1)
        for pid in profile_pids(user):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        stop_group(xvfb)
        (root/"cleanup.json").write_text(json.dumps({"profile":str(user), "terminated_pids":owned,
            "remaining_pids":profile_pids(user)}, indent=2)+"\n")


if __name__ == "__main__":
    main()
