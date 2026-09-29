# 小地图上的导航闭环

先用生成的点云和栅格把地图、过滤和最短路讲清，再在真正的 Jazzy Nav2 规划器/控制器上调用 action，保存路径、速度和软件里程计；最后用逐 tick 模拟器核对恢复语义。没有真实电机、雷达或SLAM输入，不模拟惯性、打滑和碰撞动力学。

实跑环境：Distrobox ubuntu2404、Ubuntu24.04、Python3.12、Nav2 1.3.13、PCL1.14.0。Humble 概念共用，插件/参数/速度消息按实际版本核对。

进入容器并安装缺失依赖，随后在**本项目目录**执行命令：

~~~bash
distrobox enter ubuntu2404
bash
source /opt/ros/jazzy/setup.bash
sudo apt-get install --no-install-recommends \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  libpcl-dev cmake g++ python3-numpy python3-scipy \
  python3-matplotlib python3-yaml fonts-wqy-zenhei
cd /home/mijiao/Apps/Tutorial4New/02-专项技术栈/examples/navigation/navigation-lab-demo
export ROS_DOMAIN_ID=188
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
~~~

路径换成你的仓库，两个终端用相同环境；188 若已使用则换空闲域。默认地图60×40格、0.1m/cell，有边框和中央障碍，起点(0.55,0.55)、目标(5.05,3.05)m。输出目录重复使用会覆盖，变式应另存。

~~~bash
python3 localization.py
python3 tf_demo.py
cmake -S . -B build
cmake --build build -j4
./build/point_filters
python3 grid.py --output out/map
python3 grid.py --blocked --output out/blocked
python3 grid.py --margin 0.6 --output out/wide
python3 bt.py
python3 bt.py --fail
python3 bt.py --stuck
~~~

定位修正为(0.3,0)/(0.2,0)，odom不变，长墙约束特征值0/2。tf2合成得到(1,4)，缺失分支LookupException。PCL质心x=0.02，输入32/高度31/清理30；Dijkstra和A*总代价70、71格，扩展1304/914，封路返回空路径。margin 是格心距离模型的阈值，非完整车体碰撞判定；起终点被挡也返回无路，负/NaN拒绝。

BT 默认成功、fail最终失败，都完成最多两次恢复；stuck等十个tick后输出Timeout。Control是带记忆的Sequence/Fallback，Recovery只在主任务失败后恢复、恢复成功后重试。clear/wait是脚本动作，没有调用真实Nav2服务；tick预算不等于真实时间限制。

终端一保持运行：

~~~bash
python3 grid.py --output out/map
ros2 launch "$PWD/lab.launch.py"
~~~

终端二也在项目目录加载上述环境：

~~~bash
python3 client.py --output out/nav2
ros2 topic type /cmd_vel
ros2 param get planner_server GridBased.plugin
ros2 param get controller_server FollowPath.plugin
ros2 run tf2_ros tf2_echo map base_link
~~~

查询TF程序Ctrl+C后再执行失败变式与绘图：

~~~bash
python3 client.py --blocked-goal --output out/nav2-blocked
python3 plot.py --map out/map --nav2 out/nav2 --output out/navigation.pdf
~~~

客户端等待map/planner/controller生命周期激活，避免仅action服务存在就请求规划；通信/结果期限明确，等待结果超时会请求取消。默认规划/控制status4、error0、123路径点、目标误差约0.10m；blocked-goal位于(3,2)m障碍中，规划status6/error206，无路径，不请求控制。具体样本计数随调度变化。结果保存在result.json和nav2.npz；地图输入另有PGM/YAML、grid.npz、paths.json。plot读取同次数组，默认文泉驿，--font可替换实际字体文件。

cmd_vel明确为Twist；Navfn和RPP使用params中指定的插件。两代价地图只有静态层和膨胀层，没有动态传感器观测。sim固定map→odom，用真实单调时间间隔积分速度，20Hz更新odom→base_link，软件断流0.5s后停积分。它不能替代真实定位、动力学或底盘看门狗。

慢速实验：终端一Ctrl+C，备份params.yaml，将desired_linear_vel改为0.3，重启launch恢复同一起点，再运行client另存out/slow，核对实际速度峰值和用时；完成后恢复参数。恢复实验可将bt.py的retries改为0，首次失败就退出，也可给clear脚本一个Failure检查恢复自身失败的出口。

文件配合：grid提供地图与离线算法，localization/tf_demo分别演示定位修正/真实tf2查询，point_filters+CMake构建过滤程序，params/lab.launch/sim/client形成真实服务器软件闭环，bt核对任务语义，plot画实际结果。正文完整引入全部核心文件。

仓库根目录可在同一Jazzy环境执行验证脚本：

~~~bash
python3 scripts/verify_nav_examples.py \
  --project 02-专项技术栈/examples/navigation/navigation-lab-demo \
  --work /tmp/textbook-nav-verify \
  --evidence /tmp/textbook-nav-runtime.json
~~~

脚本实际启动本项目域188，生成输入、编译PCL、独立核对路径/地图/格心/BT，订阅真实地图与代价地图、查询TF、调用Nav2并检查软件轨迹与圆形半径相对障碍的余量。域号应空闲；它不控制真实机器人。终端一Ctrl+C结束手动实验。真实雷达地图、同步/外参、实车轮廓/制动/动态障碍、现场恢复留在卷三验证。
