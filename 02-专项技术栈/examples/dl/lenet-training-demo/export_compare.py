"""固定批量导出；同一真实测试张量比较 PyTorch 与 CPU ONNX Runtime。"""
import argparse
import json
import numpy as np
import onnx
import onnxruntime as ort
import torch
from torchvision import datasets
from data import transform
from infer import load_model

if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--checkpoint', default='runs/best.pth')
    cli.add_argument('--data', default='data')
    cli.add_argument('--output', default='runs/lenet.onnx')
    cli.add_argument('--index', type=int, default=0)
    args = cli.parse_args()
    net, saved = load_model(args.checkpoint)
    test = datasets.MNIST(args.data, train=False, download=True,
                          transform=transform(saved['mean'], saved['std']))
    if not 0 <= args.index < len(test):
        cli.error('测试索引必须在 0 到 9999 之间')
    x = test[args.index][0].unsqueeze(0)
    with torch.no_grad():
        expected = net(x).numpy()
        torch.onnx.export(net, x, args.output, input_names=['image'],
                          output_names=['scores'], opset_version=17,
                          dynamo=False)
    onnx.checker.check_model(onnx.load(args.output))
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(args.output, sess_options=options,
                                   providers=['CPUExecutionProvider'])
    actual = session.run(['scores'], {'image': x.numpy()})[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-4, atol=1e-5)
    print(json.dumps({'shape': list(actual.shape),
                      'max_abs_error': float(np.max(np.abs(actual-expected))),
                      'prediction': int(actual.argmax(1)[0])}))
