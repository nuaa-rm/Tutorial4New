#!/usr/bin/env python3
"""实际运行滤波项目；独立数值、相关性、导数和退化对照。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--project',type=Path,required=True)
cli.add_argument('--work',type=Path,required=True)
cli.add_argument('--evidence',type=Path,required=True)
args=cli.parse_args();args.work.mkdir(parents=True,exist_ok=True)
records=[]
def record(name,data):
    records.append({'name':name,'status':'PASS','details':data})
def run(name,file,*options,fail=False):
    r=subprocess.run([sys.executable,str(args.project/file),*map(str,options)],capture_output=True,text=True,timeout=30)
    assert (r.returncode!=0) if fail else r.returncode==0,r.stderr
    data={'exit':r.returncode,'stderr':r.stderr[-800:]} if fail else json.loads(r.stdout)
    record(name,data);return data
for R in (.9,9):
    out=run('随机游走 R='+str(R),'scalar.py','--r',R)
    K=1.1/(1.1+R);assert abs(out['x']-2*K)<1e-12 and abs(out['P']-(1-K)*1.1)<1e-12
for R in (0,-1,'nan'):run('无效 R '+str(R),'scalar.py','--r',R,fail=True)
for variance,rho in ((3,0),(1,0),(1,1),(1,-.5)):
    out=run('融合方差/相关系数 '+str((variance,rho)),'fusion.py','--v2',variance,'--rho',rho)
    if variance==1 and rho==1:assert out['variance']==1
run('无效相关系数','fusion.py','--rho',1.1,fail=True)
for alpha in (.2,.5,1):
    out=run('因果平滑 '+str(alpha),'smooth.py','--alpha',alpha,'--output',args.work/f'smooth-{alpha}')
    expected={.2:11,.5:4,1:1}[alpha];assert out['step90_samples']==expected
run('无效平滑系数','smooth.py','--alpha',0,fail=True)
run('无效窗口','smooth.py','--window',0,fail=True)
out=run('无迹重建与非线性边界','moments_demo.py')
assert abs(out['sample_mean']-1/3)<.003 and abs(out['sample_variance']-19/45)<.003
for mode in ('linear','range'):
    for tag,options in (('default',[]),('q0',['--q',0]),('r10',['--r',.4]),
                        ('drops',['--drop-every',5]),('bias',['--bias',.5]),('alpha',['--alpha',.3]),
                        ('dt',['--dt',.05]),('seed',['--seed',2026])):
        out=run(mode+' '+tag,'run.py','--mode',mode,'--output',args.work/(mode+'-'+tag),*options)
        assert out['minimum_covariance_eigenvalue']>0
        if mode=='linear':assert out['max_state_difference']<1e-9
        if tag=='drops':assert out['dropped']==30
run('dt=0 被拒绝','run.py','--dt',0,fail=True)
run('负 Q 被拒绝','run.py','--q',-1,fail=True)
run('无效 sigma 缩放','run.py','--alpha',0,fail=True)
sys.path.insert(0,str(args.project))
from linear import predict,update,covariance
from sigma import sigma_points,moments
from smooth import low_pass,moving_average
P=np.array([[2.,.4],[.4,1.]])
F=np.array([[1.,.1],[0,1.]])
x=np.array([4.,1.]);H=np.eye(2);R=np.array([[3.,.2],[.2,2.]])
prior,C=predict(x,P,F,np.eye(2)*.01)
estimate,Cpost,innov,S=update(prior,C,np.array([9.,2.]),H,R)
K=C@np.linalg.inv(C+R)
assert np.allclose(estimate,prior+K@innov)
assert np.allclose(Cpost,(np.eye(2)-K)@C)
record('二维相关矩阵更新独立核对',{'state':estimate.tolist(),'P':Cpost.tolist(),'K':K.tolist()})
for alpha in (1.,.3,.01):
    points,wm,wc=sigma_points(x,P,alpha)
    mean,C=moments(points,wm,wc)
    assert np.allclose(mean,x) and np.allclose(C,P)
    record('非对角协方差 sigma 重建 '+str(alpha),{'mean':mean.tolist(),'P':C.tolist(),'weights_mean_sum':float(wm.sum())})
try:sigma_points(x,np.array([[1.,2.],[2.,1.]]))
except ValueError as error:record('非半正定 P 被拒绝',str(error))
else:raise AssertionError('错误协方差未拒绝')
try:sigma_points(x,np.zeros((2,2)))
except np.linalg.LinAlgError as error:record('奇异 P 不静默修补',str(error))
else:raise AssertionError('奇异矩阵没有报错')
try:sigma_points(x,P,kappa=-2)
except ValueError as error:record('n+lambda 非正被拒绝',str(error))
else:raise AssertionError('错误缩放未拒绝')
for p in (0.,1.,5.):
    h=lambda t:np.hypot(t,2)
    numeric=(h(p+1e-5)-h(p-1e-5))/2e-5
    analytic=p/h(p);assert abs(numeric-analytic)<1e-8
    record('观测雅可比独立差分 '+str(p),{'analytic':analytic,'difference':numeric})
short=np.array([9.,11.,9.,15.])
assert moving_average(short,4)[-1]==11
assert np.allclose(low_pass([1,1,1],.5),[.5,.75,.875])
record('原教材窗口/阶跃数值',{'moving_last':11.,'low_pass':[.5,.75,.875]})
rng=np.random.default_rng(2026)
a=rng.normal(size=200000);b=rng.normal(size=200000)
independent=(a+b)/2;same=(a+a)/2
assert abs(independent.var()-.5)<.01 and abs(same.var()-1)<.01
record('独立融合与重复同一信息的 Monte Carlo',{'independent_variance':float(independent.var()),
                                                    'same_variance':float(same.var())})
args.evidence.parent.mkdir(parents=True,exist_ok=True)
args.evidence.write_text(json.dumps({'python':sys.version,'numpy':np.__version__,
    'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.project.glob('*.py'))},
    'synthetic':True,'records':records},ensure_ascii=False,indent=2))
print(json.dumps({'records':len(records),'evidence':str(args.evidence)},ensure_ascii=False))
