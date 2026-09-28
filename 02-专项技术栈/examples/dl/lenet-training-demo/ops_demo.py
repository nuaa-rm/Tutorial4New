"""同一输入实际计算互相关、池化与激活，核不翻转。"""
import torch
from torch.nn import functional as F

x = torch.arange(9, dtype=torch.float32).reshape(1, 1, 3, 3)
w = torch.tensor([[[[0., 1.], [2., 3.]]]])
print('互相关', F.conv2d(x, w).flatten().tolist())
print('最大池化', F.max_pool2d(x, 2, 1).flatten().tolist())
print('平均池化', F.avg_pool2d(x, 2, 1).flatten().tolist())
a = torch.tensor([-2., 0., 2.])
print('ReLU', F.relu(a).tolist())
print('sigmoid', torch.sigmoid(a).tolist())
