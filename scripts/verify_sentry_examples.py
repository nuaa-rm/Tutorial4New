#!/usr/bin/env python3
"""核对纸面导航、宽度/坐标变式与同次实际Nav2结果解释。"""
import argparse
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--project',type=Path,required=True);c.add_argument('--nav-work',type=Path,required=True);c.add_argument('--evidence',type=Path,required=True);a=c.parse_args();p=a.project.resolve();records=[]
def rec(name,data):records.append({'name':name,'status':'PASS','details':data})
for name,opts,required,ok in [('default',[],.9,False),('thin',['--robot','.5','--margin','.1'],.7,True),('narrow',['--corridor','.7'],.9,False)]:
 cmd=[sys.executable,str(p/'check.py'),*opts];data=json.loads(subprocess.check_output(cmd,text=True));assert abs(data['width']['required_m']-required)<1e-12 and data['width']['straight_width_ok']==ok
 assert math.dist(data['patrol_goal_map_m'],[1,3])<1e-12
 rec('实际检查器 '+name,{'command':cmd,'result':data})
for opts in [['--corridor','-1'],['--margin','nan']]:
 cmd=[sys.executable,str(p/'check.py'),*opts];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==2;rec('无效尺寸拒绝',{'command':cmd,'stderr':r.stderr})
for folder,next_action in [('nav2','review trajectory and conditions'),('nav2-blocked','inspect goal, map and TF')]:
 source=a.nav_work/folder/'result.json';cmd=[sys.executable,str(p/'check.py'),'--result',str(source)];data=json.loads(subprocess.check_output(cmd,text=True));assert data['run']['next']==next_action
 real=json.loads(source.read_text())
 if folder=='nav2':assert real['plan_status']==real['follow_status']==4 and real['goal_error_m']<.101
 else:assert real['plan_status']==6 and real['plan_error']==206 and real['path_poses']==0 and 'follow_status' not in real and data['run']['follow_requested'] is False
 rec('解释同次实际结果 '+folder,{'command':cmd,'input':real,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':data})
sys.path.insert(0,str(p));from check import width_check,map_point,explain_result
for point,angle,t,expected in [([2,0],0,[1,1],[3,1]),([2,0],-90,[1,1],[1,-1]),([0,0],90,[1,1],[1,1])]:
 result=map_point(point,angle,t);assert math.dist(result,expected)<1e-12;rec('独立二维变换',{'point':point,'angle_deg':angle,'translation':t,'result':result})
controller_failure={'plan_status':4,'plan_error':0,'follow_status':6,'follow_error':101}
data=explain_result(controller_failure);assert data['next']=='inspect controller and execution';rec('人工跟踪失败分支',{'input':controller_failure,'result':data,'boundary':'人工软件分支输入，不是实车或实际服务器错误'})
def path(blocked):
 walls={(3,y) for y in range(5)}|({(3,5)} if blocked else set());q=deque([((0,0),[(0,0)])]);seen={(0,0)}
 while q:
  (x,y),route=q.popleft()
  if (x,y)==(5,5):return route
  for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]:
   z=(x+dx,y+dy)
   if 0<=z[0]<6 and 0<=z[1]<6 and z not in walls and z not in seen:seen.add(z);q.append((z,route+[z]))
 return []
open_route=path(False);assert len(open_route)==11 and not path(True)
rec('纸面地图实际填写/独立核对',{'route':open_route,'steps':len(open_route)-1,'new_obstacle':[3,5],'after_blocked':[],'boundary':'格点棋子，没有车体或动力学'})
rec('纸面接口/取证产物',{'arrows':['雷达目标信息','决策任务选择','场地巡逻点','地图目标'],'dimension':['0.8m通道','0.6m车宽','每侧0.15m裕量','总需求0.9m不通过'],'command_without_motion':[{'sent':True,'received':False,'next':'通信/约定'},{'sent':True,'received':True,'estop':True,'next':'保持停止，核对原因'}],'unknown':'真实机械/执行/动态传感器未取证，不能编造反馈'})
a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps({'python':platform.python_version(),'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='.gitignore'},'records':records,'boundaries':['真实Nav2服务器+软件积分执行，未验证实车到位/制动/动态避障/SLAM','跟踪失败分支为人工输入，未冒充实际错误']},ensure_ascii=False,indent=2)+'\n');print(len(records),'records passed',a.evidence)
