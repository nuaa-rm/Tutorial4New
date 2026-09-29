#!/usr/bin/env python3
"""实际运行选源和高度变式，独立核对投影/映射与纸面记录。"""
import argparse
from copy import deepcopy
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
variants=[('default',[], 'vision'),('radio',['--radio-age','50','--vision-age','40'],'radio'),('expired',['--radio-age','120','--vision-age','40'],'vision'),('invalid',['--radio-age','50','--vision-age','40','--radio-invalid'],'vision'),('both-expired',['--radio-age','120','--vision-age','160'],None),('boundary',['--radio-age','100'],'radio'),('past-boundary',['--radio-age','101'],'vision'),('future',['--radio-age','-1'],'vision'),('wrong-frame',['--radio-age','50','--radio-frame','camera'],'vision')]
for name,opts,source in variants:
 cmd=[sys.executable,str(p/'choose.py'),*opts];data=json.loads(subprocess.check_output(cmd,text=True));assert data['source']==source and data['valid']==(source is not None)
 if source is None: assert data['xy_m'] is None
 rec('实际选源 '+name,{'command':cmd,'output':data})
sys.path.insert(0,str(p));from choose import choose
original=json.loads((p/'sources.json').read_text());original['radio']['sample_ms']=950
for key,value in [('target',8),('unit','cm'),('clock','other_clock'),('quality_ok',False),('xy',[float('nan'),2]),('xy',[True,2]),('xy',[3]),('sample_ms',True)]:
 data=deepcopy(original);data['radio'][key]=value;result=choose(data);assert result['source']=='vision'
 rec('不合格消息回退 '+key,{'input_change':repr(value),'output':result})
data=deepcopy(original);data['radio']['valid']=False;data['vision']['valid']=False;result=choose(data);assert result['valid'] is False and result['xy_m'] is None
rec('断开与两源失效',{'output':result})
K=np.array([[600.,0,320],[0,600,240],[0,0,1.]])
R=np.diag([1.,-1.,-1.]);C=np.array([2.,1.5,5.]);t=-R@C
for height in [0.,.5,1.,2.]:
 cmd=[sys.executable,str(p/'plane.py'),'--height',str(height)];data=json.loads(subprocess.check_output(cmd,text=True))
 uv,_=cv2.projectPoints(np.array([[3.,2.,height]]),cv2.Rodrigues(R)[0],t,K,None);uv=uv.ravel()
 assert np.linalg.norm(uv-np.array(data['pixel']))<2e-5
 # 独立用射线落地求解，未调用被测单应求解器。
 expected=[2+5/(5-height),1.5+2.5/(5-height)]
 assert math.dist(expected,data['ground_mapping_m'])<2e-6
 assert abs(math.dist(expected,[3,2])-data['error_m'])<2e-6
 rec('实际高度变式/独立射线 '+str(height),{'command':cmd,'output':data,'independent_mapping_m':expected})
for height in ['5','-1','nan']:
 cmd=[sys.executable,str(p/'plane.py'),'--height',height];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==2;rec('无效几何输入拒绝',{'command':cmd,'stderr':r.stderr})
rec('纸面输入输出与故障取证',{'roles':{'high_camera':'全场目标信息→队友/决策','vehicle_lidar':'环境量测→本车定位/障碍感知'},'coordinate_queue':'旧坐标覆盖，采样时间保持原值','event_queue':'按协议有序保留/确认/去重，不用最新值覆盖','old_position_checks':['采样→选源→发送→接收各保存时刻','跨机器先核对时钟约定','发现发送积压后查卷二多机通信'],'boundary':'教学纸面产物，未读取真实裁判、射频或车辆反馈'})
a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps({'python':platform.python_version(),'opencv':cv2.__version__,'numpy':np.__version__,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='.gitignore'},'records':records,'boundaries':['人工相机投影和人工消息，不是实机标定/射频或广播链路','配置可信，质量与有效性由上游提供；程序不验证真实识别/校验','真实设备和适用赛季协议验证未完成']},ensure_ascii=False,indent=2)+'\n');print(len(records),'records passed',a.evidence)
