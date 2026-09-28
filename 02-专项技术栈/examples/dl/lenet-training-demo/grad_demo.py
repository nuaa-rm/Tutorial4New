"""分开看梯度计算、累加与参数更新。"""
import torch

w = torch.nn.Parameter(torch.tensor(0.0))
optimizer = torch.optim.SGD([w], lr=0.1)
loss = (w * 2 - 4) ** 2
loss.backward()
print('第一次梯度', w.grad.item(), '参数仍为', w.item())
(w * 2 - 4).square().backward()
print('未清零又反传', w.grad.item())
optimizer.zero_grad()
(w * 2 - 4).square().backward()
optimizer.step()
print('清零后一步', w.item(), '损失', (w * 2 - 4).square().item())
