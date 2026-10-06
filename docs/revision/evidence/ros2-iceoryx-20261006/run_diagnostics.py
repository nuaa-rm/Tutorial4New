import json, os, signal, subprocess, time
from pathlib import Path
root = Path('/home/mijiao/Apps/Tutorial4New')
demo = root / '02-专项技术栈/examples/ros2/image-path-demo'
out = root / 'docs/revision/evidence/ros2-iceoryx-20261006'
config = demo/'config/cyclone-iceoryx.xml'
if subprocess.run(['pgrep','-x','iox-roudi'],stdout=subprocess.DEVNULL).returncode==0:
    raise RuntimeError('已有 RouDi，不能接管')
before = sorted(p.name for p in Path('/dev/shm').iterdir())
log = (out/'roudi-diagnostics.log').open('w')
roudi=subprocess.Popen(['iox-roudi','-c',str(demo/'config/roudi.toml'),'-l','info'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
try:
    end=time.monotonic()+15
    while 'RouDi is ready' not in (out/'roudi-diagnostics.log').read_text():
        if roudi.poll() is not None or time.monotonic()>end: raise RuntimeError('RouDi 未就绪')
        time.sleep(0.1)
    for name, fixed, shm, loan in [('trace-dynamic-shm',False,True,False),('trace-fixed-shm-loan',True,True,True)]:
        print(name,flush=True)
        if fixed:
            cmd=['python3',str(demo/'compare_fixed.py'),'--publish-mode','loan' if loan else 'regular']
        else:
            cmd=['python3',str(demo/'compare.py'),'--width','1440','--height','1080','--channels','3','--rmws','rmw_cyclonedds_cpp','--modes','separate']
        cmd+=['--output',str(out/name),'--rate','10','--frames','20','--repeat','1','--domain','89']
        if shm: cmd+=['--cyclone-config',str(config)]
        subprocess.run(cmd,check=True,env=dict(os.environ,LD_PRELOAD='/tmp/tutorial4new-iceoryx-20261006-ws/trace_iceoryx.so'))
finally:
    if roudi.poll() is None:
        os.killpg(roudi.pid,signal.SIGINT)
        try: roudi.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(roudi.pid,signal.SIGKILL); roudi.wait()
    log.close()
    after=sorted(p.name for p in Path('/dev/shm').iterdir())
    (out/'shm-after-diagnostics.json').write_text(json.dumps(dict(before=before,after=after,added=sorted(set(after)-set(before)),roudi_returncode=roudi.returncode),indent=2)+'\n')
