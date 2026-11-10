#!/usr/bin/env python3
"""生成 USB / IP KVM 接线对照，检查候选图后发布 revised。"""
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
    # TTC 默认第 0 项是日文字形；第 2 项才是简体中文 SC。
    font = ImageFont.truetype(regular, 30, index=2)
    small = ImageFont.truetype(regular, 27, index=2)
    heading = ImageFont.truetype(bold, 36, index=2)
    title = ImageFont.truetype(bold, 43, index=2)
    if any(face.getname()[0] != 'Noto Sans CJK SC'
           for face in (font, small, heading, title)):
        raise ValueError('字体合集的第 2 项不是简体中文 SC，请核对字体文件')
    canvas = Image.new('RGB', (1660, 1100), 'white')
    draw = ImageDraw.Draw(canvas)
    ink, cyan, outline = '#203741', '#057D95', '#95CBD6'

    def center(text, x, y, face=font, fill=ink):
        bbox = draw.textbbox((0, 0), text, font=face)
        draw.text((x-(bbox[2]-bbox[0])/2, y-(bbox[3]-bbox[1])/2-bbox[1]),
                  text, font=face, fill=fill)

    def box(x, y, width, height, lines):
        draw.rounded_rectangle((x, y, x+width, y+height), radius=16,
                               fill='white', outline=outline, width=3)
        first = y+height/2-(len(lines)-1)*22
        for i, label in enumerate(lines):
            center(label, x+width/2, first+i*44)

    def arrow(x1, y1, x2, y2, both=False, fill=cyan):
        draw.line((x1, y1, x2, y2), fill=fill, width=5)
        if y1 == y2:
            sign = 1 if x2 > x1 else -1
            draw.polygon(((x2, y2), (x2-sign*12, y2-8), (x2-sign*12, y2+8)), fill=fill)
            if both:
                draw.polygon(((x1, y1), (x1+sign*12, y1-8), (x1+sign*12, y1+8)), fill=fill)
        else:
            draw.polygon(((x2, y2), (x2-8, y2+12), (x2+8, y2+12)), fill=fill)

    draw.text((38, 24), 'KVM 接线：笔记本侧一根线，机器人侧仍需完整接线', font=title, fill=ink)
    for top, label, usb_label in [
        (112, '1  USB KVM：以 Sipeed NanoKVM-USB 为例', 'Target USB · 键鼠'),
        (574, '2  IP KVM：以独立供电的 PiKVM 型号为例', 'USB HID 键鼠'),
    ]:
        draw.rounded_rectangle((28, top, 1632, top+425), radius=20, fill='#F2F9FB')
        draw.text((52, top+16), label, font=heading, fill=cyan)
        box(60, top+105, 300, 155, ['笔记本', '屏幕与键鼠'])
        box(1280, top+105, 315, 155, ['机载电脑', 'HDMI 输出', 'USB 主机口'])
        center('HDMI 视频', 1100, top+100, font, cyan)
        arrow(1272, top+137, 930, top+137)
        center(usb_label, 1100, top+184, font, cyan)
        arrow(930, top+220, 1272, top+220)
        box(1280, top+315, 315, 62, ['机器人正常电源'])
        arrow(1437, top+309, 1437, top+266)

    box(650, 217, 270, 155, ['NanoKVM-USB'])
    center('Host USB · 数据线', 505, 251, small, cyan)
    arrow(368, 294, 642, 294, both=True)
    center('画面回传 / 输入控制', 505, 337, small)
    center('笔记本打开控制台', 210, 399, small)
    center('视频与键鼠经本地 USB 传输', 785, 459, font)

    box(650, 679, 270, 155, ['IP KVM', '自己的网口'])
    center('一根网线', 505, 713, small, cyan)
    arrow(368, 756, 642, 756, both=True)
    center('HTTPS 网页控制台', 505, 799, small)
    center('先配通笔记本与 KVM 地址', 250, 861, small)
    box(650, 889, 270, 62, ['KVM 独立电源'])
    arrow(785, 883, 785, 840)

    center('USB HID：模拟键盘和鼠标；IP KVM 的网线连接 KVM 自己的网口。', 830, 1033, font)
    center('图示为本章示例接线；实际接口、供电与适配器以具体型号手册为准。', 830, 1072, small)
    target = args.output_dir / ('kvm_wiring_revised.png' if args.publish_checked
                                else 'kvm_wiring_candidate.png')
    canvas.save(target)
    print(target)


if __name__ == '__main__':
    main()
