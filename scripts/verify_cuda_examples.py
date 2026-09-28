#!/usr/bin/env python3
"""实际重放 CUDA 章节，预期错误与正常程序分开判断。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '02-专项技术栈/examples/cuda/vector-lab-demo'


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--toolkit', type=Path, default=Path('/usr/local/cuda-12.6'))
    cli.add_argument('--arch', default='86')
    args = cli.parse_args()
    records = []
    def run(step, command, cwd=None, expected=0, env=None):
        p = subprocess.run([str(x) for x in command], cwd=cwd, env=env,
                           capture_output=True, text=True, timeout=120)
        records.append({'step': step, 'command': [str(x) for x in command],
                        'returncode': p.returncode, 'output': p.stdout+p.stderr})
        assert p.returncode == expected, records[-1]
        print(step, flush=True)
        return p.stdout+p.stderr
    records.append({'step': 'source', 'sha256': {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in SOURCE.iterdir() if p.is_file()}})
    run('environment', ['bash', '-lc', 'cat /etc/os-release; g++ --version; cmake --version; nvidia-smi'])
    run('packages', ['dpkg-query','-W','cuda-keyring','cuda-compiler-12-6','cuda-cudart-dev-12-6','cuda-sanitizer-12-6'])
    run('nvcc', [args.toolkit/'bin/nvcc', '--version'])
    with tempfile.TemporaryDirectory(prefix='textbook-cuda-verify-') as temporary:
        temp = Path(temporary)
        source, build = temp/'src', temp/'build'
        shutil.copytree(SOURCE, source, ignore=shutil.ignore_patterns('build*'))
        run('configure', ['cmake','-S',source,'-B',build,'-DCMAKE_BUILD_TYPE=Release',
             f'-DCMAKE_CUDA_COMPILER={args.toolkit}/bin/nvcc',f'-DCMAKE_CUDA_ARCHITECTURES={args.arch}'])
        run('build', ['cmake','--build',build,'-j2'])
        out=run('cpu', [build/'cpu_demo'])
        assert all(s in out for s in ('阈值=0 前缀和=1','阈值=255 前缀和=8','阈值=0 前缀和=10','阈值=255 前缀和=18'))
        run('direct-cpu-build',['g++','-std=c++17',source/'cpu_demo.cpp','-o',temp/'cpu-direct'])
        run('direct-cpu-run',[temp/'cpu-direct'])
        variant=temp/'cpu-variant.cpp'
        variant.write_text((source/'cpu_demo.cpp').read_text().replace('x{1, 7, 2, 8}','x{2, 4, 6, 8}'))
        run('cpu-variant-build',['g++','-std=c++17',variant,'-o',temp/'cpu-variant'])
        out=run('cpu-variant',[temp/'cpu-variant'])
        assert all(s in out for s in ('阈值=0 前缀和=2','阈值=0 前缀和=6','阈值=255 前缀和=12','阈值=255 前缀和=20'))
        out=run('device', [build/'device_info'])
        assert 'compute=8.6' in out and 'runtime=12060' in out
        run('direct-nvcc', [args.toolkit/'bin/nvcc','-O2','-std=c++17',
            f'-arch=sm_{args.arch}','-lineinfo',source/'vec_add.cu','-o',temp/'direct'])
        out=run('direct-run',[temp/'direct',257,256])
        assert '跳过线程=255' in out and '全部结果通过' in out
        out=run('vec-default',[build/'vec_add'])
        assert 'n=1048579' in out and 'blocks=4097' in out
        for n,t in [(1,1),(10,4),(257,128),(257,256),(513,256),(4096,256),(1048579,512)]:
            out=run(f'vec-{n}-{t}',[build/'vec_add',n,t])
            blocks=(n+t-1)//t
            assert f'blocks={blocks} 跳过线程={blocks*t-n}' in out and f'设备数组字节={12*n}' in out
        for n,t in [(1,32),(257,128),(513,256),(4096,256),(1048579,512)]:
            out=run(f'sum-{n}-{t}',[build/'shared_sum',n,t])
            expected=sum(i%8 for i in range(n))
            assert f'sum={expected} CPU={expected}' in out
        for executable, params in [('vec_add',['0']),('vec_add',['257','1025']),
                ('vec_add',['abc']),('shared_sum',['513','255']),
                ('pipeline',['257','2']),('pipeline',['257','0'])]:
            run('invalid-args',[build/executable,*params],expected=2)
        sanitizer=args.toolkit/'bin/compute-sanitizer'
        for tool,executable,params in [('memcheck','vec_add',[257,256]),
                ('memcheck','shared_sum',[513,256]),('racecheck','shared_sum',[513,256]),
                ('synccheck','shared_sum',[513,256])]:
            out=run(tool,[sanitizer,'--tool',tool,'--error-exitcode',9,build/executable,*params])
            assert '0 errors' in out
        out=run('launch-error',[build/'error_demo','launch'],expected=1)
        assert 'invalid configuration argument' in out and '继续检查执行' not in out
        out=run('execution-error',[build/'error_demo','execute'],expected=1)
        assert '继续检查执行' in out and 'device-side assert triggered' in out
        out=run('memory-error',[sanitizer,'--tool','memcheck','--error-exitcode',9,
                build/'error_demo','memory'],expected=9)
        assert 'Invalid __global__ write' in out and re.search(r'ERROR SUMMARY: [1-9][0-9]* errors',out)
        run('recovery-new-process',[build/'vec_add',257,256])
        hidden=dict(os.environ,CUDA_VISIBLE_DEVICES='')
        out=run('hidden-device',[build/'device_info'],env=hidden,expected=1)
        assert 'no CUDA-capable device is detected' in out
        out=run('hidden-manager',['nvidia-smi','--query-gpu=name','--format=csv,noheader'],env=hidden)
        assert 'RTX 3070 Ti' in out
        run('hidden-cpu',[build/'cpu_demo'],env=hidden)
        run('restored-device',[build/'device_info'])
        for n,repeats in [(257,3),(1048579,7),(513,5)]:
            out=run(f'pipeline-{n}',[build/'pipeline',n,repeats])
            data=json.loads(out)
            assert data['all_checked'] and data['resident_bytes']==8*n and data['roundtrip_bytes']==24*n
            assert all(data[k]>0 for k in ('cpu_ms','kernel_ms','resident_ms','roundtrip_ms'))
            records.append({'step':'timing','data':data})
        # 检查共享内存冲突工具确实能发现去掉屏障的错误变体。
        broken=temp/'broken'
        shutil.copytree(source,broken)
        p=broken/'kernels.cuh'
        p.write_text(p.read_text().replace('    __syncthreads();\n',''))
        run('broken-shared-build',[args.toolkit/'bin/nvcc','-O2','-std=c++17',
            f'-arch=sm_{args.arch}','-lineinfo',broken/'shared_sum.cu','-o',temp/'broken-sum'])
        p=subprocess.run([str(sanitizer),'--tool','racecheck','--error-exitcode','9',
            str(temp/'broken-sum'),'513','256'],capture_output=True,text=True,timeout=120)
        output=p.stdout+p.stderr
        assert p.returncode!=0 and re.search(r'Race|race|hazard',output), (p.returncode,output)
        records.append({'step':'missing-barrier-racecheck','returncode':p.returncode,'output':output})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'scope':'actual Ubuntu CUDA CPU/GPU/negative cases','records':records},
                                     ensure_ascii=False,indent=2)+'\n')
    print(f'通过 {len(records)} 条记录')


if __name__=='__main__':main()
