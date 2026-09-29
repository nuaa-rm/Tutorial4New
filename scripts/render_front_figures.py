#!/usr/bin/env python3
"""把实际生成的教学灰度图与人工时刻表画成可检查的教材图。"""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import cv2

c=argparse.ArgumentParser(description=__doc__);c.add_argument('--project',type=Path,required=True);c.add_argument('--work',type=Path,required=True);c.add_argument('--output-dir',type=Path,required=True);c.add_argument('--publish-checked',action='store_true');a=c.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True);suffix='revised' if a.publish_checked else 'candidate'
font=FontProperties(fname='/run/host/usr/share/texmf-dist/fonts/opentype/public/fandol/FandolSong-Regular.otf',size=11)
plt.rcParams.update({'pdf.compression':0,'font.size':11,'axes.edgecolor':'#0091a0','axes.labelcolor':'#0091a0','xtick.color':'#0091a0','ytick.color':'#0091a0'})
fig,axes=plt.subplots(1,3,figsize=(9,2.2),constrained_layout=True)
for ax,name,title in zip(axes,['global_short','rolling_short','global_long'],['全局：1 ms','逐行：1 ms，行间跨度8 ms','全局：6 ms']):
 image=cv2.imread(str(a.work/'out'/f'{name}.png'),cv2.IMREAD_UNCHANGED);assert image is not None
 ax.imshow(image,cmap='gray',vmin=0,vmax=255,interpolation='nearest');ax.set_title(title,fontproperties=font);ax.set_xlabel('像素 x',fontproperties=font);ax.set_ylabel('像素 y',fontproperties=font)
fig.suptitle('同一理想移动竖条，固定图像亮度尺度；不是实拍',fontproperties=font)
fig.savefig(a.output_dir/f'front_motion_{suffix}.pdf');plt.close(fig)
rows=list(csv.DictReader((a.project/'times.csv').open()));fig,ax=plt.subplots(figsize=(8,3.4),constrained_layout=True)
for i,row in enumerate(rows):
 y=2-i;times=[float(row[key]) for key in ['sample_ms','result_ms','execute_ms']];ax.plot(times,[y]*3,color='#0091a0',linewidth=1.6)
 for x,marker in zip(times,['^','o','s']):ax.scatter([x],[y],marker=marker,color='#0091a0',s=55);ax.text(x,y+.18,f'{x:g}',ha='center')
ax.set_yticks([2,1,0],['帧0','帧1','帧2'],fontproperties=font);ax.set_xlim(-4,70);ax.set_ylim(-.5,2.65);ax.set_xlabel('同一演示时钟（ms）',fontproperties=font);ax.set_title('三角：采样　圆：结果　方：执行；每帧35 / 45 ms',fontproperties=font)
ax.spines[['top','right']].set_visible(False);fig.savefig(a.output_dir/f'front_time_{suffix}.pdf');plt.close(fig);print(a.output_dir)
