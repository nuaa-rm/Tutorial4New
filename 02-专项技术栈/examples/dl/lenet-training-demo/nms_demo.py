"""只演示同类别候选框后处理，不是训练好的 YOLO 检测器。"""
import torch
from torchvision.ops import nms

boxes = torch.tensor([[0., 0., 10., 10.], [1., 1., 11., 11.],
                      [20., 20., 30., 30.]])
scores = torch.tensor([0.9, 0.8, 0.7])
keep = nms(boxes, scores, iou_threshold=0.5)
print('保留索引', keep.tolist())
