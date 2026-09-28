#!/usr/bin/env python3
"""复现深度学习章节；可复用本次已跑完的 CPU/GPU 记录，避免无变化重训。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'02-专项技术栈/examples/dl/lenet-training-demo'


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--data',type=Path,required=True)
    cli.add_argument('--cpu-run',type=Path)
    cli.add_argument('--cpu-log',type=Path)
    cli.add_argument('--gpu-python',type=Path,required=True)
    cli.add_argument('--gpu-run',type=Path)
    cli.add_argument('--gpu-log',type=Path)
    args=cli.parse_args()
    records=[]
    def record(step,detail):
        records.append({'step':step,**detail})
    def run(step,command,cwd,expected=0):
        r=subprocess.run([str(x) for x in command],cwd=cwd,text=True,
                         stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
        record(step,{'command':[str(x) for x in command],
                     'returncode':r.returncode,'output':r.stdout})
        assert r.returncode==expected,(step,r.stdout)
        return r.stdout
    with tempfile.TemporaryDirectory(prefix='dl-textbook-') as temp:
        work=Path(temp);lab=work/'lab';shutil.copytree(PROJECT,lab)
        sha={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in PROJECT.glob('*.py')}
        record('source',{'sha256':sha})
        import numpy as np
        import torch
        import torchvision
        from torch import nn
        from torch.utils.data import DataLoader,TensorDataset
        assert torch.__version__=='2.6.0+cpu'
        assert torchvision.__version__=='0.21.0+cpu'
        record('environment',{'python':sys.version,'executable':sys.executable,
            'torch':torch.__version__,'torchvision':torchvision.__version__,
            'numpy':np.__version__})
        run('unactivated-environment',['python3','-c',
            'import sys,torch; print(sys.executable,torch.__version__)'],lab,1)
        for name in ('fit','ops','model','loss','grad','mode','nms'):
            out=run(name,[sys.executable,f'{name}_demo.py' if name!='model' else 'model.py'],lab)
            if name=='ops':assert '19.0, 25.0, 37.0, 43.0' in out
            if name=='model':assert '(2, 16, 4, 4)' in out and '(2, 10)' in out
            if name=='grad':assert '-16.0' in out and '-32.0' in out and '1.6000' in out
            if name=='nms':assert '[0, 2]' in out
        def variant(name,file,before,after,expected=0):
            folder=work/name;shutil.copytree(lab,folder)
            p=folder/file;s=p.read_text();assert before in s;p.write_text(s.replace(before,after))
            return run(name,[sys.executable,file],folder,expected)
        out=variant('fit-no-noise','fit_demo.py',
            'np.array([0., .15, -.2, .15, 0.])','np.zeros(5)')
        lines=out.splitlines()
        assert float(lines[1].split()[-1])<1e-20 and float(lines[2].split()[-1])<1e-20
        out=variant('pool-stride2','ops_demo.py','pool2d(x, 2, 1)','pool2d(x, 2, 2)')
        assert "最大池化 [4.0]" in out and "平均池化 [2.0]" in out
        out=variant('conv-ones','ops_demo.py',
            'torch.tensor([[[[0., 1.], [2., 3.]]]])','torch.ones(1,1,2,2)')
        assert '8.0, 12.0, 20.0, 24.0' in out
        out=variant('grad-lr005','grad_demo.py','lr=0.1','lr=0.05')
        assert '0.8000' in out and '5.7600' in out
        out=variant('dropout-zero','mode_demo.py','p=0.5','p=0.0')
        assert [line.split()[-1] for line in out.splitlines()]==['False','True','False']
        out=variant('nms08','nms_demo.py','iou_threshold=0.5','iou_threshold=0.8')
        assert '[0, 1, 2]' in out
        folder=work/'shape32';shutil.copytree(lab,folder)
        p=folder/'model.py';s=p.read_text().replace('torch.zeros(2, 1, 28, 28)','torch.zeros(2, 1, 32, 32)');p.write_text(s)
        out=run('shape32-error',[sys.executable,'model.py'],folder,1)
        assert '(2, 16, 5, 5)' in out and '(2, 400)' in out and 'mat1 and mat2' in out
        p.write_text(s.replace('nn.Linear(256, 120)','nn.Linear(400, 120)'))
        out=run('shape32-fixed',[sys.executable,'model.py'],folder)
        assert '(2, 10)' in out
        sys.path.insert(0,str(lab))
        from data import loaders
        from model import LeNet
        from engine import run_epoch
        train,valid,test=loaders(str(args.data),50,128)
        sizes=[len(y) for _,y in train]
        assert sizes==[50,50,28] and len(valid.dataset)==5000 and len(test.dataset)==10000
        assert not (set(train.dataset.dataset.indices)&set(valid.dataset.indices))
        x,y=next(iter(train))
        assert tuple(x.shape)==(50,1,28,28) and tuple(LeNet()(x).shape)==(50,10)
        record('data-split-batches',{'sizes':sizes,'valid':len(valid.dataset),'test':len(test.dataset)})
        scores=torch.tensor([[0.,0.],[2.,0.],[10.,0.]])
        labels=torch.tensor([0,1,0])
        net=nn.Identity()
        result=run_epoch(net,DataLoader(TensorDataset(scores,labels),batch_size=2),
                         nn.CrossEntropyLoss(),'cpu')
        target=nn.CrossEntropyLoss()(scores,labels).item()
        assert abs(result['loss']-target)<1e-6 and result['samples']==3
        record('unequal-batch-weighting',{'actual':result,'full_sample_mean':target})
        if args.cpu_run:
            assert args.cpu_log
            cpu=args.cpu_run
            out=args.cpu_log.read_text()
            record('full-cpu-training',{'command':[sys.executable,'train.py','--data',str(args.data),'--epochs','3','--out',str(cpu)],'returncode':0,'output':out,'reuse':'本次已完成同一源码运行'})
        else:
            cpu=lab/'runs'
            run('full-cpu-training',[sys.executable,'train.py','--data',args.data,'--epochs','3','--out',cpu],lab)
        metrics=json.loads((cpu/'metrics.json').read_text())
        assert metrics['epochs']==3 and metrics['train_limit']==0
        assert [r['train']['samples'] for r in metrics['history']]==[55000]*3
        assert [r['valid']['samples'] for r in metrics['history']]==[5000]*3
        assert metrics['test']['samples']==10000 and 0<=metrics['test']['accuracy']<=1
        record('full-metrics',{'metrics':metrics,'checkpoint_sha256':hashlib.sha256((cpu/'best.pth').read_bytes()).hexdigest()})
        if cpu!=lab/'runs':shutil.copytree(cpu,lab/'runs')
        out=run('independent-inference',[sys.executable,'infer.py','--data',args.data,'--index','0','1','2','9999'],lab)
        predictions=[json.loads(line) for line in out.splitlines()]
        assert len(predictions)==4 and all(len(r['scores'])==10 for r in predictions)
        run('invalid-index',[sys.executable,'infer.py','--data',args.data,'--index','10000'],lab,2)
        bad=work/'bad-load';shutil.copytree(lab,bad)
        p=bad/'model.py';p.write_text(p.read_text().replace('nn.Linear(256, 120)','nn.Linear(400, 120)'))
        out=run('incompatible-weights',[sys.executable,'infer.py','--data',args.data],bad,1)
        assert 'size mismatch' in out
        from infer import load_model
        original,_=load_model(lab/'runs/best.pth')
        saved=torch.load(lab/'runs/best.pth',map_location='cpu',weights_only=True)
        assert saved['mean']==0.1307 and saved['std']==0.3081
        restored=LeNet().eval();restored.load_state_dict(saved['state'])
        with torch.no_grad():torch.testing.assert_close(original(x),restored(x),rtol=0,atol=0)
        record('reload-exact',{'batch':50,'max_error':0,'architecture':saved['architecture']})
        saved['architecture']='wrong'
        torch.save(saved,lab/'runs/wrong.pth')
        out=run('wrong-architecture',[sys.executable,'infer.py','--data',args.data,'--checkpoint','runs/wrong.pth'],lab,1)
        assert '模型结构或类别表不匹配' in out
        run('bad-epochs',[sys.executable,'train.py','--epochs','0'],lab,2)
        run('cpu-cuda-request',[sys.executable,'train.py','--device','cuda'],lab,2)
        run('batch50-smoke',[sys.executable,'train.py','--data',args.data,
            '--train-limit','128','--batch-size','50','--epochs','1','--out',work/'smoke50'],lab)
        run('benchmark',[sys.executable,'benchmark.py'],lab)
        out=variant('benchmark8','benchmark.py','(1, 32)','(1, 8)')
        assert '8 每批ms' in out
        for index in (0,1,2):
            out=run(f'onnx-compare-{index}',[sys.executable,'export_compare.py','--data',args.data,
                       '--index',str(index),'--output',f'runs/lenet{index}.onnx'],lab)
            result=json.loads(out.splitlines()[-1]);assert result['shape']==[1,10]
        import onnxruntime as ort
        options=ort.SessionOptions();options.intra_op_num_threads=1
        session=ort.InferenceSession(str(lab/'runs/lenet0.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
        for shape in ((8,1,28,28),(1,1,32,32)):
            try:session.run(None,{'image':np.zeros(shape,dtype=np.float32)})
            except ort.capi.onnxruntime_pybind11_state.InvalidArgument as e:
                record('onnx-fixed-input-reject',{'shape':list(shape),'error':str(e)})
            else:raise AssertionError(shape)
        run('gpu-environment',[args.gpu_python,'-c',
            'import torch; print(torch.__version__,torch.version.cuda,torch.cuda.is_available(),torch.cuda.get_device_name(0))'],lab)
        run('gpu-equivalence',[args.gpu_python,'device_demo.py'],lab)
        if args.gpu_run:
            assert args.gpu_log
            gpu=args.gpu_run
            record('gpu-training',{'command':[str(args.gpu_python),'train.py','--data',str(args.data),'--epochs','1','--train-limit','128','--device','cuda','--out',str(gpu)],'returncode':0,'output':args.gpu_log.read_text(),'reuse':'本次已完成同一源码运行'})
        else:
            gpu=work/'gpu'
            run('gpu-training',[args.gpu_python,'train.py','--data',args.data,'--epochs','1',
                '--train-limit','128','--device','cuda','--out',gpu],lab)
        gm=json.loads((gpu/'metrics.json').read_text())
        assert gm['device']=='cuda' and gm['history'][0]['train']['samples']==128
        record('gpu-metrics',{'metrics':gm})
        run('gpu-weights-on-cpu',[sys.executable,'infer.py','--data',args.data,
            '--checkpoint',gpu/'best.pth','--index','0'],lab)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps({'scope':'真实 MNIST/CPU完整三轮/CUDA小规模训练/ONNX CPU；非赛场模型',
            'records':records},ensure_ascii=False,indent=2)+'\n')
        print(f'{len(records)} 条记录通过；完整CPU测试准确率 {metrics["test"]["accuracy"]}')


if __name__=='__main__':main()
