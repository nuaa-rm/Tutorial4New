#!/usr/bin/env python3
"""实测 SDR 离线流程、参数与拒收；硬件模拟单列，不当 RX 实机验收。"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parents[1] / '02-专项技术栈/examples/sdr/iq-replay-demo'
records = []


def run(command, folder, expected=0):
    result = subprocess.run(command, cwd=folder, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=20)
    records.append({'command': command, 'returncode': result.returncode, 'output': result.stdout})
    print(f'{len(records)}: {command[:2]} -> {result.returncode}', flush=True)
    assert result.returncode == expected, result.stdout
    return result.stdout


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--hardware-python', type=Path, required=True)
    args = cli.parse_args()
    with tempfile.TemporaryDirectory(prefix='sdr-textbook-') as temp:
        folder = Path(temp) / 'demo'
        shutil.copytree(SOURCE, folder)
        run(['python3', '-c', 'import sys,numpy;print(sys.version);print(numpy.__version__)'], folder)
        run(['python3', 'tone_demo.py'], folder)
        run(['python3', 'state_demo.py'], folder)
        run(['python3', 'replay.py', 'generate', 'good'], folder)
        out = run(['python3', 'replay.py', 'decode', 'good'], folder)
        assert '同步起点: 19' in out and "'x_m': 1.25" in out
        for label, options, x in [('pi', ['--phase', '3.141592653589793'], '1.25'),
                                 ('x', ['--x-mm', '2000'], '2.0'),
                                 ('mixed', ['--phase', '-1.2', '--offset-hz', '-125', '--x-mm', '3000'], '3.0')]:
            run(['python3', 'replay.py', 'generate', label] + options, folder)
            out = run(['python3', 'replay.py', 'decode', label], folder)
            assert '同步起点: 19' in out and "'x_m': " + x in out
        run(['python3', 'replay.py', 'generate', 'bad', '--corrupt'], folder)
        assert 'CRC 失败' in run(['python3', 'replay.py', 'decode', 'bad'], folder, expected=1)
        original = (folder / 'tone_demo.py').read_text()
        variant = original.replace('fs, count = 8000, 32', 'fs, count = 16000, 32')
        variant = variant.replace('2j * np.pi * 1000 * n / fs', '2j * np.pi * (-7000) * n / fs')
        (folder / 'tone_demo.py').write_text(variant)
        assert '-2.748894' in run(['python3', 'tone_demo.py'], folder)
        (folder / 'tone_demo.py').write_text(original)
        run(['python3', '-c', '''from synth import synthesize
from decode import decode
import numpy as np
cases=0
for prefix in [0,1,7,19,23]:
 for phase in [-3.14159,-1.2,0,.7,3.14159]:
  for offset in [-125,0,125]:
   iq,meta=synthesize(3000,phase,offset,.1,prefix)
   fields,detail=decode(iq,meta)
   assert detail['start']==prefix and fields['x_m']==3.0
   cases+=1
print(cases,'组前置长度/相位/已知频偏变体通过')'''], folder)
        run(['python3', '-c', '''from record import *
from synth import synthesize
from decode import decode
from frame import *
import json
import numpy as np
from pathlib import Path

def rejected(function, word):
 try: function()
 except ValueError as e: assert word in str(e),str(e)
 else: raise AssertionError(word)

iq,meta=synthesize()
rejected(lambda:decode(iq[:639],meta),'不足')
rejected(lambda:decode(iq*.1,meta),'太弱')
rejected(lambda:decode(iq,dict(meta,known_offset_hz=0)),'前导')
rejected(lambda:decode(iq,dict(meta,samples_per_symbol=0)),'正整数')
rejected(lambda:parse_frame(b'abc'),'长度')
body=bytes([2])+make_frame()[1:-2]
unknown=body+binascii.crc_hqx(body,0).to_bytes(2,'big')
rejected(lambda:parse_frame(unknown),'未知命令')
save_record('check',iq,meta)
path=Path('check/metadata.json');original=path.read_text()
for update in [dict(sample_count=669),dict(dtype='>c8'),dict(sample_rate_hz=0)]:
 m=json.loads(original);m.update(update);path.write_text(json.dumps(m))
 rejected(lambda:load_record('check'),'不符' if 'sample_rate_hz' not in update else '无效')
path.write_text(original)
data=Path('check/iq.npy');raw=data.read_bytes();data.write_bytes(raw[:-1])
rejected(lambda:load_record('check'),'哈希')
iq[0]=np.nan+0j;save_record('nan',iq,meta)
rejected(lambda:load_record('nan'),'无效')
print('截断、弱前导、错误频偏、无效sps、长度/命令、元数据、哈希及NaN拒收通过')'''], folder)
        run(['python3', '-c', '''from synth import synthesize
from decode import decode
from frame import PREAMBLE
import numpy as np
iq,meta=synthesize(phase=np.pi)
fields,details=decode(iq,meta)
count=len(PREAMBLE)*8;start=details['start']
means=details['corrected'][start:start+count].reshape(-1,8).mean(axis=1)
assert np.array_equal((means.real<0).astype(np.uint8),1-PREAMBLE)
assert fields['x_m']==1.25
print('跳过相位补偿前导全部翻转，完整解码保持正确')'''], folder)
        run(['python3', '-c', '''from state_demo import *
s=Stages();actual=[s.handle(e)[:2] for e in ['ok1','reset','ok2','ok1','ok2']]
assert actual==[('level2',1),('level1',2),('level1',2),('level2',3),('information',4)]
s=Stages();assert s.handle('reset')[:2]==('level1',1)
assert select_source(10,[('radio',10.1,(1,2)),('vision',9.9,(3,4))])[0]=='vision'
assert select_source(10,[('radio',10.1,(1,2)),('vision',9,(3,4))]) is None
assert select_source(20,[('radio',19.75,(1,2))],.25)[0]=='radio'
assert select_source(20,[('radio',19.6,(1,2)),('vision',19.9,(3,4))],.25)[0]=='vision'
assert select_source(10,[('radio',9.9,(1,2)),('vision',9.9,(3,4))])[0]=='radio'
print('练习序列、初始复位、未来时间、过期、阈值等于与优先级通过')'''], folder)
        run([str(args.hardware_python), '-c', 'import adi,iio;print(adi.__version__,iio.version)'], folder)
        run([str(args.hardware_python), 'capture_pluto.py', '--help'], folder)
        run(['iio_info', '--help'], folder)
        out=run(['iio_info', '-S', 'usb'], folder, expected=1)
        assert 'No IIO context found' in out
        run(['python3', '-c', '''# 仅测试调用关系，不伪装真实硬件。
import sys,types
import numpy as np
from capture_pluto import capture
from record import load_record
class Fake:
 def __init__(self,uri): self.uri=uri;self.destroyed=False;self.fail=False
 def rx(self):
  if self.fail: raise OSError('模拟读取失败')
  return np.ones(4096,dtype=np.complex128)*(3+4j)
 def rx_destroy_buffer(self): self.destroyed=True
fake=Fake('mock');sys.modules['adi']=types.SimpleNamespace(Pluto=lambda uri:fake)
capture('mock',2400000000,'mock')
iq,meta=load_record('mock')
assert fake.destroyed and fake.sample_rate==1000000 and fake.rx_lo==2400000000
assert fake.rx_rf_bandwidth==200000 and fake.rx_buffer_size==4096
assert fake.gain_control_mode_chan0=='slow_attack'
assert len(iq)==4096 and meta['source']=='pluto-rx' and np.all(iq==3+4j)
fake.destroyed=False;fake.fail=True
try: capture('mock',2400000000,'mock-fail')
except OSError: pass
else: raise AssertionError('应向上报告异常')
assert fake.destroyed
print('模拟属性、保存与失败清理通过；不是实机RX')'''], folder)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({'scope':'离线真实运行；硬件只做导入/帮助/USB扫描与模拟调用',
                                      'records':records}, ensure_ascii=False, indent=2)+'\n')
    print('完成',len(records),'条记录；硬件RX未完成')


if __name__ == '__main__':
    main()
