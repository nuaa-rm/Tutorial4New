#!/usr/bin/env python3
"""前端检查实际命令、人工图像观测、时刻变式及明确未知项。"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import cv2
import numpy as np

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--project',type=Path,required=True);c.add_argument('--work',type=Path,required=True);c.add_argument('--evidence',type=Path,required=True);a=c.parse_args();p=a.project.resolve();w=a.work.resolve();w.mkdir(parents=True,exist_ok=True);records=[]
def rec(name,data):records.append({'name':name,'status':'PASS','details':data})
cmd=[sys.executable,str(p/'make_frames.py'),'--output',str(w/'out')];output=subprocess.check_output(cmd,text=True);rec('按正文生成图像',{'command':cmd,'stdout':output})
images={name:cv2.imread(str(w/'out'/f'{name}.png'),cv2.IMREAD_UNCHANGED) for name in ['global_short','rolling_short','global_long']}
for name,image in images.items():
 assert image.shape==(64,160) and image.dtype==np.uint8
 cmd=[sys.executable,str(p/'check_image.py'),str(w/'out'/f'{name}.png')];data=json.loads(subprocess.check_output(cmd,text=True));assert data['width']==160 and data['height']==64 and data['channels']==1 and data['near_max_fraction']==0 and data['camera_serial'] is None and data['exposure_us'] is None
 assert data['sha256']==hashlib.sha256((w/'out'/f'{name}.png').read_bytes()).hexdigest()
 rec('实际文件记录 '+name,{'command':cmd,'output':data,'image_sha256':data['sha256']})
def center(image,row):
 signal=image[row].astype(float)-20;return float(np.dot(np.arange(160),signal)/signal.sum())
assert abs(center(images['rolling_short'],63)-center(images['rolling_short'],0)-32)<1e-10
assert np.array_equal(images['global_short'][0],images['global_short'][63]) and np.array_equal(images['global_long'][0],images['global_long'][63])
widths={name:int(np.count_nonzero(image[0]>20)) for name,image in images.items()};assert widths['global_short']==11 and widths['global_long']==31
rec('独立观测倾斜与拖影',{'rolling_row_center_shift_px':32,'first_row_nonbackground_width_px':widths,'boundary':'归一化平均人工模型，非相机量测'})
for name,image,fraction in [('white',np.full((8,10),255,np.uint8),1.),('color',np.tile(np.uint8([255,0,0]),(8,10,1)),1.)]:
 path=w/f'{name}.png';assert cv2.imwrite(str(path),image);cmd=[sys.executable,str(p/'check_image.py'),str(path)];data=json.loads(subprocess.check_output(cmd,text=True));assert data['near_max_fraction']==fraction;rec('近最大值线索 '+name,{'command':cmd,'output':data,'note':'白色/单色像素不能独立证明传感器过曝'})
for name,image in [('sixteen',np.zeros((8,10),np.uint16)),('rgba',np.zeros((8,10,4),np.uint8))]:
 path=w/f'{name}.png';assert cv2.imwrite(str(path),image);cmd=[sys.executable,str(p/'check_image.py'),str(path)];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==2;rec('格式拒绝 '+name,{'command':cmd,'stderr':r.stderr})
r=subprocess.run([sys.executable,str(p/'check_image.py'),str(w/'missing.png')],capture_output=True,text=True);assert r.returncode==2;rec('缺图拒绝',{'stderr':r.stderr})
cmd=[sys.executable,str(p/'timing.py'),str(p/'times.csv')];data=json.loads(subprocess.check_output(cmd,text=True));assert data=={'observed_sample_fps':100.,'result_delay_ms':[35.,35.,35.],'end_to_end_ms':[45.,45.,45.]};rec('实际人工时刻表',{'command':cmd,'output':data})
rows=list(csv.DictReader((p/'times.csv').open()));keys=list(rows[0])
variants=[]
for name,key,values in [('slower','sample_ms',[0,20,40]),('future','result_ms',[-1,45,55]),('nonfinite','sample_ms',['nan',10,20]),('duplicate-frame','frame',[0,0,2]),('bad-clock','clock',['other','demo_clock','demo_clock']),('unordered','sample_ms',[0,0,20])]:
 changed=[dict(row) for row in rows]
 for row,value in zip(changed,values):row[key]=str(value)
 if name=='slower':
  for row,result,execute in zip(changed,[50,70,90],[60,80,100]):row['result_ms']=str(result);row['execute_ms']=str(execute)
 variants.append((name,changed))
for name,changed in variants:
 path=w/f'{name}.csv'
 with path.open('w') as f:writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(changed)
 cmd=[sys.executable,str(p/'timing.py'),str(path)];r=subprocess.run(cmd,capture_output=True,text=True)
 if name=='slower':
  assert r.returncode==0;data=json.loads(r.stdout);assert data=={'observed_sample_fps':50.,'result_delay_ms':[50.]*3,'end_to_end_ms':[60.]*3};rec('实际降帧变式',{'command':cmd,'output':data})
 else:assert r.returncode==2;rec('时刻/配对拒绝 '+name,{'command':cmd,'stderr':r.stderr})
rec('现场检查记录/明确缺项',{'raw_image':str(w/'out/global_short.png'),'observation':'教学竖条，近最大值比例0；曝光期间运动导致展宽，行间时序使倾斜','unknown':['真实设备型号/序列号/镜头','实际曝光/增益/触发','内参/畸变/配置备份与恢复','真实采样时钟/执行时间'],'next':'实机按序列号读配置并保存原始帧/时刻；模型不能补全这些事实','restoration':'本次仅生成临时文件，未改变设备参数'})
a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps({'python':platform.python_version(),'opencv':cv2.__version__,'numpy':np.__version__,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='.gitignore'},'records':records,'boundaries':['图像和CSV都是人工教材样本；不是设备性能或实际执行测速','真实设备/SDK设置读取保存恢复、运动光照对照与端到端时刻未完成']},ensure_ascii=False,indent=2)+'\n');print(len(records),'records passed',a.evidence)
