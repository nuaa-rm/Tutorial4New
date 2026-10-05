#!/usr/bin/env python3
"""在已加载 ROS2 Humble 的环境中核验教学项目；所有构建和修改只发生在临时副本。"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'02-专项技术栈/examples/ros2'
records=[]
live=[]

def stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid,signal.SIGINT)
        try:proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            proc.wait(timeout=5)

def run(cmd,cwd,env,expected=0,timeout=40):
    proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
    try:out,_=proc.communicate(timeout=timeout); code=proc.returncode
    except subprocess.TimeoutExpired:
        stop(proc);out,_=proc.communicate();code=124
    record={'command':cmd,'returncode':code,'expected':expected,'output':out}
    records.append(record)
    print(f'{len(records)}: {cmd} -> {code}',flush=True)
    if code!=expected:raise RuntimeError(out)
    return out

def background(cmd,cwd,env):
    log=tempfile.TemporaryFile(mode='w+t')
    proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,text=True,start_new_session=True)
    live.append((proc,log))
    return proc,log

def logged(proc,log,label):
    stop(proc);log.seek(0);out=log.read()
    records.append({'background':label,'returncode':proc.returncode,'output':out})
    print(f'{label} stopped: {proc.returncode}',flush=True)
    return out

def environment(folder,base):
    code='source "'+str(folder/'install/setup.bash')+'"; env -0'
    out=subprocess.check_output(['bash','-c',code],env=base)
    return dict(x.split('=',1) for x in out.decode().split('\0') if '=' in x)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    base=os.environ.copy()
    assert base.get('ROS_DISTRO')=='humble','请先 source /opt/ros/humble/setup.bash'
    base.update(ROS_DOMAIN_ID='76',ROS_LOCALHOST_ONLY='1',RCUTILS_COLORIZED_OUTPUT='0',PYTHONUNBUFFERED='1')
    for key in ['ROS_AUTOMATIC_DISCOVERY_RANGE','ROS_STATIC_PEERS','RMW_IMPLEMENTATION']:base.pop(key,None)
    try:
        with tempfile.TemporaryDirectory(prefix='ros-textbook-') as temp:
            folder=Path(temp)
            (folder/'src').mkdir()
            for domain in ['76','77']:
                run(['ros2','daemon','stop'],folder,base|{'ROS_DOMAIN_ID':domain})
            for name in ['my_msgs','my_package']:
                shutil.copytree(SOURCE/'basic-interfaces-demo'/name,folder/'src'/name)
            shutil.copytree(SOURCE/'training_tools',folder/'src/training_tools')
            run(['rosdep','check','--from-paths','src','--ignore-src'],folder,base)
            run(['colcon','build','--cmake-args','-DBUILD_TESTING=ON','-DCMAKE_BUILD_TYPE=Debug','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON'],folder,base,timeout=100)
            env=environment(folder,base)
            run(['colcon','test','--packages-select','training_tools'],folder,env)
            run(['colcon','test-result','--verbose'],folder,env)
            assert (folder/'build/training_tools/compile_commands.json').exists()
            executable=folder/'install/my_package/lib/my_package/my_node'
            proc,log=background([str(executable)],folder,env)
            msg=run(['ros2','topic','echo','/my_msg','my_msgs/msg/My','--once'],folder,env)
            assert all(s in msg for s in ['camera_link','yaw: 0.25','detect_success: true'])
            reader,rlog=background(['ros2','topic','echo','/send','std_msgs/msg/String','--once'],folder,env)
            time.sleep(4)
            run(['ros2','topic','pub','--once','/receive','std_msgs/msg/String','{data: armor_found}'],folder,env)
            reader.wait(timeout=12);rlog.seek(0);reply=rlog.read()
            assert 'I can hear:armor_found' in reply
            records.append({'check':'string callback round trip','output':reply})
            hz=run(['ros2','topic','hz','/timer_','--window','5'],folder,env,expected=124,timeout=12)
            assert re.search(r'average rate: 1\.',hz) or re.search(r'average rate: 0\.99',hz)
            logged(proc,log,'basic node 1Hz')
            run(['ros2','topic','pub','--once','--wait-matching-subscriptions','0','/receive','std_msgs/msg/String','{data: stopped}'],folder,env)
            # A real interface change also rebuilds its consumer.
            msgs=folder/'src/my_msgs/msg/My.msg'
            msgs.write_text(msgs.read_text()+'float64 distance # 米\n')
            cpp=folder/'src/my_package/src/my_node.cpp'
            cpp.write_text(cpp.read_text().replace('milliseconds(1000)','milliseconds(500)').replace('self_msg.yaw = 0.25;','self_msg.distance = 3.5;\n    self_msg.yaw = 0.25;'))
            run(['colcon','build','--packages-up-to','my_package'],folder,base,timeout=80)
            env=environment(folder,base)
            assert 'float64 distance' in run(['ros2','interface','show','my_msgs/msg/My'],folder,env)
            proc,log=background([str(executable)],folder,env)
            assert 'distance: 3.5' in run(['ros2','topic','echo','/my_msg','my_msgs/msg/My','--once'],folder,env)
            hz=run(['ros2','topic','hz','/timer_','--window','5'],folder,env,expected=124,timeout=10)
            assert re.search(r'average rate: (2\.|1\.99)',hz)
            logged(proc,log,'basic node 2Hz and distance')
            # QoS compatibility, with the sender independent of matching subscribers.
            for offered,requested,expected in [('best_effort','reliable',124),('best_effort','best_effort',0),('reliable','best_effort',0)]:
                proc,log=background(['ros2','topic','pub','/qos_demo','std_msgs/msg/String','{data: hello}','--rate','1','--wait-matching-subscriptions','0','--qos-reliability',offered],folder,env)
                out=run(['ros2','topic','echo','/qos_demo','std_msgs/msg/String','--qos-reliability',requested,'--once'],folder,env,expected=expected,timeout=6)
                if expected==0:assert 'data: hello' in out
                else:assert 'incompatible QoS' in out
                run(['ros2','topic','info','/qos_demo','--verbose'],folder,env)
                logged(proc,log,'QoS '+offered+' -> '+requested)
            # Ordinary demo interfaces, two local domains, and Cyclone.
            talker=Path('/opt/ros/humble/lib/demo_nodes_cpp/talker')
            listener=Path('/opt/ros/humble/lib/demo_nodes_cpp/listener')
            proc,log=background([str(talker)],folder,env)
            different=env|{'ROS_DOMAIN_ID':'77'}
            assert 'I heard:' not in run([str(listener)],folder,different,expected=124,timeout=3)
            assert 'I heard:' in run([str(listener)],folder,env,expected=124,timeout=3)
            run(['ros2','node','list'],folder,env)
            run(['ros2','topic','info','/chatter'],folder,env)
            logged(proc,log,'talker domain 76')
            cyclone=env|{'RMW_IMPLEMENTATION':'rmw_cyclonedds_cpp'}
            proc,log=background([str(talker)],folder,cyclone)
            assert 'I heard:' in run([str(listener)],folder,cyclone,expected=124,timeout=4)
            logged(proc,log,'Cyclone talker')
            server=Path('/opt/ros/humble/lib/demo_nodes_cpp/add_two_ints_server')
            proc,log=background([str(server)],folder,env)
            run(['ros2','service','list','-t'],folder,env)
            run(['ros2','interface','show','example_interfaces/srv/AddTwoInts'],folder,env)
            for value in ['{a: 2, b: 3}','{a: -4, b: 9}']:
                assert 'sum=5' in run(['ros2','service','call','/add_two_ints','example_interfaces/srv/AddTwoInts',value],folder,env)
            logged(proc,log,'AddTwoInts')
            # Launch parameters, remapping, string typing and conditional observer.
            for robot,text in [('red','tracking'),('blue','true')]:
                proc,log=background(['ros2','launch','training_tools','heartbeat.launch.py','robot:='+robot,'text:='+text],folder,env)
                assert 'data: '+("'true'" if text=='true' else text) in run(['ros2','topic','echo','/'+robot+'/health','std_msgs/msg/String','--once'],folder,env)
                assert 'String value is: '+text in run(['ros2','param','get','/'+robot+'/heartbeat','text'],folder,env)
                logged(proc,log,'heartbeat launch '+robot)
            proc,log=background(['ros2','launch','training_tools','team.launch.py'],folder,env)
            time.sleep(4)
            assert 'data: team ready' in run(['ros2','topic','echo','/red/health','std_msgs/msg/String','--once'],folder,env)
            assert 'Observer exited; heartbeat keeps running.' in logged(proc,log,'team red')
            team=folder/'src/training_tools/launch/team.launch.py'
            team.write_text(team.read_text().replace("'/red/health'","['/', LaunchConfiguration('robot'), '/health']"))
            run(['colcon','build','--packages-select','training_tools'],folder,base)
            env=environment(folder,base)
            for watch in ['true','false']:
                proc,log=background(['ros2','launch','training_tools','team.launch.py','robot:=blue','watch:='+watch],folder,env)
                time.sleep(3)
                assert 'data: team ready' in run(['ros2','topic','echo','/blue/health','std_msgs/msg/String','--once'],folder,env)
                out=logged(proc,log,'team blue watch='+watch)
                assert ('Observer exited; heartbeat keeps running.' in out)==(watch=='true')
            heartbeat=folder/'install/training_tools/lib/training_tools/heartbeat'
            # Publishing continues even when ordinary logs are hidden.
            for level in ['debug','warn']:
                proc,log=background([str(heartbeat),'--ros-args','--log-level',level],folder,env)
                hz=run(['ros2','topic','hz','/status','--window','10'],folder,env,expected=124,timeout=8)
                assert re.search(r'average rate: (5\.|4\.99)',hz)
                out=logged(proc,log,'log level '+level)
                assert ('first heartbeat' in out)==(level=='debug')
                if level=='debug':assert 'publish: ready' in out and 'heartbeat alive' in out
            # Independent log destination and the 1000ms throttle exercise.
            cpp=folder/'src/training_tools/src/heartbeat.cpp'
            cpp.write_text(cpp.read_text().replace('*get_clock(), 2000','*get_clock(), 1000'))
            test=folder/'src/training_tools/test/test_interval.cpp'
            test.write_text(test.read_text().replace('1000','500').replace('1001','501'))
            run(['colcon','build','--packages-select','training_tools'],folder,base)
            run(['colcon','test','--packages-select','training_tools'],folder,env)
            run(['colcon','test-result','--verbose'],folder,env)
            logging_env=env|{'ROS_LOG_DIR':str(folder/'experiment_logs'),'RCUTILS_CONSOLE_OUTPUT_FORMAT':'[{severity}] [{name}] {message}','RCUTILS_LOGGING_BUFFERED_STREAM':'0'}
            proc,log=background([str(heartbeat),'--ros-args','--log-level','debug'],folder,logging_env)
            time.sleep(3.5)
            out=logged(proc,log,'1000ms log throttle')
            assert 3<=out.count('heartbeat alive')<=4 and out.count('publish: ready')>=15
            assert list((folder/'experiment_logs').rglob('*.log'))
            # Separate IDE-style build, changed source, old install, then install refresh.
            cpp.write_text(cpp.read_text().replace('"text", "ready"','"text", "from_debug"'))
            run(['cmake','-S',str(folder/'src/training_tools'),'-B',str(folder/'ide-build'),'-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=OFF'],folder,env)
            run(['cmake','--build',str(folder/'ide-build')],folder,env)
            for target,text in [(folder/'ide-build/heartbeat','from_debug'),(heartbeat,'ready')]:
                proc,log=background([str(target)],folder,env)
                assert 'data: '+text in run(['ros2','topic','echo','/status','std_msgs/msg/String','--once'],folder,env)
                logged(proc,log,'build/install difference '+text)
            trace=run(['gdb','-q','-batch','-ex','set debuginfod enabled off','-ex','break heartbeat.cpp:16','-ex','run','-ex','bt','--args',str(folder/'ide-build/heartbeat')],folder,env)
            assert 'hit Breakpoint' in trace and 'operator()' in trace and 'Executor' in trace
            run(['colcon','build','--packages-select','training_tools'],folder,base)
            proc,log=background([str(heartbeat)],folder,env)
            assert 'data: from_debug' in run(['ros2','topic','echo','/status','std_msgs/msg/String','--once'],folder,env)
            logged(proc,log,'updated install')
            # Replace the complete rules for the auto-ament variant.
            package=folder/'src/training_tools/package.xml'
            package.write_text(package.read_text().replace('<buildtool_depend>ament_cmake</buildtool_depend>','<buildtool_depend>ament_cmake_auto</buildtool_depend>'))
            shutil.copyfile(folder/'src/training_tools/cmake/Auto.cmake',folder/'src/training_tools/CMakeLists.txt')
            run(['colcon','build','--packages-select','training_tools','--cmake-clean-cache','--cmake-args','-DBUILD_TESTING=ON'],folder,base)
            env=environment(folder,base)
            run(['colcon','test','--packages-select','training_tools'],folder,env)
            run(['colcon','test-result','--verbose'],folder,env)
            proc,log=background(['ros2','launch','training_tools','heartbeat.launch.py','robot:=red','text:=auto_ready'],folder,env)
            assert 'data: auto_ready' in run(['ros2','topic','echo','/red/health','std_msgs/msg/String','--once'],folder,env)
            logged(proc,log,'auto ament installed resources')
            for domain in ['76','77']:
                run(['ros2','daemon','stop'],folder,base|{'ROS_DOMAIN_ID':domain})
    finally:
        for proc,log in live:
            if proc.poll() is None:
                logged(proc,log,'cleanup after interrupted check')
            log.close()
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps({'ROS_DISTRO':base.get('ROS_DISTRO'),'records':records},ensure_ascii=False,indent=2)+'\n')
    print(f'{len(records)} records passed; {args.output}',flush=True)

if __name__=='__main__':main()
