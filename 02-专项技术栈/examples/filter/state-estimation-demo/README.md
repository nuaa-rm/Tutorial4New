# 状态估计小实验

这一章先让同一个阶跃经过低通和尾部均值，再用含真值的运动轨迹比较 KF、EKF 与 UKF。你可以改参数，看误差与响应怎样一起变化；所有数据都是明确生成的模拟量，没有接实车。

在 Ubuntu 24.04 的 Distrobox 中已用 Python 3.12.3、NumPy 1.26.4 和 Matplotlib 3.6.3 实际运行。项目本身不依赖 ROS。

先安装依赖，然后进入这个 README 所在目录。下面的路径要换成自己的教材目录：

~~~bash
sudo apt install python3-numpy python3-matplotlib
cd /你的教材目录/02-专项技术栈/examples/filter/state-estimation-demo
python3 smooth.py --alpha 0.2 --window 10 --output out/smooth
python3 scalar.py
python3 fusion.py
python3 moments_demo.py
python3 run.py --mode linear --output out/linear
python3 run.py --mode range --output out/range
python3 plot.py --input out/smooth/series.npz --output out/smooth.pdf
python3 plot.py --input out/linear/series.npz --output out/linear.pdf
python3 plot.py --input out/range/series.npz --output out/range.pdf
~~~

绘图默认读取教材 fonts/站酷高端黑.ttf，也可用 --font /实际路径/中文字体.ttf 指定另一字体。plot 只读取保存的数组，不重新计算估计。

项目分工如下：

| 文件 | 用途 |
| --- | --- |
| smooth.py | 因果低通、只取已有样本的尾部均值、高通互补和无噪声阶跃响应 |
| fusion.py | 独立或相关的标量融合，完整保留交叉协方差 |
| linear.py | 检查协方差、线性预测、线性方程求解与 Joseph 更新 |
| scalar.py | 初值0/P1/Q0.1/R0.9/观测2的一步手算入口 |
| data.py | 种子42，起点1 m、速度0.3 m/s、中间三分之一加速度0.7 m/s²的真值与观测 |
| run.py | 同一序列同时运行 KF/EKF 与 UKF，记录创新、NIS、误差和协方差 |
| sigma.py | 下三角 Cholesky 因子的列生成点，重建均值与协方差 |
| moments_demo.py | 非对角协方差重建、仿射传播及均匀分布的非线性近似边界 |
| ukf.py | 独立加性噪声模型下完整取点、预测、加Q、重新取点和观测更新 |
| plot.py | 展示实际数组、真值误差与创新 |

输出目录同名文件会覆盖；比较参数时分别选择目录：

~~~bash
python3 smooth.py --alpha 0.5 --output out/smooth-a05
python3 smooth.py --alpha 1 --output out/current
python3 scalar.py --r 9
python3 fusion.py --v2 1 --rho 0
python3 fusion.py --v2 1 --rho 1
python3 run.py --mode linear --q 0 --output out/q0
python3 run.py --mode linear --r 0.4 --output out/r04
python3 run.py --mode linear --drop-every 5 --output out/drops
python3 run.py --mode linear --bias 0.5 --output out/bias
python3 run.py --mode range --alpha 0.3 --output out/range-a03
~~~

默认采样间隔 dt=0.1 s，状态顺序为位置m、速度m/s。q=0.5 是每段随机加速度方差，Q=qGGᵀ、G=[dt²/2,dt]；r=0.04 是观测方差m²，对应标准差0.2 m。不要把方差写成标准差，也不要混用连续白噪声谱密度公式。真实生成加速度不提供给滤波器；固定间隔模拟不替代实车时间戳处理。

range 观测为 sqrt(p²+2²)，EKF 在当前先验处求雅可比，但创新仍用真实 h；UKF 先加 Q 再重新取观测点。给定初始正侧位置，并不解决距离的 ±p 全局歧义。两种观测用同一份模拟噪声，不作为独立信息融合。

本次默认实测：低通 alpha=0.2 无噪声阶跃第11次更新达到90%，alpha=0.5 为4次、alpha=1 为1次；scalar 输出 K=0.55、x=1.1、P=0.495。默认线性位置 RMSE 约0.1385 m，KF/UKF 状态最大差约9.8e-15；非线性 EKF/UKF 的 RMSE 约0.1535/0.1568 m，UKF 在这里没有更准。具体版本、参数和种子改变时应重新记录。

moments_demo 的仿射传播匹配解析均值和协方差；均匀输入 X²+X 的精确方差19/45与当前 beta=2 的 UT 方差5/9不同。这是分布高阶矩的差异，不能把一个均值算对当作所有统计量精确。

run 的 series.npz 保存真值、观测、两种估计、创新、NIS、dt/Q/R；metrics.json 和终端 JSON 保存有限的误差与协方差指标。缺测帧的创新与 NIS 数组为 NaN，因为没有新观测可比较；两个滤波器只预测，不重复更新旧观测。协方差应对称半正定；本项目取点需正定，奇异矩阵会明确报错。

单次 NIS 平均值不是模型正确的证明。先检查输入单位、时间、偏置和模型，再比较真值误差、变化时段与残差。真实目标、时序和工程状态机需要另外验证。
