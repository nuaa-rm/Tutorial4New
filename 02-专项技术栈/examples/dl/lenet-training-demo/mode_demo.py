"""eval 控制层行为，no_grad 控制梯度记录，两者分工不同。"""
import torch

torch.manual_seed(42)
net = torch.nn.Dropout(p=0.5).train()
x = torch.ones(8, requires_grad=True)
with torch.no_grad():
    train_output = net(x).clone()
net.eval()
eval_output = net(x).clone()
with torch.no_grad():
    inference_output = net(x).clone()
print('训练+no_grad', train_output.tolist(), train_output.requires_grad)
print('eval', eval_output.tolist(), eval_output.requires_grad)
print('eval+no_grad', inference_output.tolist(), inference_output.requires_grad)
