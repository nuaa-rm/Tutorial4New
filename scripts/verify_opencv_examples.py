#!/usr/bin/env python3
"""OpenCV 逐程序、关键参数、中间图、独立窗口与 Jazzy 图像回调实测。"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

SOURCE=Path(__file__).resolve().parents[1]/'02-专项技术栈/examples/opencv'
records=[]


def stop(process):
    if process.poll() is None:
        os.killpg(process.pid,signal.SIGINT)
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=5)


def run(name,command,cwd,env,expected=0):
    process=subprocess.Popen(command,cwd=cwd,env=env,stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,text=True,start_new_session=True)
    try:output,_=process.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        stop(process);output,_=process.communicate();raise RuntimeError(output)
    records.append({'step':name,'command':command,'returncode':process.returncode,'output':output})
    print(name,'->',process.returncode,flush=True)
    assert process.returncode==expected,records[-1]
    return output


def gui_worker(mode,binary,sample,screenshot):
    env=os.environ.copy();env.pop('WAYLAND_DISPLAY',None);env['QT_QPA_PLATFORM']='xcb'
    command=([binary,sample] if mode!='ros' else
             ['ros2','run','image_tools','showimage','--ros-args','-r','image:=/image_out'])
    process=subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,start_new_session=True)
    try:
        window='';title='^Image lab$' if mode=='viewer' else '^Video lab$' if mode.startswith('video') else '.'
        for _ in range(60):
            result=subprocess.run(['xdotool','search','--onlyvisible','--name',title],capture_output=True,text=True)
            if result.returncode==0:window=result.stdout.splitlines()[0];break
            assert process.poll() is None,process.communicate()
            time.sleep(.05)
        assert window,'未发现窗口'
        time.sleep(.08)
        subprocess.run(['xwd','-silent','-id',window,'-out',screenshot],check=True)
        if mode=='viewer':subprocess.run(['xdotool','keydown','--window',window,'s'],check=True)
        elif mode=='video-escape':subprocess.run(['xdotool','keydown','--window',window,'Escape'],check=True)
        elif mode=='ros':stop(process)
        output,error=process.communicate(timeout=6)
        print(output,end='');print(error,end='',file=sys.stderr)
        if mode!='ros':assert process.returncode==0
    finally:
        if process.poll() is None:stop(process)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--assets-dir',type=Path,required=True)
    args=cli.parse_args();args.output=args.output.resolve();args.assets_dir=args.assets_dir.resolve()
    args.assets_dir.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();assert env.get('ROS_DISTRO')=='jazzy'
    env.update(ROS_DOMAIN_ID='81',ROS_AUTOMATIC_DISCOVERY_RANGE='LOCALHOST',RCUTILS_COLORIZED_OUTPUT='0')
    for key in ['ROS_LOCALHOST_ONLY','ROS_STATIC_PEERS','RMW_IMPLEMENTATION']:env.pop(key,None)
    import cv2
    import numpy as np
    with tempfile.TemporaryDirectory(prefix='opencv-textbook-') as temp:
        root=Path(temp);lab=root/'lab';bridge=root/'bridge';out=root/'output';out.mkdir()
        shutil.copytree(SOURCE/'image-lab-demo',lab);shutil.copytree(SOURCE/'image-bridge-demo',bridge)
        run('configure',['cmake','-S',str(lab),'-B',str(root/'build')],root,env)
        run('build',['cmake','--build',str(root/'build'),'--parallel','4'],root,env)
        bins=root/'build'
        def demo(name,arguments=(),expected=0):return run(name,[str(bins/(name+'_demo')),*arguments],out,env,expected)
        checks={'version':'4.6.0','mat':'9 1','io':'32 48','hsv':'2','threshold':'Otsu=50 非零=400 adaptive非零=720',
                'filter':'28,64,255','morphology':'26 25','contour':'1 171 200','resize':'40 20'}
        for name,expected in checks.items():assert expected in demo(name)
        assert int(demo('features').strip())>0
        demo('sample');assert '3600,3599,3600 外轮廓=2 保留=2' in demo('pipeline',['scene.png'])
        saved={name:cv2.imread(str(out/(name+'.png')),cv2.IMREAD_UNCHANGED) for name in ['scene','mask','opened','closed','edges','annotated']}
        assert saved['scene'].shape==(120,160,3) and saved['mask'].shape==(120,160)
        assert saved['mask'][5,5]==255 and saved['opened'][5,5]==0
        assert saved['opened'][40,110]==0 and saved['closed'][40,110]==255
        assert np.any(saved['annotated']!=saved['scene'])
        for name in saved:shutil.copy2(out/(name+'.png'),args.assets_dir/(name+'.png'))
        demo('pipeline',expected=1);demo('pipeline',['missing.png'],expected=2)
        demo('viewer',expected=1);demo('viewer',['missing.png'],expected=2)
        demo('video',expected=1);demo('video',['missing.avi'],expected=2)
        original={p.name:p.read_text() for p in (lab/'src').glob('*.cpp')}
        def variant(name,transform,expected_text=None,arguments=()):
            p=lab/'src'/(name+'_demo.cpp');base=original[p.name];changed=transform(base)
            assert changed!=base;p.write_text(changed)
            run('build-'+name+'-variant',['cmake','--build',str(bins),'--target',name+'_demo'],root,env)
            output=demo(name,arguments)
            if expected_text is not None:assert expected_text in output,output
            p.write_text(base)
            return output
        variant('mat',lambda s:s.replace('b = a,','b = a(cv::Rect(0,0,1,1)),'),'9 1')
        variant('mat',lambda s:s.replace('c = a.clone()','c = a'),'9 9')
        p=lab/'src/io_demo.cpp';p.write_text(original[p.name].replace('cv::imread("input.png")','cv::imread("absent.png")'))
        run('build-io-variant',['cmake','--build',str(bins),'--target','io_demo'],root,env);demo('io',expected=2);p.write_text(original[p.name])
        variant('hsv',lambda s:s.replace('{179, 255, 255}','{90, 255, 255}'),'1')
        variant('hsv',lambda s:s.replace('{179, 255, 255}','{90, 255, 255}').replace('{0, 255, 255}','{0, 0, 255}'),'0')
        variant('threshold',lambda s:s.replace(', cv::THRESH_BINARY);',', cv::THRESH_BINARY_INV);',1),'255 255 0')
        adaptive=variant('threshold',lambda s:s.replace(', 11, 2);',', 11, -2);'))
        count=int(re.search(r'adaptive非零=(\d+)',adaptive).group(1));assert count<720
        variant('filter',lambda s:s.replace('cv::medianBlur(a, out, 3);','cv::blur(a, out, cv::Size(3,3));'),'28\n')
        bilateral=variant('filter',lambda s:s.replace('bilateral,5,25,25','bilateral,5,250,25'))
        assert int(re.search(r'中心=28,64,(\d+)',bilateral).group(1))<255
        variant('morphology',lambda s:s.replace('cv::Size(3,3)','cv::Size(7,7)'),'26 0')
        contour=variant('contour',lambda s:s.replace('std::vector<std::vector<cv::Point>> cs;','cv::Mat edges; cv::Canny(a,edges,50,150);\n    std::cout << "边缘像素=" << cv::countNonZero(edges) << "\\n";\n    std::vector<std::vector<cv::Point>> cs;').replace('findContours(a,cs','findContours(edges,cs'))
        assert '200' in contour
        variant('resize',lambda s:s.replace('cv::INTER_AREA','cv::INTER_NEAREST'),'40 20')
        features=variant('features',lambda s:s.replace('std::vector<cv::DMatch> matches;','cv::Mat moved,other; std::vector<cv::KeyPoint> kp2;\n    cv::Mat M=(cv::Mat_<double>(2,3)<<1,0,5,0,1,0);\n    cv::warpAffine(a,moved,M,a.size());\n    orb->detectAndCompute(moved,cv::noArray(),kp2,other);\n    if(other.empty()) return 3;\n    std::vector<cv::DMatch> matches;').replace('.match(desc,desc,matches)','.match(desc,other,matches)').replace('for(const auto& m:matches) if(m.distance!=0) return 2;','int consistent=0;\n    for(const auto& m:matches) {\n        auto delta=kp2[m.trainIdx].pt-kp[m.queryIdx].pt;\n        if(cv::norm(delta-cv::Point2f(5,0))<2) ++consistent;\n    }\n    std::cout << "几何近似平移=" << consistent << " 总数=" << matches.size() << "\\n";'))
        m=re.search(r'几何近似平移=(\d+) 总数=(\d+)',features);assert int(m[1])>int(m[2])*.6
        variant('pipeline',lambda s:s.replace('area < 100.0','area < 2000.0'),arguments=['scene.png'])
        assert np.array_equal(cv2.imread(str(out/'closed.png'),0),saved['closed'])
        assert np.array_equal(cv2.imread(str(out/'annotated.png')),saved['scene'])
        p=lab/'src/pipeline_demo.cpp';p.write_text(original[p.name].replace('cv::bitwise_or(low, high, mask);','mask=low;'))
        run('build-low-h',['cmake','--build',str(bins),'--target','pipeline_demo'],root,env)
        assert '1801,1800,1800 外轮廓=1 保留=1' in demo('pipeline',['scene.png']);p.write_text(original[p.name])
        cmake=lab/'CMakeLists.txt';base=cmake.read_text();cmake.write_text(base.replace('version mat','image mat'))
        (lab/'src/version_demo.cpp').rename(lab/'src/image_demo.cpp')
        run('rename-configure',['cmake','-S',str(lab),'-B',str(root/'rename')],root,env)
        run('rename-build',['cmake','--build',str(root/'rename'),'--target','image_demo'],root,env)
        run('renamed-version',[str(root/'rename/image_demo')],out,env)
        for mode in ['viewer','video-natural','video-escape']:
            name='viewer' if mode=='viewer' else 'video';sample='scene.png' if mode=='viewer' else 'scene.avi'
            output=run('window-'+mode,['xvfb-run','-a','-s','-screen 0 800x600x24',sys.executable,
                str(Path(__file__).resolve()),'--gui-worker',mode,str(bins/(name+'_demo')),sample,
                str(args.assets_dir/(mode+'.xwd'))],out,env)
            if mode=='video-natural':assert '读取帧数=20' in output
            if mode=='video-escape':assert 0<int(re.search(r'读取帧数=(\d+)',output)[1])<20
        assert np.array_equal(cv2.imread(str(out/'saved.png')),saved['scene'])
        env['ROS_LOG_DIR']=str(root/'ros-logs')
        run('ros-build',['colcon','--log-base',str(root/'log'),'build','--base-paths',str(bridge),
                         '--build-base',str(root/'ros-build'),'--install-base',str(root/'install')],root,env)
        install=root/'install/image_bridge_demo/lib/image_bridge_demo'
        assert '灰度=76' in run('roundtrip',[str(install/'roundtrip')],root,env)
        log=tempfile.TemporaryFile(mode='w+t')
        node=subprocess.Popen([str(install/'bridge_node')],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            run('ros-image-fields',['python3','-c','''import time
import rclpy
from sensor_msgs.msg import Image
rclpy.init();node=rclpy.create_node('image_check');incoming={};outgoing={}
def key(msg):return (msg.header.stamp.sec,msg.header.stamp.nanosec,msg.header.frame_id)
def receive_input(msg):incoming[key(msg)]=msg
def receive_output(msg):outgoing[key(msg)]=msg
one=node.create_subscription(Image,'image_in',receive_input,10)
two=node.create_subscription(Image,'image_out',receive_output,10)
deadline=time.monotonic()+8
while time.monotonic()<deadline:
 rclpy.spin_once(node,timeout_sec=.1)
 common=incoming.keys()&outgoing.keys()
 if common:
  tag=next(iter(common));a,b=incoming[tag],outgoing[tag]
  assert a.encoding=='bgr8' and b.encoding=='mono8'
  assert a.height==b.height==8 and a.width==b.width==8
  assert a.step==24 and b.step==8 and len(b.data)==64 and set(b.data)=={76}
  assert tag[2]=='camera_optical_frame' and tag[0]>0
  print('输入/输出Header相同，bgr8→mono8，64像素均76',tag);break
else:raise RuntimeError('未收到对应输入输出')
node.destroy_node();rclpy.shutdown()'''],root,env)
            run('cli-image-echo',['ros2','topic','echo','/image_out','sensor_msgs/msg/Image','--once'],root,env)
            run('bad-encoding',['ros2','topic','pub','--once','/image_in','sensor_msgs/msg/Image',
                '{height: 1, width: 1, encoding: invalid, step: 1, data: [0]}'],root,env)
            time.sleep(.8);log.seek(0);output=log.read();assert 'cv_bridge:' in output and 'invalid' in output
            run('ros-image-window',['xvfb-run','-a','-s','-screen 0 800x600x24',sys.executable,
                str(Path(__file__).resolve()),'--gui-worker','ros','unused','unused',
                str(args.assets_dir/'ros-image.xwd')],root,env)
        finally:
            stop(node);log.seek(0);records.append({'step':'bridge-node-log','returncode':node.returncode,'output':log.read()});log.close()
            run('stop-own-domain-daemon',['ros2','daemon','stop'],root,env)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'scope':'OpenCV4.6/Jazzy；真实独立窗口与视频文件，相机硬件未验证','records':records},ensure_ascii=False,indent=2)+'\n')
    print('完成',len(records),'条记录')


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--gui-worker':gui_worker(*sys.argv[2:])
    else:main()
