"""固定划分；只在训练子集限量，不动验证/测试数据。"""
import torch
from torch.utils.data import DataLoader, Subset, random_split
from torchvision import datasets, transforms

MEAN, STD = 0.1307, 0.3081


def transform(mean=MEAN, std=STD):
    return transforms.Compose([
        transforms.ToTensor(), transforms.Normalize((mean,), (std,))])


def loaders(root, batch_size=64, train_limit=0):
    source = datasets.MNIST(root, train=True, download=True,
                            transform=transform())
    train, valid = random_split(source, [55000, 5000],
                               generator=torch.Generator().manual_seed(42))
    if train_limit:
        if not 1 <= train_limit <= len(train):
            raise ValueError('train_limit 必须在 1 到 55000 之间')
        train = Subset(train, range(train_limit))
    test = datasets.MNIST(root, train=False, download=True,
                          transform=transform())
    return (DataLoader(train, batch_size=batch_size, shuffle=True,
                       generator=torch.Generator().manual_seed(42)),
            DataLoader(valid, batch_size=256),
            DataLoader(test, batch_size=256))
