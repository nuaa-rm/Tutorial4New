#!/usr/bin/env python3
"""实际运行自瞄概述回放，独立核对时间/变化帧及教学PnP输入。"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import cv2
import numpy as np

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--project',type=Path,required=True);c.add_argument('--evidence',type=Path,required=True);a=c.parse_args();p=a.project.resolve();records=[]
def rec(name,data): records.append({'name':name,'status':'PASS','details':data})
for delay,flight in [(35,65),(25,60),(0,0)]:
 for state_at in ['sample','control']:
  command=[sys.executable,str(p/'replay.py'),'--delay-ms',str(delay),'--flight-ms',str(flight),'--state-at',state_at]
  r=subprocess.run(command,capture_output=True,text=True,check=True);data=json.loads(r.stdout);t=data['timeline']
  assert t['hit_ms']==10+delay+flight
  assert t['horizon_ms']==flight+(delay if state_at=='sample' else 0)
  assert abs(t['x_hit_m']-(4+2*(delay+flight)/1000))<1e-12
  assert abs(t['wrong_repeat_delay_x_m']-t['x_hit_m']-(2*delay/1000 if state_at=='control' else 0))<1e-12
  assert [v['frame'] for v in data['first_changes'].values()]==[120,120,121,122]
  rec('时间线 '+str([delay,flight,state_at]),{'command':command,'result':data})
for threshold,expected in [(150,None),(129,None),(128,120),(0,119)]:
 command=[sys.executable,str(p/'replay.py'),'--pixel-threshold',str(threshold)]
 data=json.loads(subprocess.check_output(command,text=True));v=data['first_changes']['corner_u_px'];assert (v['frame'] if v else None)==expected
 rec('像素阈值 '+str(threshold),{'command':command,'result':data['first_changes']})
for opts in [['--delay-ms','-1'],['--flight-ms','nan'],['--pixel-threshold','-1']]:
 command=[sys.executable,str(p/'replay.py'),*opts];r=subprocess.run(command,capture_output=True,text=True);assert r.returncode==2
 rec('无效参数 '+str(opts),{'command':command,'exit':r.returncode,'stderr':r.stderr})
points=np.array([[-.1,-.05,0],[.1,-.05,0],[.1,.05,0],[-.1,.05,0]],dtype=np.float64)
k=np.array([[600,0,320],[0,600,240],[0,0,1]],dtype=np.float64);r=np.zeros(3);t=np.array([0,0,2.],dtype=np.float64)
pixels=cv2.projectPoints(points,r,t,k,None)[0].reshape(-1,2)
assert np.allclose(pixels,[[290,225],[350,225],[350,255],[290,255]])
ok,rv,tv=cv2.solvePnP(points,pixels,k,None);assert ok and np.allclose(tv.ravel(),t,atol=1e-8)
rec('实际OpenCV核对纸面PnP',{'camera_matrix':k.tolist(),'points':points.tolist(),'pixels':pixels.tolist(),'rvec':rv.ravel().tolist(),'tvec':tv.ravel().tolist()})
khalf=k.copy();khalf[:2]*=.5
ok,rh,th=cv2.solvePnP(points,pixels*.5,khalf,None);assert ok and np.allclose(th.ravel(),t,atol=1e-8)
rec('缩放一半同步K',{'K':khalf.tolist(),'first_pixel':(pixels*.5)[0].tolist(),'tvec':th.ravel().tolist()})
ok,rwrong,twrong=cv2.solvePnP(points,pixels*.5,k,None);assert ok and not np.allclose(twrong.ravel(),t,atol=.1)
rec('只缩像点不改内参',{'tvec':twrong.ravel().tolist(),'truth_tvec':t.tolist()})
rec('云台理想下界手算核对',{'20deg_100deg_s':20/100,'15deg_100deg_s':15/100,'10ms_max_degree':100*.01,'boundary':'不包含加速度、延迟与反馈，未做实车转动'})
rec('指标/算法纸面产物',{'A':{'hit':12,'total':20,'lost':0,'delay_ms':[10,20],'light':'亮'},'B':{'hit':12,'total':20,'lost':6,'delay_ms':[10,60],'light':'暗'},'hit_rate':[12/20,12/20],'confound':'光照不同，不能直接归因算法','mapping':{'BA':'重投影/几何','Kalman':'状态不确定性/状态估计','MPC':'轨迹与控制代价/控制序列'}})
a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps({'python':platform.python_version(),'opencv':cv2.__version__,'numpy':np.__version__,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='.gitignore'},'records':records,'boundaries':['CSV为人工教学数据，不是真实机器或完整算法输出','匀速/定飞行时间是假设，未发送控制/开火，纸面转动未冒充实车测试']},ensure_ascii=False,indent=2)+'\n');print(len(records),'records passed',a.evidence)
