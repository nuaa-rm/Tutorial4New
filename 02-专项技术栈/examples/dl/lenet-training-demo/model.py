"""本章的 28×28 LeNet 风格网络，不等同于原版 LeNet-5。"""
import torch
from torch import nn


class LeNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 6, 5), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(6, 16, 5), nn.ReLU(), nn.MaxPool2d(2))
        self.classifier = nn.Sequential(
            nn.Linear(256, 120), nn.ReLU(),
            nn.Linear(120, 84), nn.ReLU(), nn.Linear(84, 10))

    def forward(self, x):
        return self.classifier(self.features(x).flatten(1))


if __name__ == '__main__':
    net = LeNet()
    x = torch.zeros(2, 1, 28, 28)
    print('特征', tuple(net.features(x).shape))
    print('展平', tuple(net.features(x).flatten(1).shape))
    print('分数', tuple(net(x).shape))
