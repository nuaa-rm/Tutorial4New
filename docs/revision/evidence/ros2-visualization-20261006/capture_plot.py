import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

DEMO=Path('/home/mijiao/Apps/Tutorial4New/02-专项技术栈/examples/ros2/visualization-demo')
p=argparse.ArgumentParser(); p.add_argument('--mode', choices=['all','plot','screen'], default='all'); p.add_argument('--output', type=Path, required=True); args=p.parse_args()
out=args.output; out.mkdir(parents=True,exist_ok=True)
if args.mode=='screen':
    from PyQt5.QtWidgets import QApplication
    app=QApplication([])
    assert app.primaryScreen().grabWindow(0).save(str(out/'screen.png'))
elif args.mode=='plot':
    import rclpy
    from rqt_plot.plot_widget import PlotWidget
    from rqt_plot.data_plot import DataPlot
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QIcon
    app=QApplication([]); font=app.font(); font.setPointSize(14); app.setFont(font); QIcon.setThemeName("Humanity"); rclpy.init(); node=rclpy.create_node('capture_rqt_plot')
    deadline=time.monotonic()+10
    while '/viz/pose' not in dict(node.get_topic_names_and_types()):
        assert time.monotonic()<deadline
        rclpy.spin_once(node,timeout_sec=.1)
    widget=PlotWidget(node, initial_topics=['/viz/signal/data','/viz/pose/pose/position/x'])
    data=DataPlot(widget); data.set_autoscale(x=False); data.set_autoscale(y=DataPlot.SCALE_EXTEND|DataPlot.SCALE_VISIBLE); data.set_xlim([0,10]); widget.switch_data_plot_widget(data)
    widget.resize(1180,620); widget.show(); app.processEvents(); data.set_xlim([0,10]); data.set_ylim([-1.2,1.2]); 
    for _,label in data._data_plot_widget._plot_widget.getPlotItem().legend.items: label.setText(label.text,size="16pt")
    deadline=time.monotonic()+12
    while time.monotonic()<deadline:
        rclpy.spin_once(node,timeout_sec=.01); app.processEvents()
    counts={}
    for topic,curve in data._data_plot_widget._curves.items():
        x,y=curve.getData(); assert len(y)>=80; counts[topic]=len(y)
    assert widget.grab().save(str(out/'rqt_plot.png'))
    (out/'plot-data.json').write_text(json.dumps(counts,indent=2)+'\n')
    widget.clean_up_subscribers(); widget.close(); node.destroy_node(); rclpy.shutdown()
else:
    processes=[]; logs=[]
    def start(name,cmd,extra=None):
        log=(out/(name+'.txt')).open('w'); logs.append(log)
        env=os.environ.copy(); env.update(extra or {})
        proc=subprocess.Popen(cmd,cwd=DEMO,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True); processes.append(proc); return proc
    def stop(proc):
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            try: proc.wait(timeout=8)
            except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGTERM); proc.wait(timeout=5)
    try:
        start('xvfb',['Xvfb',':99','-screen','0','1400x950x24','-nolisten','tcp'])
        time.sleep(1)
        env={'DISPLAY':':99','LIBGL_ALWAYS_SOFTWARE':'1','QT_X11_NO_MITSHM':'1','XDG_CONFIG_HOME':str(out/'config')}
        start('data',['python3',str(DEMO/'data_node.py')]); time.sleep(2)
        plot=start('plot',['python3',__file__,'--mode','plot','--output',str(out)],env)
        assert plot.wait(timeout=25)==0
        print('图形截图完成',flush=True)
    finally:
        for proc in reversed(processes): stop(proc)
        for log in logs: log.close()
