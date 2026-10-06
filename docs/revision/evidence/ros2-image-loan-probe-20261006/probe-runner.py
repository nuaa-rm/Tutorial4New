from pathlib import Path
import argparse,json,os,re,subprocess,sys
ws=Path('/tmp/tutorial4new-image-loan-probe-20261006-ws')
sys.path.insert(0,str(ws/'src/image_path_demo'))
from compare import zenoh_router
from compare_images import shared_pool
out=Path('/home/mijiao/Apps/Tutorial4New/docs/revision/evidence/ros2-image-loan-probe-20261006/runtime')
out.mkdir(exist_ok=False)
prefix=Path(subprocess.check_output(['ros2','pkg','prefix','image_path_demo'],text=True).strip())
share=prefix/'share/image_path_demo'
args=argparse.Namespace(output=out,share=share,profiles=['default','shared'],rmws=['rmw_cyclonedds_cpp'],zenoh_port=17877,zenoh_shm_pool_mib=6,zenoh_shm=False)
base=os.environ.copy()
for key in list(base):
 if key.startswith(('ZENOH_','RMW_ZENOH_')) or key in ('CYCLONEDDS_URI','FASTRTPS_DEFAULT_PROFILES_FILE','FASTDDS_DEFAULT_PROFILES_FILE','RMW_FASTRTPS_USE_QOS_FROM_XML','RMW_FASTRTPS_PUBLICATION_MODE','ROS_DISABLE_LOANED_MESSAGES'):
  base.pop(key,None)
base.update(ROS_DOMAIN_ID='91',ROS_LOCALHOST_ONLY='1')
rows=[]
cases=[('rmw_fastrtps_cpp','default',0),('rmw_fastrtps_cpp','shared',1),('rmw_fastrtps_cpp','disabled',0),('rmw_cyclonedds_cpp','default',0),('rmw_cyclonedds_cpp','shared',1),('rmw_zenoh_cpp','default',0),('rmw_zenoh_cpp','shared',0)]
with shared_pool(args):
 for rmw,profile,expected in cases:
  env=dict(base,RMW_IMPLEMENTATION=rmw)
  if rmw=='rmw_fastrtps_cpp' and profile!='default':
   env.update(FASTRTPS_DEFAULT_PROFILES_FILE=str(share/'config/fastdds-loan.xml'),RMW_FASTRTPS_USE_QOS_FROM_XML='1')
  if profile=='disabled':env['ROS_DISABLE_LOANED_MESSAGES']='1'
  if rmw=='rmw_cyclonedds_cpp' and profile=='shared':env['CYCLONEDDS_URI']='file://'+str(share/'config/cyclone-iceoryx.xml')
  args.zenoh_shm=profile=='shared'
  name=f'{rmw}-{profile}'
  with zenoh_router(args,rmw,env,out/f'{name}-router.log') as router:
   run=subprocess.run([str(prefix/'lib/image_path_demo/loan_probe')],env=env,cwd=ws,capture_output=True,text=True,timeout=25)
   (out/f'{name}.log').write_text(run.stdout+run.stderr)
   assert run.returncode==0,(name,run.stdout,run.stderr)
   cap=json.loads(re.findall(r'LOAN (\{[^\n]*\})',run.stdout)[0])
   pub=json.loads(re.findall(r'PUBLISHED (\{[^\n]*\})',run.stdout)[0])
   assert cap=={'image':0,'fixed_image':expected},(name,cap)
   assert pub=={'image':1,'fixed_image':1},(name,pub)
   assert 'Error creating lazy ShmProvider' not in run.stdout+run.stderr,name
   row=dict(rmw=rmw,profile=profile,capabilities=cap,publish_calls=pub,returncode=run.returncode)
   rows.append(row)
   print(json.dumps(row),flush=True)
(out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
