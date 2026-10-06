import json, os, re, signal, subprocess, time
from pathlib import Path
root=Path('/home/mijiao/Apps/Tutorial4New')
out=root/'docs/revision/evidence/ros2-iceoryx-20261006'
prefix=Path(subprocess.check_output(['ros2','pkg','prefix','--share','image_path_demo'],text=True).strip())
if subprocess.run(['pgrep','-x','iox-roudi'],stdout=subprocess.DEVNULL).returncode==0: raise RuntimeError('已有 RouDi')
logs={};children={}
with (out/'roudi-manual.log').open('w') as log:
    roudi=subprocess.Popen(['iox-roudi','-c',str(prefix/'config/roudi.toml')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try:
        end=time.monotonic()+15
        while 'RouDi is ready' not in (out/'roudi-manual.log').read_text():
            if roudi.poll() is not None or time.monotonic()>end: raise RuntimeError('RouDi 未就绪')
            time.sleep(0.1)
        env=dict(os.environ,RMW_IMPLEMENTATION='rmw_cyclonedds_cpp',ROS_DOMAIN_ID='89',ROS_LOCALHOST_ONLY='1',CYCLONEDDS_URI='file://'+str(prefix/'config/cyclone-iceoryx.xml'),ROS_DISABLE_LOANED_MESSAGES='0')
        negative=subprocess.run(['ros2','run','image_path_demo','fixed_image','--ros-args','-p','role:=send'],env=dict(env,ROS_DISABLE_LOANED_MESSAGES='1'),capture_output=True,text=True,timeout=15)
        (out/'fixed-disable-loan.log').write_text(negative.stdout+negative.stderr)
        assert negative.returncode==2 and '"can_loan":0' in negative.stdout
        for role in ('receive','send'):
            logs[role]=(out/f'manual-{role}.log').open('w')
            command=['ros2','run','image_path_demo','fixed_image','--ros-args','-r',f'__node:=fixed_{role}','-p',f'role:={role}']
            command+=['-p','verify_full:=true'] if role=='receive' else ['-p','rate:=10.0','-p','frames:=20']
            children[role]=subprocess.Popen(command,env=env,stdout=logs[role],stderr=subprocess.STDOUT,start_new_session=True)
        end=time.monotonic()+30
        while 'FIXED_DONE 20' not in (out/'manual-send.log').read_text():
            if any(c.poll() is not None for c in children.values()) or time.monotonic()>end: raise RuntimeError('收发未完成')
            time.sleep(0.1)
        time.sleep(1)
    finally:
        for role in ('send','receive'):
            if role in children and children[role].poll() is None:
                os.killpg(children[role].pid,signal.SIGINT); children[role].wait(timeout=10)
            if role in logs: logs[role].close()
        if roudi.poll() is None:
            os.killpg(roudi.pid,signal.SIGINT); roudi.wait(timeout=10)
rows={role:json.loads(re.findall(r'FIXED_STATS (\{[^\n]*\})',(out/f'manual-{role}.log').read_text())[-1]) for role in children}
assert rows['receive']['count']==rows['send']['count']==20 and rows['receive']['bad_frames']==0
(out/'manual-summary.json').write_text(json.dumps(dict(stats=rows,disable_loan_returncode=negative.returncode,returncodes={r:c.returncode for r,c in children.items()},roudi_returncode=roudi.returncode),indent=2)+'\n')
print('手动 ros2 run 路径：20 帧完整像素通过；禁用借出正确退出 2；再次启用后正常收发')
