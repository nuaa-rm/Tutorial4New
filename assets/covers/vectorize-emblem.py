"""将新版几何队徽提取为独立 SVG 路径，并导出同源矢量 PDF。"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parent
source = ROOT.parent / "textures" / "team_icon.png"
im = Image.open(source).convert("RGBA")
mask = np.asarray(im.getchannel("A")) >= 128
h, w = mask.shape
edges = {}

def add_edges(test, start_offset, end_offset):
    for y, x in zip(*np.nonzero(test)):
        start = (int(x + start_offset[0]), int(y + start_offset[1]))
        end = (int(x + end_offset[0]), int(y + end_offset[1]))
        edges.setdefault(start, []).append(end)

padded = np.pad(mask, 1)
add_edges(mask & ~padded[:-2, 1:-1], (0, 0), (1, 0))
add_edges(mask & ~padded[1:-1, 2:], (1, 0), (1, 1))
add_edges(mask & ~padded[2:, 1:-1], (1, 1), (0, 1))
add_edges(mask & ~padded[1:-1, :-2], (0, 1), (0, 0))

def rdp(points, tolerance=1.35):
    if len(points) < 3:
        return points
    a, b = np.asarray(points[0], float), np.asarray(points[-1], float)
    p = np.asarray(points[1:-1], float)
    line = b - a
    den = float(line @ line)
    if den:
        t = np.clip((p - a) @ line / den, 0, 1)
        distances = np.linalg.norm(p - a - t[:, None] * line, axis=1)
    else:
        distances = np.linalg.norm(p - a, axis=1)
    index = int(np.argmax(distances)) + 1
    if distances[index - 1] <= tolerance:
        return [points[0], points[-1]]
    return rdp(points[:index + 1], tolerance)[:-1] + rdp(points[index:], tolerance)

polygons = []
while edges:
    start = next(iter(edges))
    current, points = start, [start]
    while True:
        choices = edges[current]
        nxt = choices.pop()
        if not choices:
            del edges[current]
        current = nxt
        if current == start:
            break
        points.append(current)
    area = abs(sum(x * points[(i + 1) % len(points)][1]
                   - y * points[(i + 1) % len(points)][0]
                   for i, (x, y) in enumerate(points))) / 2
    if area < 40:
        continue
    split = int(np.argmax(np.sum((np.asarray(points) - points[0]) ** 2, axis=1)))
    simple = rdp(points[:split + 1])[:-1] + rdp(points[split:] + [points[0]])[:-1]
    polygons.append({"points": simple, "area": area})

polygons.sort(key=lambda p: (min(y for x, y in p["points"]), min(x for x, y in p["points"])))
for i, p in enumerate(polygons, 1):
    pts = np.asarray(p["points"])
    x, y = pts.mean(axis=0)
    if pts[:, 1].max() > 950 and pts[:, 1].min() > 700:
        region = "tail"
        color = "#CB5C49" if x < 470 else "#E97953" if x < 800 else "#F1AF64"
    elif x > 780 and y < 240:
        region, color = "crest", "#D75B4C"
    elif x > 800:
        region = "head"
        color = "#1FBABE" if y < 370 else "#127D91"
    else:
        region = "wing"
        color = "#55CAD0" if y < 170 else "#1FBABE" if y < 340 else "#127D91" if y < 540 else "#225769"
    p.update(id=f"{region}-{i:02d}", color=color)
    print(p["id"],len(p["points"]),color,pts.min(axis=0).tolist(),pts.max(axis=0).tolist())

# 用栅格对照检查轮廓拟合；SVG 中不嵌入图片。
check = Image.new("L", (w*4, h*4))
draw = ImageDraw.Draw(check)
for p in polygons:
    draw.polygon([(x*4,y*4) for x,y in p["points"]], fill=255)
reconstructed = np.asarray(check.resize((w,h), Image.Resampling.LANCZOS)) >= 128
iou = (mask & reconstructed).sum() / (mask | reconstructed).sum()
assert iou > 0.985, f"轮廓拟合不足：{iou:.4%}"
print(f"轮廓重叠率 IoU: {iou:.4%}; 分块: {len(polygons)}")

def svg(monochrome=False):
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
             '<title id="title">长空御风战队队徽</title>',
             '<desc id="desc">由用户提供的新版几何队徽提取的矢量轮廓；青绿翼部搭配珊瑚橙眉羽与暖金尾翼。</desc>']
    for p in polygons:
        d = "M " + " L ".join(f"{x},{y}" for x,y in p["points"]) + " Z"
        color = "#16343E" if monochrome else p["color"]
        lines.append(f'  <path id="{p["id"]}" fill="{color}" d="{d}"/>')
    return "\n".join(lines + ["</svg>\n"])

(ROOT / "team-emblem-cyan.svg").write_text(svg(), encoding="utf-8")
(ROOT / "team-emblem-mono.svg").write_text(svg(True), encoding="utf-8")
pdf = canvas.Canvas(str(ROOT / "team-emblem-cyan.pdf"), pagesize=(w, h))
pdf.setTitle("长空御风 · 教材配色矢量队徽")
for p in polygons:
    path = pdf.beginPath()
    x, y = p["points"][0]
    path.moveTo(x, h-y)
    for x,y in p["points"][1:]:
        path.lineTo(x, h-y)
    path.close()
    pdf.setFillColor(HexColor(p["color"]))
    pdf.drawPath(path, fill=1, stroke=0)
pdf.showPage()
pdf.save()

preview = Image.new("RGBA", (w*2, h*2), (0,0,0,0))
draw = ImageDraw.Draw(preview)
for p in polygons:
    draw.polygon([(x*2,y*2) for x,y in p["points"]], fill=p["color"])
preview.resize((w,h), Image.Resampling.LANCZOS).save(ROOT / "team-emblem-cyan.png")
(ROOT / "team-emblem-trace.json").write_text(json.dumps({"source":"../textures/team_icon.png", "iou":float(iou), "parts":polygons},ensure_ascii=False,indent=2),encoding="utf-8")
