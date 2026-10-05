# 相机与标定小实验

从本目录执行。数值部分用 Ubuntu 系统 Python 3、NumPy、OpenCV、PyYAML；ROS 部分使用 Ubuntu 22.04 / Humble。模拟棋盘格不代替真实镜头、曝光、板面或同步测试。

~~~bash
sudo apt install python3-numpy python3-opencv python3-yaml
python3 optics.py
python3 optics.py --aperture 8 --distance 7000
python3 format_gamma.py --gamma 2.2 --output out/format
python3 format_gamma.py --gamma 1 --output out/identity
python3 noise.py --photons 900 --output out/noise
python3 generate.py --output data
python3 calibrate.py --images data/train --output out
python3 calibrate.py --images data/front --output out/front
python3 validate.py --image data/validation/000.png --model out/model.npz --output out/validation
python3 validate.py --image data/validation/000.png --model out/front/model.npz --output out/front-validation
python3 stereo.py --data data --model out/front.yaml --output out/stereo
~~~

同名输出会写入，第一次运行用新的 data/out 目录；重新生成不同参数的数据时也换目录，避免混入旧图。固定种子 2026 生成 83 张训练、15 张验证、12 张正面图和 94 对双目图。truth.json 记录生成条件，拟合不读取它。

默认数值：H=6416 mm、近界约1526.72 mm、远界约2898.55 mm；800 pixel/s、1 pixel 预算对应1.25 ms最长曝光。远界无穷以 null 表示。Bayer48字节、BGR144字节，中心 BGR=[50,100,200]；gamma2.2的LUT[128]=186，gamma1逐项恒等。光子期望900的理论标准差30、相对噪声约3.33%。

多姿态拟合 RMS 约0.255 pixel、fx约559.70；仅正面拟合也能有约0.263 pixel RMS，但fx约2493.39，不能只用低训练残差选模型。验证000固定内参、只解该图位姿，主模型 RMS约0.337 pixel；这不是外部真值精度。model.npz 保存原K/D、模式、板尺寸与平移；front.yaml 为ROS标定文件。验证还保存原图、角点图、校正图与校正模型。原图用原K/D，校正图用新K和零畸变。双目93对有效角点、水平基线约0.11995 m、参与拟合照片的纵向残差RMS约0.091 pixel；本模拟两侧内参相同，实机需分别求两侧模型。

文件协作：board统一规格/角点检测；generate造输入；calibrate求解/逐图残差，调用model_io写YAML；validate固定内参检查独立照片；stereo固定内参求相对位姿和校正投影；replay_ros加载图/YAML、发布原图与参数并提供持久保存服务；check_ros核对实际校正输出。optics、format_gamma、noise分别负责独立小数组实验。全部11个核心源码在正文展示。

## Humble 单目保存与校正

~~~bash
sudo apt install ros-humble-camera-calibration ros-humble-image-proc \
  ros-humble-camera-info-manager \
  ros-humble-rqt-image-view
source /opt/ros/humble/setup.bash
python3 replay_ros.py --images data/train --yaml out/ros-front.yaml
~~~

保持回放运行，其他终端同样 source 环境。显示标定界面需要图形会话。回放640×480 mono8、每0.1秒发布、每0.5秒换图；没有YAML时K00=0。GUI的CALIBRATE可用后求解，再SAVE，核对/tmp/calibrationdata.tar.gz的采样图和ost.yaml，及时复制到独立目录。COMMIT实际调用下面的服务，成功后写入指定YAML。已有文件会在下次启动时加载；想重新开始用新文件名。

~~~bash
ros2 topic info /camera/image_raw --verbose
ros2 topic hz /camera/image_raw
ros2 service list -t
ros2 run camera_calibration cameracalibrator \
  --size 9x6 --square 0.025 --camera_name front --k-coefficients 2 \
  --ros-args -r image:=/camera/image_raw \
  -r camera/set_camera_info:=/camera/set_camera_info
~~~

9×6数内角点，边长0.025米；两个径向系数对应固定k3=0。标定器采到40个样本也可能启用CALIBRATE，不代表覆盖条或真实质量已经合格。

用Ctrl+C停止回放，再按同一命令启动。实际检查重启后参数、匹配时间戳与校正图，第三个终端跑check：

~~~bash
ros2 topic echo /camera/camera_info --once
ros2 launch image_proc image_proc.launch.py namespace:=camera
# 另一个加载环境的终端：
python3 check_ros.py --output out/ros-check
ros2 run rqt_image_view rqt_image_view
~~~

检查器等待最多15秒，收齐相同时间戳的原图/参数/校正图，比较真实image_proc与同一K/D/R/P的remap，允许逐像素最大差1；同时检查编码和frame_id。这验证模型使用链路，真实标定质量仍需独立照片与实拍。

无服务练习：replay添加--no-service；标定器在--ros-args之前加--no-service-check，只求解/SAVE。提取ost.yaml后，用--yaml明确加载，重新启动并再核对。管理库安装或跳过服务检查不会自动让任意驱动加载文件。

## 双目命名与同步

~~~bash
python3 replay_ros.py --images data/left --right data/right \
  --namespace left --yaml out/stereo-ros.yaml
# 另一个图形终端：
ros2 run camera_calibration cameracalibrator \
  --size 9x6 --square 0.025 --k-coefficients 2 \
  --ros-args -r left:=/left/image_raw -r right:=/right/image_raw \
  -r left_camera/set_camera_info:=/left/set_camera_info \
  -r right_camera/set_camera_info:=/right/set_camera_info
~~~

左右发布同一时间戳，分别保存stereo-ros.yaml/stereo-ros_right.yaml。默认精确时间配对。--approximate 0.01（放在--ros-args前）仅允许配对时间差，不消除曝光时差或运动误差。核对左右角点、保存的两份参数及相同时间戳，再检查重启后的参数加载。真实双目装置还需现场检查同步、基线和曝光。

自动验证见仓库scripts/verify_camera_examples.py和verify_camera_gui.py（GUI使用独立Xvfb，只控制自己的窗口）；完整证据/边界见docs/revision/volume-2-chapter-7.md。
