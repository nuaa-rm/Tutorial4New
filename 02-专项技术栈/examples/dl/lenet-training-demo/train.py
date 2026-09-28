"""先用 128 张检查闭环，再恢复完整训练集；测试只评价最终模型。"""
import argparse
import json
from pathlib import Path
import torch
import torchvision
from data import loaders, MEAN, STD
from engine import run_epoch
from model import LeNet


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--data', default='data')
    cli.add_argument('--out', type=Path, default=Path('runs'))
    cli.add_argument('--epochs', type=int, default=3)
    cli.add_argument('--batch-size', type=int, default=64)
    cli.add_argument('--train-limit', type=int, default=0)
    cli.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    cli.add_argument('--threads', type=int, default=1)
    args = cli.parse_args()
    if min(args.epochs, args.batch_size, args.threads) <= 0:
        cli.error('epochs/batch-size/threads 必须大于零')
    if args.train_limit < 0:
        cli.error('train-limit 不得为负；0 表示完整训练集')
    if args.device == 'cuda' and not torch.cuda.is_available():
        cli.error('当前 PyTorch/CUDA 环境不可用')
    torch.manual_seed(42)
    torch.set_num_threads(args.threads)
    device = torch.device(args.device)
    train, valid, test = loaders(args.data, args.batch_size, args.train_limit)
    net = LeNet().to(device)  # 先移动模型，再创建优化器
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
    x, y = next(iter(train))
    print('首批', tuple(x.shape), tuple(y.shape), '输出',
          tuple(net(x.to(device)).shape))
    args.out.mkdir(parents=True, exist_ok=True)
    best = float('inf')
    history = []
    for epoch in range(1, args.epochs + 1):
        row = {'epoch': epoch,
               'train': run_epoch(net, train, criterion, device, optimizer),
               'valid': run_epoch(net, valid, criterion, device)}
        history.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if row['valid']['loss'] < best:
            best = row['valid']['loss']
            torch.save({'architecture': 'lenet28-v1', 'mean': MEAN,
                        'std': STD, 'classes': list(range(10)),
                        'state': {k: v.detach().cpu() for k, v in net.state_dict().items()}},
                       args.out / 'best.pth')
    saved = torch.load(args.out / 'best.pth', map_location=device, weights_only=True)
    net.load_state_dict(saved['state'])
    result = run_epoch(net, test, criterion, device)
    print('最终测试', json.dumps(result), flush=True)
    report = {'torch': torch.__version__, 'torchvision': torchvision.__version__,
              'device': str(device), 'epochs': args.epochs,
              'batch_size': args.batch_size, 'threads': args.threads,
              'train_limit': args.train_limit, 'seed': 42, 'history': history,
              'test': result, 'selection': '最低验证损失'}
    (args.out / 'metrics.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
