"""在独立 Xvfb 显示中验证真实 rqt 插件；参数为节点可执行文件和 XWD 输出路径。"""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from python_qt_binding.QtCore import QObject, Qt
from python_qt_binding.QtWidgets import QApplication,QMainWindow,QSplitter
from python_qt_binding.QtTest import QTest
import rclpy
from rqt_topic.topic_widget import TopicWidget
from rqt_publisher.publisher import Publisher

app=QApplication([])
font=app.font()
font.setPointSize(14)
app.setFont(font)
rclpy.init()
node=rclpy.create_node('textbook_rqt_check')
window=QMainWindow()
window.setWindowTitle('ROS2 textbook verification - rqt plugins')
splitter=QSplitter(Qt.Vertical)
window.setCentralWidget(splitter)
class Context(QObject):
    def __init__(self):super().__init__();self.node=node
    def serial_number(self):return 1
    def add_widget(self,widget):splitter.addWidget(widget)
context=Context()
publisher=Publisher(context)
monitor=TopicWidget(node,selected_topics=[('/receive',['std_msgs/msg/String']),('/send',['std_msgs/msg/String']),('/my_msg',['my_msgs/msg/My']),('/timer_',['std_msgs/msg/String'])])
splitter.addWidget(monitor)
monitor.start()
window.resize(1200,900)
window.show()
def advance(seconds):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        rclpy.spin_once(node,timeout_sec=0.01)
        app.processEvents()
def until(test,seconds=15):
    end=time.monotonic()+seconds
    while not test():
        if time.monotonic()>end:raise AssertionError('GUI condition timed out')
        advance(.1)
def launch():
    return subprocess.Popen([sys.argv[1]],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
proc=launch()
try:
    until(lambda:'/send' in monitor._topics and publisher._widget.type_combo_box.isEnabled())
    publisher._widget.topic_combo_box.setEditText('/receive')
    publisher._widget.type_combo_box.setEditText('std_msgs/msg/String')
    publisher._widget.frequency_combo_box.setEditText('1')
    QTest.mouseClick(publisher._widget.add_publisher_button,Qt.LeftButton)
    until(lambda:len(publisher._publishers)==1)
    model=publisher._widget.publisher_tree_widget.model()
    top=model.item(0,0)
    top.child(0,3).setText("'armor_found'")
    top.setCheckState(Qt.Checked)
    publisher._widget.publisher_tree_widget.expandAll()
    for info in monitor._topics.values():info['item'].setCheckState(0,Qt.Checked)
    monitor.topics_tree_widget.expandAll()
    until(lambda:monitor._tree_items['/send/data'].text(4)=="'I can hear:armor_found'")
    advance(2)
    assert monitor._tree_items['/my_msg/yaw'].text(4)=='0.25'
    subprocess.run(['xwd','-silent','-id',str(int(window.winId())),'-out',sys.argv[2]],check=True)
    print('rqt Publisher -> receive -> my_node -> send -> rqt Monitor: I can hear:armor_found',flush=True)
    print('my_msg yaw:',monitor._tree_items['/my_msg/yaw'].text(4),flush=True)
    os.killpg(proc.pid,signal.SIGINT);proc.wait(timeout=5)
    advance(2)
    assert node.count_publishers('/send')==0
    old=monitor._tree_items['/send/data'].text(4) if '/send/data' in monitor._tree_items else None
    proc=launch()
    until(lambda:node.count_publishers('/send')==1)
    until(lambda:'/send' in monitor._topics)
    monitor._topics['/send']['item'].setCheckState(0,Qt.Checked)
    until(lambda:monitor._tree_items['/send/data'].text(4)=="'I can hear:armor_found'")
    print('publisher count after stop: 0; after restart: 1; reply recovered',flush=True)
finally:
    if proc.poll() is None:os.killpg(proc.pid,signal.SIGINT);proc.wait(timeout=5)
    publisher.shutdown_plugin()
    monitor.shutdown_plugin()
    node.destroy_node()
    rclpy.shutdown()
    window.close()
