#!/usr/bin/env python3
"""在独立 Xvfb 中实际点击已安装 Jazzy 标定器；不操作用户桌面。"""
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
args = cli.parse_args()
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
        env = dict(os.environ, DISPLAY=":"+display, QT_QPA_PLATFORM="xcb",
                   ROS_DOMAIN_ID="185", ROS_AUTOMATIC_DISCOVERY_RANGE="LOCALHOST",
                   ROS_LOG_DIR=str(folder/"ros-logs"), PYTHONUNBUFFERED="1")
        try:
            publog = (args.output/"publisher.txt").open("w")
            publisher = subprocess.Popen([sys.executable, str(args.project/"replay_ros.py"),
                "--images", str(args.data/"train"), "--yaml", str(args.output/"committed.yaml"),
                "--period", ".3"], env=env, stdout=publog, stderr=subprocess.STDOUT)
            processes.append(publisher)
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child",
                "--project", str(args.project), "--data", str(args.data),
                "--output", str(args.output)], env=env, timeout=180)
            if result.returncode: raise RuntimeError("GUI 子进程失败")
            assert (args.output/"committed.yaml").exists()
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

rclpy.init(args=["--ros-args", "-r", "image:=/camera/image_raw",
                "-r", "camera/set_camera_info:=/camera/set_camera_info"])
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
        until(lambda: archive_path.exists() and archive_path.stat().st_mtime_ns > before, 10)
        shutil.copy2("/tmp/calibrationdata.tar.gz", args.output/"calibrationdata.tar.gz")
        outcome["archive"] = subprocess.check_output(
            ["tar", "-tzf", str(args.output/"calibrationdata.tar.gz")]).decode().splitlines()
        capture("saved.xwd")
        message = node.c.as_message()
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
