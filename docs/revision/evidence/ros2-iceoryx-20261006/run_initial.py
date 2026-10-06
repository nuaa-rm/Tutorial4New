import json, os, signal, subprocess, time
from pathlib import Path
root = Path('/home/mijiao/Apps/Tutorial4New')
demo = root / '02-专项技术栈/examples/ros2/image-path-demo'
out = root / 'docs/revision/evidence/ros2-iceoryx-20261006'
if subprocess.run(['pgrep', '-x', 'iox-roudi'], stdout=subprocess.DEVNULL).returncode == 0:
    raise RuntimeError('已有 RouDi，不能接管')
before = sorted(p.name for p in Path('/dev/shm').iterdir())
(out / 'shm-before.json').write_text(json.dumps(before, indent=2)+'\n')
log = (out / 'roudi-initial.log').open('w')
roudi = subprocess.Popen(['iox-roudi', '-c', str(demo / 'config/roudi.toml'), '-l', 'info'], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
try:
    end = time.monotonic()+15
    while 'RouDi is ready' not in (out/'roudi-initial.log').read_text():
        if roudi.poll() is not None or time.monotonic()>end:
            raise RuntimeError('RouDi 未就绪')
        time.sleep(0.1)
    print('RouDi 已就绪', flush=True)
    env = dict(os.environ, RMW_IMPLEMENTATION='rmw_cyclonedds_cpp', ROS_LOCALHOST_ONLY='1', ROS_DOMAIN_ID='89', CYCLONEDDS_URI='file://' + str(demo/'config/cyclone-iceoryx.xml'))
    for key in ('FASTRTPS_DEFAULT_PROFILES_FILE', 'FASTDDS_DEFAULT_PROFILES_FILE', 'ROS_DISABLE_LOANED_MESSAGES'):
        env.pop(key, None)
    probe = subprocess.run(['ros2','run','image_path_demo','loan_probe'], env=env, capture_output=True, text=True, timeout=20)
    (out/'loan-probe-iceoryx.log').write_text(probe.stdout+probe.stderr)
    print(probe.stdout.strip(), flush=True)
    probe.check_returncode()
    subprocess.run(['python3', str(demo/'compare_fixed.py'), '--output', str(out/'fixed-full-check'), '--cyclone-config', str(demo/'config/cyclone-iceoryx.xml'), '--rate','10','--frames','20','--repeat','1','--verify-full'], check=True)
finally:
    if roudi.poll() is None:
        os.killpg(roudi.pid, signal.SIGINT)
        try: roudi.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(roudi.pid,signal.SIGKILL); roudi.wait()
    log.close()
    after = sorted(p.name for p in Path('/dev/shm').iterdir())
    (out/'shm-after-initial.json').write_text(json.dumps(dict(before=before, after=after, added=sorted(set(after)-set(before)), roudi_returncode=roudi.returncode),indent=2)+'\n')
