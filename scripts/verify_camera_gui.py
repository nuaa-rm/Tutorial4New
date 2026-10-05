#!/usr/bin/env python3
"""在独立 Xvfb 中核验已安装的 Humble 标定器；不操作用户桌面。"""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

cli = argparse.ArgumentParser(description=__doc__)
cli.add_argument("--project", type=Path, required=True)
cli.add_argument("--data", type=Path, required=True)
cli.add_argument("--output", type=Path, required=True)
cli.add_argument("--child", action="store_true")
cli.add_argument("--stereo", action="store_true")
args = cli.parse_args()
if os.environ.get('ROS_DISTRO') != 'humble':
    raise SystemExit('请先 source /opt/ros/humble/setup.bash')
args.output.mkdir(parents=True, exist_ok=True)
if not args.child:
    saved = Path("/tmp/calibrationdata.tar.gz")
    with tempfile.TemporaryDirectory(prefix="camera-gui-") as folder:
        folder = Path(folder)
        backup = folder/"previous.tar.gz"
        if saved.exists(): shutil.copy2(saved, backup)
        processes = []
        rfd, wfd = os.pipe()
        xvfb = subprocess.Popen(["Xvfb", "-displayfd", str(wfd), "-screen", "0", "1600x1000x24"],
                                pass_fds=(wfd,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(xvfb); os.close(wfd)
        display = os.read(rfd, 100).decode().strip(); os.close(rfd)
        env = dict(os.environ, DISPLAY=":"+display, QT_QPA_PLATFORM="xcb", GDK_BACKEND="x11",
                   ROS_DOMAIN_ID="189" if args.stereo else "185", ROS_LOCALHOST_ONLY="1",
                   ROS_LOG_DIR=str(folder/"ros-logs"), PYTHONUNBUFFERED="1")
        env.pop("WAYLAND_DISPLAY", None)
        try:
            publog = (args.output/"publisher.txt").open("w")
            publisher = subprocess.Popen([sys.executable, str(args.project/"replay_ros.py"),
                "--images", str(args.data/("left" if args.stereo else "train")), "--yaml", str(args.output/"committed.yaml"),
                "--period", ".3", *(["--right", str(args.data/"right"), "--namespace", "left"] if args.stereo else [])], env=env, stdout=publog, stderr=subprocess.STDOUT)
            processes.append(publisher)
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child",
                "--project", str(args.project), "--data", str(args.data),
                "--output", str(args.output), *(["--stereo"] if args.stereo else [])], env=env, timeout=180)
            if result.returncode: raise RuntimeError("GUI 子进程失败")
            assert (args.output/"committed.yaml").exists()
            if args.stereo:
                import numpy as np
                sys.path.insert(0, str(args.project))
                from model_io import load_yaml
                result_file = args.output/"gui.json"
                outcome = json.loads(result_file.read_text())
                for side, name in [("left", "committed.yaml"), ("right", "committed_right.yaml")]:
                    K,D,R,P,size = load_yaml(args.output/name)
                    m = outcome["messages"][side]
                    assert size == (640,480)
                    assert all(np.allclose(value.reshape(-1), m[key], atol=1e-10, rtol=0)
                               for value,key in [(K,"K"),(D,"D"),(R,"R"),(P,"P")])
                outcome["both_persisted_K_D_R_P_match"] = True
                result_file.write_text(json.dumps(outcome, indent=2))
        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    process.send_signal(signal.SIGINT)
                    try: process.wait(timeout=5)
                    except subprocess.TimeoutExpired: process.kill(); process.wait()
            if backup.exists(): shutil.copy2(backup, saved)
            elif saved.exists(): saved.unlink()
    raise SystemExit(0)

import cv2
import rclpy
from camera_calibration.calibrator import ChessboardInfo
from camera_calibration.camera_calibrator import OpenCVCalibrationNode

remaps = (["-r", "left:=/left/image_raw", "-r", "right:=/right/image_raw",
           "-r", "left_camera/set_camera_info:=/left/set_camera_info",
           "-r", "right_camera/set_camera_info:=/right/set_camera_info"] if args.stereo else
          ["-r", "image:=/camera/image_raw", "-r", "camera/set_camera_info:=/camera/set_camera_info"])
rclpy.init(args=["--ros-args", *remaps])
board = ChessboardInfo(n_cols=9, n_rows=6, dim=.025)
node = OpenCVCalibrationNode("camera_calibrator", [board], flags=cv2.CALIB_FIX_K3,
                            camera_name="front")
# 使用与正文 CLI 相同的话题、服务映射，在进程启动时传入 ROS 参数。
# 此处类构造后没有改回调和采样/标定内部状态。
outcome = {}


def until(test, seconds=120):
    end = time.monotonic()+seconds
    while not test():
        if time.monotonic() > end: raise TimeoutError("等待 GUI 状态超时")
        time.sleep(.1)


def driver():
    try:
        until(lambda: node.c is not None and node.c.goodenough)
        width = node.displaywidth+100
        cv2.resizeWindow("display", width, 650)
        time.sleep(.5)
        window = subprocess.check_output(["xdotool", "search", "--name", "^display$"]).decode().split()[0]

        def capture(name):
            subprocess.run(["xwd", "-silent", "-id", window, "-out", str(args.output/name)], check=True)

        def click(y):
            x0, y0, w, h = cv2.getWindowImageRect("display")
            x = round(x0+(node.displaywidth+50)/width*w)
            y = round(y0+y/node._last_display.shape[0]*h)
            subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"], check=True)

        capture("sampling.xwd")
        outcome["samples"] = len(node.c.db)
        outcome["coverage"] = node.c.compute_goodenough()
        click(230)
        until(lambda: node.c.calibrated, 60)
        time.sleep(.7)
        capture("calibrated.xwd")
        archive_path = Path("/tmp/calibrationdata.tar.gz")
        before = archive_path.stat().st_mtime_ns if archive_path.exists() else 0
        click(330)
        def archive_ready():
            if not archive_path.exists() or archive_path.stat().st_mtime_ns <= before:
                return False
            # SAVE 先创建文件，再写入；完整读取成功后才复制较大的双目存档。
            return subprocess.run(["tar", "-tzf", str(archive_path)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        until(archive_ready, 10)
        shutil.copy2("/tmp/calibrationdata.tar.gz", args.output/"calibrationdata.tar.gz")
        outcome["archive"] = subprocess.check_output(
            ["tar", "-tzf", str(args.output/"calibrationdata.tar.gz")]).decode().splitlines()
        capture("saved.xwd")
        message = node.c.as_message()
        if args.stereo:
            assert not node.c.is_mono
            outcome["messages"] = {side: {"K": list(m.k), "D": list(m.d),
                                          "R": list(m.r), "P": list(m.p)}
                                   for side,m in zip(["left","right"],message)}
            right = message[1]
            outcome["baseline_m"] = -right.p[3]/right.p[0]
        else:
            outcome["K"] = list(message.k); outcome["D"] = list(message.d)
        click(430)
        until(lambda: not rclpy.ok(), 10)
        outcome["commit_shutdown"] = True
    except BaseException as error:
        outcome["error"] = repr(error)
        if rclpy.ok(): rclpy.shutdown()


thread = threading.Thread(target=driver)
thread.start()
try:
    node.spin()
finally:
    thread.join(timeout=5)
    node.destroy_node()
    if rclpy.ok(): rclpy.shutdown()
    (args.output/"gui.json").write_text(json.dumps(outcome, indent=2))
if "error" in outcome: raise RuntimeError(outcome["error"])
print(json.dumps(outcome), flush=True)
