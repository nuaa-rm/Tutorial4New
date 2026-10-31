#!/usr/bin/env python3
"""生成第5章网络路径示意图；实际查看候选图后才发布 revised。"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--publish-checked', action='store_true')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    regular = '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc'
    bold = '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc'
    font = ImageFont.truetype(regular, 31)
    small = ImageFont.truetype(regular, 28)
    heading = ImageFont.truetype(bold, 36)
    title = ImageFont.truetype(bold, 44)
    canvas = Image.new('RGB', (1540, 1060), 'white')
    draw = ImageDraw.Draw(canvas)
    ink, cyan, line = '#203741', '#057D95', '#95CBD6'

    def center(text, x, y, face=font, fill=ink):
        box = draw.textbbox((0, 0), text, font=face)
        draw.text((x - (box[2]-box[0])/2, y - (box[3]-box[1])/2-box[1]),
                  text, font=face, fill=fill)

    def box(x, y, width, height, lines):
        draw.rounded_rectangle((x, y, x+width, y+height), radius=16,
                               fill='white', outline=line, width=3)
        baseline = y + height/2 - (len(lines)-1)*22
        for i, label in enumerate(lines):
            center(label, x+width/2, baseline+i*44)

    def link(x1, y, x2, label):
        draw.line((x1, y, x2, y), fill=cyan, width=5)
        draw.polygon(((x2, y), (x2-12, y-8), (x2-12, y+8)), fill=cyan)
        draw.polygon(((x1, y), (x1+12, y-8), (x1+12, y+8)), fill=cyan)
        center(label, (x1+x2)/2, y-27, small, cyan)

    draw.text((38, 24), '先选网络入口，再连接 SSH 或远程桌面', font=title, fill=ink)
    rows = [
        (112, '1  局域网：路由器分配地址', '同一网络内可互访，名字解析可用时也能按名连接'),
        (410, '2  网线直连：两端约定固定地址', '无须互联网或网关；不抢占笔记本原来的默认出口'),
        (708, '3  Tailscale：跨互联网建立加密网络', '两端先联网并获准加入同一 Tailnet；可能直连，也可能中继'),
    ]
    for top, name, note in rows:
        draw.rounded_rectangle((28, top, 1512, top+270), radius=20, fill='#F2F9FB')
        draw.text((52, top+16), name, font=heading, fill=cyan)
        draw.text((52, top+224), note, font=small, fill=ink)

    box(60, 192, 330, 120, ['笔记本', '192.168.50.10/24'])
    box(610, 192, 320, 120, ['路由器', '分配地址并允许互访'])
    box(1150, 192, 330, 120, ['机器人', '192.168.50.20/24'])
    link(396, 258, 604, '有线或 Wi-Fi')
    link(936, 258, 1144, '有线或 Wi-Fi')

    box(60, 490, 330, 120, ['笔记本', '192.168.77.1/24'])
    box(1150, 490, 330, 120, ['机器人', '192.168.77.2/24'])
    link(396, 556, 1144, '一根网线；双方配置同一子网')

    box(60, 788, 330, 120, ['笔记本 / 网络 A', 'Tailscale 客户端'])
    box(610, 788, 320, 120, ['互联网', 'Tailscale 加密通道'])
    box(1150, 788, 330, 120, ['机器人 / 网络 B', 'Tailscale 客户端'])
    link(396, 854, 604, '可用的出口')
    link(936, 854, 1144, '可用的出口')
    center('数字地址、名字、服务端口、登录认证：逐层验证，不能互相替代。',
           770, 1020, font)
    target = args.output_dir / ('network_paths_revised.png' if args.publish_checked
                                else 'network_paths_candidate.png')
    canvas.save(target)
    print(target)


if __name__ == '__main__':
    main()
