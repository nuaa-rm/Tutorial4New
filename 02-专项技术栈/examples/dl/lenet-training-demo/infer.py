"""独立进程读参数与预处理，对未参与训练的指定测试样本推理。"""
import argparse
import json
import torch
from torchvision import datasets
from data import transform
from model import LeNet


def load_model(path):
    saved = torch.load(path, map_location='cpu', weights_only=True)
    if saved['architecture'] != 'lenet28-v1' or saved['classes'] != list(range(10)):
        raise ValueError('模型结构或类别表不匹配')
    net = LeNet().eval()
    net.load_state_dict(saved['state'])
    return net, saved


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--checkpoint', default='runs/best.pth')
    cli.add_argument('--data', default='data')
    cli.add_argument('--index', type=int, nargs='+', default=[0])
    args = cli.parse_args()
    net, saved = load_model(args.checkpoint)
    test = datasets.MNIST(args.data, train=False, download=True,
                          transform=transform(saved['mean'], saved['std']))
    for index in args.index:
        if not 0 <= index < len(test):
            cli.error('测试索引必须在 0 到 9999 之间')
        x, label = test[index]
        with torch.no_grad():
            scores = net(x.unsqueeze(0))[0]
        print(json.dumps({'index': index, 'label': label,
                          'prediction': scores.argmax().item(),
                          'scores': scores.tolist()}))
