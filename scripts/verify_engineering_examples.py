#!/usr/bin/env python3
"""实际基线/失败/回滚与独立判据核对，不代替第二人签认或实车。"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--project',type=Path,required=True);c.add_argument('--work',type=Path,required=True);c.add_argument('--evidence',type=Path,required=True);a=c.parse_args();p=a.project.resolve();w=a.work.resolve();w.mkdir(parents=True,exist_ok=True);records=[];runs={}
def rec(name,data):records.append({'name':name,'status':'PASS','details':data})
for name,limit,passed,source,age in [('baseline',100,True,'vision',50),('trial',200,False,'radio',150),('rollback',100,True,'vision',50)]:
 cmd=[sys.executable,str(p/'run.py'),'--radio-limit',str(limit),'--record',str(w/f'{name}.json')];output=json.loads(subprocess.check_output(cmd,text=True));data=json.loads((w/f'{name}.json').read_text());assert output['passed']==data['passed']==passed and output['source']==source and output['age_ms']==age
 assert data['fixed']=={'now_ms':1000,'vision_limit_ms':150,'required_max_age_ms':100}
 assert data['passed']==(0<=1000-data['observations']['sample_ms']<=100)
 for f,value in data['source_sha256'].items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==value
 runs[name]=data;rec('独立进程 '+name,{'command':cmd,'stdout':output,'raw_record':data,'record_sha256':hashlib.sha256((w/f'{name}.json').read_bytes()).hexdigest()})
assert runs['baseline']==runs['rollback'];assert runs['baseline']['input_sha256']==runs['trial']['input_sha256'] and runs['baseline']['source_sha256']==runs['trial']['source_sha256'] and runs['baseline']['fixed']==runs['trial']['fixed']
rec('单变量与回滚独立核对',{'variable_changes':[100,200,100],'same_input':True,'same_sources':True,'same_fixed_criterion':True,'baseline_equals_rollback':True,'boundary':'脚本独立计算，不是第二个人签认'})
cmd=[sys.executable,str(p/'run.py'),'--radio-limit','-1','--record',str(w/'invalid.json')];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==2 and not (w/'invalid.json').exists();rec('无效试验参数拒绝',{'command':cmd,'stderr':r.stderr})
review={'conclusion':'放宽后确实选中无线电，但年龄150ms违反固定100ms条件，试验失败；回滚后视觉50ms且源/输入一致。','earliest_observation':'无线电采样时刻850与当前1000；选源前已经150ms','next':'现场尚未测量；保持原配置，不据此放宽赛场参数','roles':{'复核人':'待真实同学复核','版本/输入/判据':'记录原始JSON与SHA，不填写虚构签认'}}
(w/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n');rec('填写失败与下一步记录',review)
plan={'direction':'雷达坐标变旧','hypothesis':'发送队列积压','earliest':'入队与发出时刻/队列长度','single_variable':'仅坐标改为保留最新值，事件通道保持独立','same_input':'实际原录包/版本待提供','criterion':'先约定可接受年龄与有效目标损失，再同输入对照','rollback':'错误覆盖事件或时效/有效性恶化即恢复基线','status':'计划，尚未执行真实链路'};rec('开放任务计划产物',plan)
a.evidence.parent.mkdir(parents=True,exist_ok=True);a.evidence.write_text(json.dumps({'python':platform.python_version(),'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file() and f.name!='.gitignore'},'records':records,'boundaries':['人工消息的软件实验，不是实车/靶场/对抗验证','本次按用户要求自行安排分进程运行与独立脚本复核；未伪造第二人签认，学员双人现场验收仍保留']},ensure_ascii=False,indent=2)+'\n');print(len(records),'records passed',a.evidence)
