# 从任务前提到导航结果

本卷只用一个小检查器说明直通道宽度、坐标变换与结果取证。
Python3.10+标准库即可。check.py不连接执行器，不关闭急停，不能证明真实机器人到位。
真正的Nav2项目复用卷二navigation/navigation-lab-demo，核心源码和配置已在卷二完整讲解。

在卷三目录：

```bash
cd examples/navigation-task-demo
python3 check.py
python3 check.py --robot 0.5 --margin 0.1
python3 check.py --corridor 0.7
```

默认车宽0.6m、两侧各0.15m，总需求0.9m，0.8m直通道不通过。
0.5/0.1变式需求0.7m，通过直线宽度检查，仍不能证明转弯和动态场景可行。
教学场地巡逻点(2,0)m，经yaw=90deg、平移(1,1)m得到地图点(1,3)m。
变换方向明确为map<-field，选出的巡逻点不是直接把敌方位置当成本车定位或速度。

实际Nav2输入在仓库根目录按卷二README准备Ubuntu24.04/Jazzy环境，
并选用空闲DDS域188，仅localhost；输出目录已存在时会覆盖，改动参数另存。
可以用随书验证脚本启动/清理自己的软件模型和3个服务器：

```bash
python3 scripts/verify_nav_examples.py \
  --project 02-专项技术栈/examples/navigation/navigation-lab-demo \
  --work /tmp/textbook-v3-nav --evidence /tmp/textbook-v3-nav-runtime.json
```

这会真实调用规划/控制action，生成map/PGM/YAML、nav2/result.json、nav2/nav2.npz，
并给出nav2-blocked/result.json。源码/插件/YAML/启动文件完整讲解见卷二导航章。
默认实际status4/error0、约0.10m误差；障碍内目标status6/error206/0路径，
未请求FollowPath。样本数受调度影响，检查具体运行结果而不是背次数。
然后回到本项目运行：

```bash
python3 check.py --result /tmp/textbook-v3-nav/nav2/result.json
python3 check.py --result /tmp/textbook-v3-nav/nav2-blocked/result.json
```

前者提示继续复核轨迹与实验条件，后者提示查看目标/地图/TF，不能把规划失败
与执行失败混成同一层。其他ROS发行版先按自己的版本核对插件与消息类型。
软件模型固定定位，仅静态地图/膨胀层；没有动态雷达、真实SLAM、摩擦、打滑与惯性。
实际赛场建图、车体外形、动态障碍、制动和恢复空间仍须真实设备测试。
