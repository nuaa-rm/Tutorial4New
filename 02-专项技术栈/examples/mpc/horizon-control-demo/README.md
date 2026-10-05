# 有限时域 MPC 离线小项目

先从原来能手算的三步响应与一步优化接着做，再用实际 OSQP 求解一段未来输入。所有数据由小模型生成，不连接 ROS、电机或开火接口。

## 文件与单位

| 文件 | 作用 |
| --- | --- |
| response.py | 一阶阶跃、离散稳态频响、纯延时与几何半角 |
| scalar.py | 一步标量限幅、重新规划与照旧序列的扰动比较 |
| model.py | 保持加速度的双积分离线模型，生成实际对象 |
| prediction.py | 堆叠未来角度/角速度，对应明确的 k 索引 |
| qp.py | 完整有限时域代价、加速度/速度约束与可选硬终点 |
| controller.py | 真实单调时间、状态/有限性/原始约束/预算/年龄检查 |
| run.py | 模拟对象、反馈循环、模型增益误差、后置低通和失败日志 |
| plot.py | 仅读取实际保存数组，不重新求解或改写轨迹 |

状态为角度 rad、角速度 rad/s，输入为每周期保持的角加速度 rad/s²；dt=0.05 s。模型不是已辨识的云台，也不能将加速度直接发送到接收速度或力矩的接口。一阶 response 的 y 是归一化信号，与此物理状态分开。

## 准备与最短运行

Ubuntu24.04 中使用 Python3.12，NumPy1.26.4、SciPy1.11.4、Matplotlib3.6.3、OSQP1.0.4 实测。项目不依赖 ROS。将下面教材路径换成自己的，在项目目录执行：

~~~bash
sudo apt install python3-venv python3-numpy python3-scipy python3-matplotlib
cd /你的教材目录/02-专项技术栈/examples/mpc/horizon-control-demo
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python response.py --output out/response
python response.py --a 0.5 --output out/fast
python scalar.py
python run.py --output out/default
~~~

response 默认前三步为0.2/0.36/0.488，达到0.9需11步；a0.5需4步。scalar 输入0.2、完整代价0.68，原六轮到0.95；第三轮后负0.1扰动，重新规划到0.925、旧序列到0.85。完整 MPC 默认 N15、q角度20/q速度0.5/r0.1、加速度2/速度0.8，80轮约4s模拟，角度收敛到约0.4；实际计时是桌面运行，不是实时调度证明。

NPZ保存状态与真正执行输入；log.json逐轮保存求解状态、原始约束违反量、实际采集/开始/结束单调时间、整轮耗时、输入年龄、接受或回退理由、control与applied。已有同名输出会覆盖，比较时换目录。仿真 plant_time=k×dt 与实际 perf_counter 时间分别解释，不把离线循环当实时定周期运行。

## 改参数观察

~~~bash
python run.py --horizon 1 --output out/short
python run.py --horizon 30 --output out/long
python run.py --r 1 --output out/weight
python run.py --vmax 0.3 --output out/speed
python run.py --reference 0.7 --output out/jump
python run.py --disturb -0.1 --output out/disturb
python run.py --gain 0.6 --output out/mismatch
python run.py --command-alpha 0.1 --output out/filtered
~~~

horizon以步计，reference/disturb以rad计；gain只改变模拟对象。q/r为当前单位下的代价，不是硬约束。N1在本次4s窗口明显较慢；N30与N15效果相近但计算更多。r1更温和，vmax0.3限制速度，数值容差可能有约1e-7级差异。模型增益误差不代表所有非线性扰动。后置alpha0.1低通让输入平滑，但这次最大速度约0.8203超过0.8，不能据此认为平滑就保证约束。

## 真实失败与时效实验

~~~bash
python run.py --horizon 2 --terminal --steps 3 --output out/infeasible
python run.py --max-iter 1 --steps 3 --output out/maxiter
python run.py --work-ms 20 --steps 3 --output out/late
python run.py --age-ms 200 --steps 3 --output out/stale
~~~

从静止状态、0.1s内保持加速度最多2，只能转0.01rad，硬终点0.4实际不可行。max-iter1限制真实求解器；work-ms是真实等待，制造整轮超过10ms预算；age-ms让采集时间早于现在，100ms年龄上限会拒绝。后两者即使 solved 也回退。默认选择只接受 status_val=1，再检查有限控制、原始约束违反量≤1e-5、整轮预算与输入年龄。OSQP内部run_time不包含整个Python链路。

回退按声明模型限制减速 clip(-速度/dt,-amax,amax)，非万能安全策略；初始速度1.2时下一步仍1.1，无法立即满足0.8。无效/非有限输入明确拒绝，未来单调时间戳也拒绝；跨设备时钟需另外同步并定义错误接收行为。

## 实际数组绘图

~~~bash
python plot.py --kind response --input out/response/result.npz --compare out/fast/result.npz --output out/response.pdf
python plot.py --kind control --input out/default/result.npz --compare out/short/result.npz --output out/horizon.pdf
python plot.py --kind control --input out/default/result.npz --compare out/filtered/result.npz --compare-label '后置低通alpha0.1' --output out/filter.pdf
~~~

随书字体默认 fonts/站酷高端黑.ttf，也可用 --font 指定本机字体。候选配图在独立及正文实际尺寸检查通过后才加 _revised。图中灰线取默认输入的上限；比较不同上限/参考须重新解释。response右图是稳态分量，不是初始响应；纯延时不改变幅度比例。

## 完整复核

从项目目录，激活虚拟环境后运行：

~~~bash
python ../../../../scripts/verify_mpc_examples.py --project "$PWD" --work /tmp/mpc-check --evidence /tmp/mpc-check.json
~~~

脚本实际运行参数和失败变体，再以独立矩阵指数、逐步递推、完整代价/差分梯度、SLSQP、稳态正弦拟合与非零速度回退核对。记录源码SHA256与环境；绘图另实际运行并记录输入/输出散列。时间依机器负载变化，不能要求新机器复制同一毫秒数，也不能只拿编译通过或 solved 当全链路验收。

官方接口：https://osqp.org/docs/interfaces/python.html 。状态：https://osqp.org/docs/interfaces/status_values.html 。求解器设置：https://osqp.org/docs/interfaces/solver_settings.html 。本项目使用实际1.0.4参数，其他版本应重新核对。
