"""训练和评估共用加权统计，最后一个小批量也按样本数计算。"""
import torch


def run_epoch(net, loader, criterion, device, optimizer=None):
    training = optimizer is not None
    net.train(training)
    total = correct = 0
    loss_sum = 0.0
    with torch.set_grad_enabled(training):
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            if training:
                optimizer.zero_grad()
            scores = net(x)
            loss = criterion(scores, y)
            if training:
                loss.backward()
                optimizer.step()
            total += len(y)
            loss_sum += loss.item() * len(y)
            correct += (scores.argmax(1) == y).sum().item()
    if total == 0:
        raise ValueError('数据集为空')
    return {'loss': loss_sum / total, 'accuracy': correct / total,
            'samples': total}
