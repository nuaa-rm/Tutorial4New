#!/usr/bin/env python3
"""只排版实际运行中间图，不改像素或伪造处理结果。"""
import argparse
from pathlib import Path


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--assets-dir',type=Path,required=True)
    cli.add_argument('--output-dir',type=Path,required=True)
    cli.add_argument('--font',type=Path,required=True)
    cli.add_argument('--publish-checked',action='store_true')
    args=cli.parse_args()
    import cv2
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont(str(args.font))
    font=font_manager.FontProperties(fname=str(args.font)).get_name()
    # 本机组合的低位深索引图压缩会错行；直接嵌入原像素，避免失真。
    plt.rcParams.update({'font.family':font,'font.size':12,'pdf.fonttype':3,'pdf.compression':0})
    fig,axes=plt.subplots(2,3,figsize=(9,5.4),layout='constrained')
    panels=[('scene','① BGR 合成输入'),('mask','② 两段红色掩膜：3600'),
            ('opened','③ 开运算去点：3599'),('closed','④ 闭运算补孔：3600'),
            ('edges','⑤ Canny 边缘（作对照）'),('annotated','⑥ 两个旋转矩形')]
    for ax,(name,label) in zip(axes.flat,panels):
        image=cv2.imread(str(args.assets_dir/(name+'.png')),cv2.IMREAD_UNCHANGED)
        if image is None:raise FileNotFoundError(name)
        if image.ndim==3:ax.imshow(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),interpolation='nearest')
        else:ax.imshow(image,cmap='gray',vmin=0,vmax=255,interpolation='nearest')
        ax.set_title(label,color='#0091a0');ax.axis('off')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    target=args.output_dir/('opencv_pipeline_'+('revised' if args.publish_checked else 'candidate')+'.pdf')
    fig.savefig(target);plt.close(fig);print(target)


if __name__=='__main__':main()
