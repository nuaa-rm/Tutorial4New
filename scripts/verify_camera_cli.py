#!/usr/bin/env python3
"""只在独立 Xvfb 运行正文 CLI 和图像查看器。"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--project',type=Path,required=True)
cli.add_argument('--data',type=Path,required=True)
cli.add_argument('--yaml',type=Path,required=True)
cli.add_argument('--output',type=Path,required=True)
cli.add_argument('--stereo',action='store_true')
args=cli.parse_args();args.output.mkdir(parents=True,exist_ok=True)
processes=[];logs=[];results=[]
rfd,wfd=os.pipe()
xvfb=subprocess.Popen(['Xvfb','-displayfd',str(wfd),'-screen','0','1600x1000x24'],
                     pass_fds=(wfd,),start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
processes.append(xvfb);os.close(wfd)
display=os.read(rfd,100).decode().strip();os.close(rfd)
env=dict(os.environ,DISPLAY=':'+display,QT_QPA_PLATFORM='xcb',ROS_DOMAIN_ID='190' if args.stereo else '187',PYTHONUNBUFFERED='1',
         ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',ROS_LOG_DIR=str(args.output/'logs'))
def start(command,name):
    log=(args.output/(name+'.txt')).open('w');logs.append(log)
    proc=subprocess.Popen(command,env=env,start_new_session=True,stdout=log,stderr=subprocess.STDOUT)
    processes.append(proc);return proc
def stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid,signal.SIGINT)
        try:proc.wait(timeout=8)
        except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
def capture(pattern,name):
    end=time.monotonic()+20
    while time.monotonic()<end:
        result=subprocess.run(['xdotool','search','--onlyvisible','--name',pattern],env=env,capture_output=True,text=True)
        if result.returncode==0:
            window=result.stdout.splitlines()[-1]
            subprocess.run(['xdotool','windowsize',window,'1000','800'],env=env,check=True)
            time.sleep(5)
            subprocess.run(['xwd','-silent','-id',window,'-out',str(args.output/(name+'.xwd'))],env=env,check=True)
            return
        time.sleep(.2)
    raise TimeoutError(pattern)
try:
    namespace='left' if args.stereo else 'camera'
    image_topic=f'/{namespace}/image_raw'
    rect_topic=f'/{namespace}/image_rect'
    pub=start([sys.executable,str(args.project/'replay_ros.py'),'--images',str(args.data/('left' if args.stereo else 'train')),
               '--yaml',str(args.yaml),*(['--right',str(args.data/'right'),'--namespace','left'] if args.stereo else [])],'publisher')
    time.sleep(3)
    for command in (['ros2','topic','info',image_topic,'--verbose'],
                    ['ros2','service','list','-t'],['ros2','topic','hz',image_topic]):
        try:
            r=subprocess.run(command,env=env,capture_output=True,text=True,timeout=4)
            output=r.stdout+r.stderr;code=r.returncode
        except subprocess.TimeoutExpired as e:
            output=(e.stdout or b'').decode()+(e.stderr or b'').decode();code='observed_for_4_seconds'
        results.append({'command':command,'exit':code,'output':output})
    remaps=(['-r','left:=/left/image_raw','-r','right:=/right/image_raw',
             '-r','left_camera/set_camera_info:=/left/set_camera_info',
             '-r','right_camera/set_camera_info:=/right/set_camera_info'] if args.stereo else
            ['-r','image:=/camera/image_raw','-r','camera/set_camera_info:=/camera/set_camera_info'])
    command=['ros2','run','camera_calibration','cameracalibrator','--size','9x6','--square','.025',
             *([] if args.stereo else ['--camera_name','front']),'--k-coefficients','2','--ros-args',*remaps]
    cal=start(command,'calibrator')
    capture('^display$','cli');assert cal.poll() is None
    results.append({'command':command,'window':'cli.xwd','started':True})
    stop(cal)
    rect=start(['ros2','launch','image_proc','image_proc.launch.py',f'namespace:={namespace}'],'image-proc')
    view=start(['ros2','run','rqt_image_view','rqt_image_view',rect_topic],'rqt')
    capture('rqt_image_view','rqt');assert view.poll() is None
    results.append({'command':f'rqt_image_view {rect_topic}','window':'rqt.xwd','started':True})
finally:
    for proc in reversed(processes):stop(proc)
    for log in logs:log.close()
(args.output/'cli.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False))
