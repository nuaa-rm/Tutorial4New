# LeNet 训练、保存与独立推理

从本目录运行。Ubuntu2404 的 Python3.12 已实际验证；Distrobox 用户先进入 ubuntu2404。CPU 是必做路径，CUDA 另建环境，避免覆盖能工作的 CPU 环境。PyTorch2.6.0/torchvision0.21.0 是固定复现组合，不声称最新版本。

```bash
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu
python -c "import sys,torch,torchvision; print(sys.executable,torch.__version__,torchvision.__version__,torch.ones(2,3).shape)"
python fit_demo.py
python ops_demo.py
python loss_demo.py
python grad_demo.py
python mode_demo.py
python model.py
python train.py --epochs 1 --train-limit 128 --out smoke
python train.py --epochs 3 --out runs
python infer.py --index 0 1 2
python nms_demo.py
python benchmark.py
python -m pip install -r requirements-export.txt
python export_compare.py
```

MNIST 首次下载四个 gzip，训练来源60000张，固定划分55000/5000；测试10000张。网络输入N×1×28×28→特征N×16×4×4→logits N×10。128张只用于检查闭环，不评价模型能力。完整训练逐轮显示训练/验证统计，按验证损失保存 best.pth，最终只评价选中模型一次测试。runs/metrics.json 记录配置和真实曲线，独立 infer 使用权重中保存的归一化与类别表。默认CPU1线程以控制复现成本，成绩不是硬性承诺。

生成的 smoke/runs/data 为本地结果，不提交大数据和权重。再次运行会覆盖同一输出目录的参数/统计；需比较时用不同 --out 路径。

ops_demo 的互相关为19/25/37/43，池化最大4/5/7/8、平均2/3/5/6；grad_demo 为-16→-32，清零后一步w=1.6/损失0.64。model.py 输入32变体的特征为16×5×5，必须同步更改Linear400才能完成分类。nms_demo 是同类别人工候选框，保留0/2，不能当作赛场检测。

export_compare 是固定1×1×28×28的ONNX opset17；dynamo=False明确使用本次实测的旧导出路径，不依赖新版默认值。同一真实张量检查误差与类别；预处理仍在Python外部保存，不包含在ONNX图内。OpenVINO/TensorRT是后续部署目标，未运行时不能称加速已验证。benchmark只测CPU前向中位数，批量32的每样本成本与单帧响应不是一回事。

CUDA 可选：按 [官方固定版本组合](https://docs.pytorch.org/get-started/previous-versions/) 在单独虚拟环境选择匹配驱动的构建，检查 torch.version.cuda/torch.cuda.is_available()；再用相同命令加 --device cuda，报告实际设备与版本。不把 torch 的CUDA运行库当成 nvcc 编译环境。检测框架须另查选定仓库/提交的预处理、类别表、许可与后处理；本项目不需要下载YOLO权重。
