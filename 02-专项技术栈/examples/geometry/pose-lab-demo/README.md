# 几何与位姿实验

先把同一批三维点变成像素，再反过来恢复位姿，最后把多帧相机与三维点一起放进优化。这里使用明确生成的小规模数据，便于核对方向、尺度、导数和误差；没有把模拟结果当成赛场相机精度。

在教材卷二的 examples/geometry/pose-lab-demo 目录执行。Ubuntu 24.04 的 Distrobox 中已实际运行 Python 3.12.3、OpenCV 4.6.0、NumPy 1.26.4、SciPy 1.11.4、Matplotlib 3.6.3。项目本身不依赖 ROS。缺依赖时：

~~~bash
sudo apt install python3-numpy python3-opencv python3-scipy python3-matplotlib
cd /你的教材目录/02-专项技术栈/examples/geometry/pose-lab-demo
~~~

从 Arch 宿主进入已有容器可以先执行 distrobox enter ubuntu2404，再在里面运行。不要用宿主的 Python 代替容器 Python 又假定依赖相同。

| 文件 | 做什么 |
| --- | --- |
| model.py / basics.py | 世界到相机变换、正深度针孔投影、图像缩放/裁剪与逆变换 |
| dlt.py / pnp_demo.py | 去畸变归一化 DLT、PnP 和三点/额外点核对 P3P 候选 |
| numeric_demo.py | RQ 与 QR 顺序、反射及含误差旋转的 SVD 投影 |
| lie.py / lie_demo.py | 叉乘帽、SO(3)/SE(3)指数、左右乘小扰动与对数分支核对 |
| residual.py / jacobian_demo.py | 观测减预测的像素残差、左乘雅可比与独立中心差分 |
| optimize.py / pose_demo.py | 固定三维点、阻尼位姿迭代、二维块 Huber 与候选代价检查 |
| schur.py / bundle_demo.py | 三相机/20点联合 BA，固定参考与深度尺度锚，消元后回代 |
| graph_demo.py | 一维相对平移图的白化、参考固定与不一致闭环 |
| registration_demo.py | 已知对应 SVD 拟合，以及真实最近邻搜索的 ICP 循环 |
| plot.py | 读取刚保存的实际数组，以相同坐标范围画优化前后残差 |

先依次运行能单独核对的小例子，再跑优化：

~~~bash
python3 basics.py
python3 pnp_demo.py
python3 numeric_demo.py
python3 lie_demo.py
python3 jacobian_demo.py
python3 pose_demo.py --output out/pose
python3 bundle_demo.py --output out/bundle
python3 graph_demo.py --loop 2.2
python3 registration_demo.py
python3 plot.py --input out/bundle/result.npz --output out/bundle.pdf
python3 plot.py --input out/pose/result.npz --output out/pose.pdf
~~~

每个程序打印实际 JSON 指标。pose/bundle 自动创建输出目录，但同名 result.npz 会被覆盖，保留对照时请分目录；plot 的同名 PDF 也会被覆盖。默认中文字体取教材共享字体，可用 --font /字体文件路径 指定自己的 TTF/OTF。NPZ 保存观测、真值及初始/最终预测，plot 读取它，不另造一组更好看的结果。

接下来改变输入，观察结果和检查条件一起变化：

~~~bash
python3 pnp_demo.py --noise 0.3
python3 pnp_demo.py --swap
python3 pnp_demo.py --scale 1000
python3 pose_demo.py --noise 0 --output out/pose-clean
python3 pose_demo.py --outlier 80 --output out/pose-outlier
python3 pose_demo.py --outlier 80 --huber 2 --output out/pose-robust
python3 bundle_demo.py --noise 0 --output out/bundle-clean
python3 bundle_demo.py --outlier 80 --output out/bundle-outlier
python3 bundle_demo.py --outlier 80 --loss huber --output out/bundle-robust
python3 graph_demo.py --loop 2
python3 registration_demo.py --initial-shift 2
~~~

noise 是像素标准差，outlier 是指定观测的 (b,-b) pixel 偏移。pose 的 huber 按每个二维残差的范数计算，0 为普通平方；bundle 的 loss huber 使用 SciPy 逐坐标 Huber，阈值为 2 pixel，两者定义不同。scale 同时缩放物体点与真实平移，单位由三维模型决定。initial-shift 是 ICP 初始平移的 x 分量，单位为 m。参数细节也可用 --help 查看。

本次应能核对的现象：

- 点 (0.2,0.1,2)m 投到 (400,280)pixel，深度加倍后为 (360,260)；图像缩半/裁左20后为 (180,140)。
- 无噪声 PnP/DLT RMS 接近浮点零；0.3pixel 噪声下分别约 0.299/2.186pixel。默认 P3P 有两个候选，三点均接近拟合，但全部点 RMS 约 67.57 与 0.000056pixel，应看额外点及正深度，不固定候选编号。
- 交换点序后，本次 PnP 返回成功但存在负深度，RMS 为 null；这是无效位姿提示。三维数值乘1000后，平移 z 从2变2000，投影基本不变。
- 位姿/点解析雅可比与中心差分最大差约 2.3e-8 / 9.5e-9。左右乘近似误差约 9.2e-12，直接元素相加则破坏正交性。
- 固定点位姿优化在同样80pixel异常偏移下，普通平方/块Huber的其余点真值RMS约8.235/0.153pixel；不同损失的总cost不能直接比较。
- 联合 BA 固定相机0和第一个点 Z=3.5m，71变量/120残差；默认 RMS 从28.84降至0.269pixel，但点RMSE仍约0.135m。无噪声时两类误差接近浮点零。异常点 Huber 变体的干净点真值RMS仍约4.89pixel，不能宣称自动修好了数据。
- Schur 与直接解核对的是同一个加阻尼增量方程。参考/尺度未固定的原问题不能靠阻尼证明唯一。
- 一维闭环2.2m给出位置约0/1.06667/2.13333。已知配准误差接近浮点零，当前40个非对称点的ICP在初始平移0/2m时分别3/9轮收敛；这不保证其他场景。对称结构可能最近邻误差很小而标签对应仍错误。

所有位姿均需按文件说明看方向。本项目 model 的 T 把世界/物体点变到相机系，行数组用 points @ R.T + t；graph 的节点是独立的一维世界位置。联合 BA 的有限边界只适合声明的生成场景，不能照搬到任意真实点云。RMS 按二维像素向量定义；三维点 RMSE 与像素误差单位不同。

完整核验在容器中运行教材根目录的 scripts/verify_geometry_examples.py，保存源码散列、真实输出、矩阵指数/差分、畸变、退化配置、规范自由度与对称点云证据：

~~~bash
python3 /你的教材目录/scripts/verify_geometry_examples.py \
  --project "$PWD" --work /tmp/textbook-geometry-verify \
  --evidence /tmp/geometry-runtime.json
~~~

核验不会使用相机或控制执行器；Ceres/g2o 和一般六维位姿图是正文的后续阅读，不属于本项目已经运行的功能。
