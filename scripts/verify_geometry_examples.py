#!/usr/bin/env python3
"""几何项目实际运行；独立核对投影、导数、规范自由度与配准。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import cv2
import numpy as np
import scipy
from scipy.linalg import expm

cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument("--project",type=Path,required=True)
cli.add_argument("--work",type=Path,required=True)
cli.add_argument("--evidence",type=Path,required=True)
args=cli.parse_args();args.work.mkdir(parents=True,exist_ok=True)
records=[]
def record(name,data):
    records.append({"name":name,"status":"PASS","details":data})
def run(name,file,*options,fail=False):
    cmd=[sys.executable,str(args.project/file),*map(str,options)]
    r=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
    assert (r.returncode!=0) if fail else r.returncode==0,r.stderr
    data={"exit":r.returncode,"stderr":r.stderr[-700:]} if fail else json.loads(r.stdout)
    record(name,{"command":cmd,"result":data});return data
for file in ("basics.py","numeric_demo.py","jacobian_demo.py","lie_demo.py"):
    run(file,file)
base=run("PnP/DLT/P3P默认","pnp_demo.py")
assert base["pnp"]["rms_pixel"]<1e-8 and base["dlt"]["rms_pixel"]<1e-8
assert 1<=base["p3p_count"]<=4 and min(x["rms_all_points"] for x in base["p3p_candidates"])<1e-3
assert max(x["rms_three_points"] for x in base["p3p_candidates"])<1e-3
assert max(x["rms_extra_points"] for x in base["p3p_candidates"])>10
scaled=run("米到毫米","pnp_demo.py","--scale",1000)
assert abs(scaled["pnp"]["translation"][2]/base["pnp"]["translation"][2]-1000)<1e-8
bad=run("交换对应点","pnp_demo.py","--swap")
assert not bad["pnp"]["positive_depth"] and bad["pnp"]["rms_pixel"] is None
run("观测噪声0.3","pnp_demo.py","--noise",.3)
run("尺度0拒绝","pnp_demo.py","--scale",0,fail=True)
run("负噪声拒绝","pnp_demo.py","--noise",-1,fail=True)
for loop in (2.,2.2):
    graph=run("平移图闭环 "+str(loop),"graph_demo.py","--loop",loop)
    assert graph["rank_fixed"]==2 and graph["rank_unfixed"]==2
for shift in (0,2):
    out=run("真实ICP初值 "+str(shift),"registration_demo.py","--initial-shift",shift)
    assert out["known_max_error"]<1e-10 and out["icp_known_pair_rms"]<1e-10
pose={}
for tag,options in (("default",[]),("clean",["--noise",0]),("outlier",["--outlier",80]),
                    ("robust",["--outlier",80,"--huber",2])):
    pose[tag]=run("位姿优化 "+tag,"pose_demo.py","--output",args.work/("pose-"+tag),*options)
    assert pose[tag]["accepted_cost_nonincreasing"]
assert pose["clean"]["inlier_rms_pixel"]<1e-6
assert pose["robust"]["inlier_rms_pixel"]<pose["outlier"]["inlier_rms_pixel"]/10
bundle={}
for tag,options in (("default",[]),("clean",["--noise",0]),("outlier",["--outlier",80]),
                    ("robust",["--outlier",80,"--loss","huber"])):
    bundle[tag]=run("三相机联合BA "+tag,"bundle_demo.py","--output",args.work/("bundle-"+tag),*options)
    assert bundle[tag]["variables"]==71 and bundle[tag]["jacobian_rank"]==71
    assert bundle[tag]["schur_max_difference"]<1e-8
assert bundle["clean"]["final_rms_pixel"]<1e-8 and bundle["clean"]["point_rmse_m"]<1e-8
run("负Huber拒绝","pose_demo.py","--huber",-1,fail=True)
sys.path.insert(0,str(args.project))
from model import pose as make_pose,project,transform,sample,K
from lie import exp3,exp6,hat,left_jacobian
from dlt import solve,rotation_projection
from residual import jacobians
from registration_demo import rigid,icp
for phi in ([0.,0,0],[1e-8,0,0],[.3,-.2,.1],[0.,0,np.pi]):
    phi=np.array(phi);R=exp3(phi)
    assert np.allclose(R,expm(hat(phi)),atol=1e-13)
    assert np.allclose(R.T@R,np.eye(3)) and abs(np.linalg.det(R)-1)<1e-12
    record("SO3独立矩阵指数 "+str(phi.tolist()),{"max_error":float(np.max(abs(R-expm(hat(phi)))))})
xi=np.array([1.,.2,-.3,.3,-.2,.1])
W=np.zeros((4,4));W[:3,:3]=hat(xi[3:]);W[:3,3]=xi[:3]
assert np.allclose(exp6(xi),expm(W),atol=1e-13)
record("SE3独立矩阵指数",exp6(xi).tolist())
points=sample();T=make_pose([.1,-.05,.03],[.2,.1,.3])
dist=np.array([-.1,.01,.002,-.001,0.])
uv=cv2.projectPoints(points,cv2.Rodrigues(T[:3,:3])[0],T[:3,3],K,dist)[0].reshape(-1,2)
estimated=solve(points,uv,K,dist)
assert np.allclose(estimated,T,atol=1e-7)
record("DLT先去畸变",{"transform_max_error":float(np.max(abs(estimated-T)))})
planar=points.copy();planar[:,2]=3.
try:solve(planar,project(planar,T),K)
except ValueError as error:record("共面DLT明确拒绝",str(error))
else:raise AssertionError("共面输入未拒绝")
try:project(np.array([[1.,2.,0.]]),np.eye(4))
except ValueError as error:record("零深度拒绝",str(error))
else:raise AssertionError("零深度未拒绝")
for p in ([0.,0.,-1.],[0.,0.,float("nan")]):
    try:project(np.array([p]),np.eye(4))
    except ValueError as error:record("无效投影拒绝 "+str(p),str(error))
    else:raise AssertionError("错误投影未拒绝")
# 未固定坐标/尺度的完整BA雅可比：78变量，7个规范自由度。
poses=[np.eye(4),make_pose([.01,.02,0],[-.3,0,0]),make_pose([-.02,.03,.01],[-.6,.05,.02])]
J=np.zeros((120,78))
for i,T in enumerate(poses):
    for k,p in enumerate(points):
        a,b=jacobians(p,T);row=2*(i*20+k)
        J[row:row+2,i*6:i*6+6]=a;J[row:row+2,18+k*3:18+k*3+3]=b
rank=int(np.linalg.matrix_rank(J));assert rank==71
record("BA未固定规范的秩",{"variables":78,"rank":rank,"nullity":78-rank})
G=make_pose([.2,.1,-.1],[.4,-.1,.2]);changed=transform(points,G)
error=max(np.max(abs(project(changed,T@np.linalg.inv(G))-project(points,T))) for T in poses)
assert error<1e-10
scaled_points=points*2
scale_error=0.
for T in poses:
    S=T.copy();S[:3,3]*=2
    scale_error=max(scale_error,float(np.max(abs(project(scaled_points,S)-project(points,T)))))
assert scale_error<1e-10
record("整体坐标/尺度图像不变",{"frame_max_error":float(error),"scale_max_error":scale_error})
line=np.column_stack([np.arange(5.),np.zeros((5,2))])
try:rigid(line,line)
except ValueError as error:record("共线配准明确拒绝",str(error))
else:raise AssertionError("共线退化未拒绝")
cube=np.array([[x,y,z] for x in (-1.,1.) for y in (-1.,1.) for z in (-1.,1.)])
ambiguous,history=icp(cube,cube,make_pose([0,0,np.pi/2],[0,0,0]))
nearest=float(np.sqrt(history[-1]))
pairs=float(np.sqrt(np.mean(np.sum((transform(cube,ambiguous)-cube)**2,axis=1))))
assert nearest<1e-10 and pairs>1
record("对称点云最近邻不等于标签配对",{"nearest_rms":nearest,"known_pair_rms":pairs})
original=np.array([[0.,0,0],[1.,0,0],[0.,1,0]])
target=transform(original,make_pose([0.,0,np.pi/2],[1.,2.,3.]))
shift=target.mean(axis=0)-original.mean(axis=0)
cost=float(np.sum((original+shift-target)**2))
fit=rigid(original,target)
assert np.allclose(shift,[1/3,2,3]) and abs(cost-8/3)<1e-12
assert np.allclose(transform(original,fit),target)
record("原三点质心差与完整配准",{"translation_only":shift.tolist(),
    "squared_sum":cost,"rigid_translation":fit[:3,3].tolist()})
# 原文标量最小二乘的正常/异常结果。
x=np.array([0.,1.,2.])
for y,expected in ((np.array([2.,3.,4.]),2.),(np.array([2.,3.,10.]),4.)):
    t=float(np.mean(y-x));assert t==expected
    record("原标量最小二乘 "+str(t),{"t":t,"squared_sum":float(np.sum((x+t-y)**2))})
args.evidence.parent.mkdir(parents=True,exist_ok=True)
args.evidence.write_text(json.dumps({"python":sys.version,"opencv":cv2.__version__,"numpy":np.__version__,
    "scipy":scipy.__version__,"synthetic":True,"source_sha256":{
        p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.project.glob("*.py"))},
    "records":records},ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"records":len(records),"evidence":str(args.evidence)},ensure_ascii=False))
