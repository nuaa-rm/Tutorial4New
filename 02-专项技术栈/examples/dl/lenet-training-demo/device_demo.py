"""同一参数、同一输入比较 CPU/CUDA 前向；不把可用性当加速证明。"""
import sys
import torch
from infer import load_model
from model import LeNet

if not torch.cuda.is_available():
    sys.exit('当前构建或设备不能使用 CUDA')
net, saved = load_model('runs/best.pth')
gpu = LeNet().to('cuda').eval()
gpu.load_state_dict(saved['state'])
x = torch.ones(2, 1, 28, 28)
with torch.no_grad():
    expected = net(x)
    actual = gpu(x.to('cuda')).cpu()
torch.testing.assert_close(actual, expected, rtol=1e-4, atol=1e-5)
print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0))
print('CPU/CUDA最大误差', (actual-expected).abs().max().item())
