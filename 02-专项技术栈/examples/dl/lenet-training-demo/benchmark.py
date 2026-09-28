"""只测 CPU 前向，预处理、排队和传输不在此计时内。"""
import torch
from torch.utils.benchmark import Timer
from infer import load_model

net, _ = load_model('runs/best.pth')
for batch in (1, 32):
    x = torch.ones(batch, 1, 28, 28)
    with torch.no_grad():
        net(x)  # 预热
        result = Timer('net(x)', globals={'net': net, 'x': x},
                       num_threads=1).blocked_autorange(min_run_time=0.2)
    seconds = result.median
    print(batch, '每批ms', seconds*1000, '每样本ms', seconds*1000/batch,
          '吞吐sample/s', batch/seconds, '线程', result.num_threads)
