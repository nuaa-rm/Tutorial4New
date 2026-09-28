"""分类交叉熵内部处理 logits，不再提前套一次 softmax。"""
import torch

scores = torch.tensor([[2., 0., -1.]], requires_grad=True)
label = torch.tensor([0])
loss = torch.nn.CrossEntropyLoss()(scores, label)
probability = scores.softmax(1)
print('概率', probability.detach().tolist())
print('交叉熵', loss.item(), '负对数概率', -probability[0, 0].log().item())
print('重复softmax后的损失', torch.nn.CrossEntropyLoss()(probability, label).item())
loss.backward()
print('logits梯度', scores.grad.tolist())
