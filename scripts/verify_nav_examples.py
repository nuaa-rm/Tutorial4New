#!/usr/bin/env python3
"""运行导航项目，独立核对地图/最短路/BT及真实Nav2软件闭环。"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import numpy as np
import yaml
from scipy.ndimage import distance_transform_edt

cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--project',type=Path,required=True)
cli.add_argument('--work',type=Path,required=True)
cli.add_argument('--evidence',type=Path,required=True)
a=cli.parse_args();p=a.project.resolve();w=a.work.resolve();w.mkdir(parents=True,exist_ok=True)
if os.environ.get('ROS_DISTRO') != 'humble':
 raise SystemExit('请先 source /opt/ros/humble/setup.bash')
sys.path.insert(0,str(p));import grid,bt
records=[]
def record(name,details):records.append({'name':name,'status':'PASS','details':details})
def run(name,file,*opts,fail=False):
 cmd=[sys.executable,str(p/file),*map(str,opts)]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
 assert r.returncode!=0 if fail else r.returncode==0,r.stderr
 data={'exit':r.returncode,'stderr':r.stderr[-300:]} if fail else json.loads(r.stdout)
 record(name,{'command':cmd,'result':data});return data
for name,opts in [('map',[]),('blocked',['--blocked']),('wide',['--margin',.6]),('invalid',['--margin',-1]),('nan',['--margin','nan'])]:
 run('地图/栅格 '+name,'grid.py','--output',w/name,*opts,fail=name in ['invalid','nan'])
paths=json.loads((w/'map/paths.json').read_text());occupied=grid.make_map()
for name,(path,cost,expanded) in paths.items():
 assert cost==70 and len(path)==71
 clearance=distance_transform_edt(~occupied)*.1
 assert min(clearance[j,i] for i,j in path)>.35
 assert all(abs(i-x)+abs(j-y)==1 for (i,j),(x,y) in zip(path,path[1:]))
 record('独立栅格核对 '+name,{'cost':cost,'expanded':expanded,'min_clearance':min(clearance[j,i] for i,j in path)})
assert grid.plan(occupied,3)==([],None,0);record('不可通行起终点拒绝',{'margin':3,'path':[]})
meta=yaml.safe_load((w/'map/map.yaml').read_text());pgm=(w/'map/map.pgm').read_bytes()
pixels=np.frombuffer(pgm.split(b'\n',3)[3],dtype=np.uint8).reshape(40,60)
assert np.array_equal(np.flipud(pixels)==0,occupied)
assert meta['resolution']==.1 and meta['origin']==[0.,0.,0.]
record('PGM上下翻转与YAML',{'image_row0_map_y':39,'shape':[60,40],'metadata':meta})
for ij,res,origin,expected in [((10,20),.05,(0,0,0),(.525,1.025)),((10,20),.05,(-2,-1,0),(-1.475,.025)),((2,3),.1,(1,2,0),(1.25,2.35)),((2,3),.1,(1,2,math.pi/2),(.65,2.25))]:
 actual=grid.cell_center(*ij,res,origin);assert np.allclose(actual,expected,atol=1e-14)
 record('格心 '+str(origin),{'ij':ij,'resolution':res,'xy':actual})
for ab,bc,ac,expected in [(1,2,5,3),(1,2,2,2),(2,2,5,4),(4,4,5,5)]:
 g={'A':[('B',ab),('C',ac)],'B':[('C',bc)],'C':[]}
 path,cost,_=grid.shortest(g.__getitem__,'A','C');assert cost==expected
 record('三顶点 '+str([ab,bc,ac]),{'path':path,'cost':cost})
try:grid.shortest(lambda n:[('C',-1)] if n=='A' else [],'A','C')
except ValueError:record('负边权拒绝',{'weight':-1})
else:raise AssertionError('负权未拒绝')
for name,opts,status in [('success',[],bt.SUCCESS),('fail',['--fail'],bt.FAILURE),('stuck',['--stuck'],'Timeout')]:
 data=run('恢复 '+name,'bt.py',*opts);assert data['status']==status and data['retries']<=2
 if name!='stuck':assert data['retries']==2 and [x[0] for x in data['log']].count('navigate')==3
for sequence,states,expected,called in [(False,[bt.RUNNING,bt.SUCCESS],bt.RUNNING,1),(False,[bt.FAILURE,bt.SUCCESS],bt.SUCCESS,2),(False,[bt.FAILURE,bt.FAILURE],bt.FAILURE,2),(True,[bt.RUNNING,bt.SUCCESS],bt.RUNNING,1),(True,[bt.SUCCESS,bt.SUCCESS],bt.SUCCESS,2),(True,[bt.FAILURE,bt.SUCCESS],bt.FAILURE,1)]:
 log=[];root=bt.Control([bt.Script(str(i),[s],log) for i,s in enumerate(states)],sequence)
 assert root.tick()==expected and len(log)==called
 record('控制节点 '+str([sequence,states]),{'status':expected,'log':log})
loc=run('定位修正和长墙退化','localization.py');assert np.allclose(loc['map_odom_xy'],[.3,0]) and np.allclose(loc['corrected_xy'],[.2,0]) and loc['wall_eigenvalues']==[0.,2.]
tf=run('真实tf2合成与缺失','tf_demo.py');assert np.allclose(tf['xy'],[1,4]) and tf['missing']=='LookupException'
for cmd in [['cmake','-S',str(p),'-B',str(w/'build')],['cmake','--build',str(w/'build'),'-j4']]:
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stdout+r.stderr
 record('PCL构建 '+cmd[0],{'command':cmd,'exit':r.returncode})
r=subprocess.run([str(w/'build/point_filters')],capture_output=True,text=True,check=True)
data=json.loads(r.stdout);assert data['centroid_x']==.02 and data['clean']==30
record('真实PCL三种过滤',{'command':[str(w/'build/point_filters')],'result':data})

# 隔离DDS，只启动本项目。实际Nav2进程保留日志，退出时结束本组子进程。
os.environ['ROS_DOMAIN_ID']='188';os.environ['ROS_LOCALHOST_ONLY']='1'
log=(w/'launch.txt').open('w')
cmd=['ros2','launch',str(p/'lab.launch.py'),'map:='+str(w/'map/map.yaml')]
proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
try:
 data=run('实际Nav2规划控制','client.py','--output',w/'nav2')
 assert data['plan_status']==4 and data['follow_status']==4
 assert data['goal_error_m']<.101 and data['command_samples']>20
 arrays=np.load(w/'nav2/nav2.npz');trajectory=arrays['trajectory'];commands=arrays['commands']
 assert np.all(np.isfinite(trajectory)) and np.all(np.isfinite(commands))
 assert np.max(np.abs(commands[:,0]))<=.601 and np.any(np.abs(commands[:,1])>.1)
 # 以每个障碍格的矩形边界核对圆形车体净距，不只检查质点落在哪格。
 boxes=np.array([(i*.1,j*.1) for j,i in zip(*np.where(occupied))])
 def gap(points):
  dx=np.maximum(np.maximum(boxes[:,0][None,:]-points[:,0,None],points[:,0,None]-(boxes[:,0]+.1)[None,:]),0)
  dy=np.maximum(np.maximum(boxes[:,1][None,:]-points[:,1,None],points[:,1,None]-(boxes[:,1]+.1)[None,:]),0)
  return float(np.sqrt(dx*dx+dy*dy).min())
 gaps={k:gap(arrays[k]) for k in ['path','trajectory']}
 assert min(gaps.values())>.15
 record('实际保存路径/轨迹/速度独立核对',{'min_obstacle_gap_m':gaps,'max_v':float(np.max(abs(commands[:,0]))),'radius_m':.15})
 bad=run('实际障碍内目标拒绝','client.py','--blocked-goal','--output',w/'nav2-blocked')
 assert bad['plan_status']==6 and bad['path_poses']==0 and bad['command_samples']==0
 import rclpy
 from nav_msgs.msg import OccupancyGrid
 from nav2_msgs.msg import Costmap
 from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy
 from tf2_ros import Buffer,TransformListener,TransformException
 rclpy.init();node=rclpy.create_node('nav_check');buffer=Buffer();listener=TransformListener(buffer,node);seen={}
 qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
 node.create_subscription(OccupancyGrid,'map',lambda m:seen.update(map=m),qos)
 node.create_subscription(Costmap,'/global_costmap/costmap_raw',lambda m:seen.update(costmap=m),qos)
 end=time.monotonic()+5
 while time.monotonic()<end:rclpy.spin_once(node,timeout_sec=.1)
 m=seen['map'];assert (m.info.width,m.info.height)==(60,40) and abs(m.info.resolution-.1)<1e-8
 assert np.array_equal(np.array(m.data).reshape(40,60)==100,occupied)
 record('实际map_server地图',{'frame':m.header.frame_id,'resolution':m.info.resolution,'shape':[60,40],'values':sorted(set(m.data))})
 c=seen['costmap'];assert c.header.frame_id=='map' and 254 in c.data and 253 in c.data
 record('实际全局代价地图',{'frame':c.header.frame_id,'shape':[c.metadata.size_x,c.metadata.size_y],'raw_values':sorted(set(c.data))})
 t=buffer.lookup_transform('map','base_link',rclpy.time.Time());xy=[t.transform.translation.x,t.transform.translation.y]
 assert np.allclose(xy,data['final_xy'],atol=.02)
 record('实际广播TF链',{'map_to_base_xy':xy})
 try:buffer.lookup_transform('map','missing_laser',rclpy.time.Time())
 except TransformException as e:record('实际广播树缺失分支',{'error':type(e).__name__})
 else:raise AssertionError('缺失坐标系竟然存在')
 node.destroy_node();rclpy.shutdown()
finally:
 proc.send_signal(signal.SIGINT)
 try:proc.wait(timeout=8)
 except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=5)
 log.close()
record('制动与延时量级',{'v':2,'a':1,'braking_m':2,'latency_s':.2,'minimum_forward_m_without_margin':2.4})
a.evidence.parent.mkdir(parents=True,exist_ok=True)
versions={pkg:subprocess.check_output(['dpkg-query','-W','-f=${Version}',pkg],text=True) for pkg in ['ros-humble-nav2-bringup','ros-humble-nav2-planner','ros-humble-nav2-controller','libpcl-dev']}
payload={'environment':{'python':sys.version,'versions':versions,'ROS_DOMAIN_ID':188,'discovery':'LOCALHOST'},'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.suffix in ['.py','.yaml','.cpp','.txt']},'records':records}
a.evidence.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'records':len(records),'evidence':str(a.evidence)},ensure_ascii=False))
