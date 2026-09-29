#!/usr/bin/env python3
"""实际打开四入口，比较错误声明与副本迁移，不虚构队内确认。"""
import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--project',type=Path,required=True);c.add_argument('--work',type=Path,required=True);c.add_argument('--evidence',type=Path,required=True);a=c.parse_args();p=a.project.resolve();root=p.parents[2];w=a.work.resolve();w.mkdir(parents=True,exist_ok=True);records=[];cards={}
def rec(name,data):records.append({'name':name,'status':'PASS','details':data})
def run(key,extra=()):
 cmd=[sys.executable,str(p/'audit.py'),key,*map(str,extra)];r=subprocess.run(cmd,capture_output=True,text=True,check=True);d=json.loads(r.stdout);assert d['checked_on']==date.today().isoformat();assert d['owner'] is None;return cmd,d
expected={'build':('01-基础通识/Chapter3/3.tex','编译过程与 CMake 基础','2026.09',r'target\_link\_libraries'),'geometry':('02-专项技术栈/chapters/G_ba.tex','几何视觉与 Bundle Adjustment','2026.08','PnP'),'engineering':('03-RM视觉概述/chapters/05_engineering.tex','工程准则与调车文化','2026.08','required'),'communication':('02-专项技术栈/chapters/J_comm.tex','多机通信方法','2026.08','CRC')}
for key,(rel,title,version,concept) in expected.items():
 cmd,d=run(key);target=root/rel;assert d['status']=='入口与声明一致' and d['chapter']==title and d['book_version']==version;assert Path(d['entry'])==target;assert hashlib.sha256(target.read_bytes()).hexdigest()==d['sha256'];assert concept in target.read_text();cards[key]=d;rec('实际教材入口 '+key,{'command':cmd,'stdout':d,'read_content_marker':concept})
for key,status in [('lecture','本机未取得文件'),('team','未取得入口')]:
 cmd,d=run(key);assert d['status']==status and 'sha256' not in d;rec('明确缺项 '+key,{'command':cmd,'stdout':d})
with (p/'catalog.csv').open(newline='') as f:original=list(csv.DictReader(f));fields=list(original[0])
def catalog(rows,name):
 path=w/name
 with path.open('w',newline='') as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
 return path
for field,value in [('version','2026.07'),('chapter','错章名'),('entry','chapters/not_here.tex')]:
 rows=[dict(row) for row in original];next(row for row in rows if row['key']=='communication')[field]=value;path=catalog(rows,f'bad-{field}.csv');cmd,d=run('communication',['--catalog',path]);assert d['status']==('本机未取得文件' if field=='entry' else '章名或版本不一致');rec('清单变式 '+field,{'command':cmd,'stdout':d})
book=w/'book';volume=book/'02-专项技术栈';(volume/'chapters').mkdir(parents=True,exist_ok=True);shutil.copy2(root/'02-专项技术栈/main.tex',volume/'main.tex');shutil.copy2(root/'02-专项技术栈/chapters/J_comm.tex',volume/'chapters/comm_copy.tex');rows=[dict(row) for row in original];next(row for row in rows if row['key']=='communication')['entry']='chapters/comm_copy.tex';path=catalog(rows,'moved.csv');cmd,d=run('communication',['--catalog',path,'--root',book]);assert d['status']=='入口未被主文件引用';rec('只移动正文',{'command':cmd,'stdout':d,'boundary':'副本仅用于该入口检查，不声称整卷可编译'})
main=volume/'main.tex';main.write_text(main.read_text().replace(r'\input{chapters/J_comm.tex}',r'\input{chapters/comm_copy.tex}'));cmd,d=run('communication',['--catalog',path,'--root',book]);assert d['status']=='入口与声明一致' and d['sha256']==cards['communication']['sha256'] and d['main_sha256']!=cards['communication']['main_sha256'];rec('同步主文件后迁移',{'command':cmd,'stdout':d,'same_content':True,'changed_main':True})
r=subprocess.run([sys.executable,str(p/'audit.py'),'unknown'],capture_output=True,text=True);assert r.returncode==2;rec('未知名称拒绝',{'stderr':r.stderr,'returncode':r.returncode})
practice=[]
for key,meaning in [('communication','接收字节、解析教学帧，输出有效消息'),('geometry','空间点与像素对应，输出位姿/重投影检查')]:practice.append({'file':cards[key]['entry'],'chapter':cards[key]['chapter'],'checked_on':cards[key]['checked_on'],'meaning':meaning,'sha256':cards[key]['sha256']})
(w/'practice.json').write_text(json.dumps(practice,ensure_ascii=False,indent=2)+'\n');rec('章末实际打开两个卷二入口',practice)
plan=[{'step':'卷一工程','product':'构建/运行/调试记录'},{'step':'卷三导航与工程','product':'地图/定位/目标接口图及前提'},{'step':'卷二ROS2与导航','product':'正常与无路路线的运行记录'},{'step':'现场','product':'受控现场演示，当前未完成'}];(w/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n');rec('方向学习计划产物',plan)
a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps({'python':platform.python_version(),'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='.gitignore'},'records':records,'boundaries':['教材四入口与教学副本实际打开，目录/链接存在不证明协议适用','队内讲义/仓库/当年协议/实际责任人尚未提供，不编造批准或第二人签名']},ensure_ascii=False,indent=2)+'\n');print(len(records),'records passed',a.evidence)
