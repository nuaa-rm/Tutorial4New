# install1.png 图片风格整理

- 日期：2026-09-29。
- 原图：`01-基础通识/images/install1.png`（保留，未覆盖）。
- 成图：`01-基础通识/images/install1_revised.png`，1184 × 1328，RGB PNG。
- 生成方式：内置 `image_gen` 图片编辑；一轮生成。
- 参考：相邻的 `shell_revised.pdf` 与卷一封面，分别渲染后作为风格参考传入。
- 调整：青绿色表头、白底与浅青色分行、细线、统一中文字体和按键框；去除原图水印、边缘按钮和空白表格行。重复的“主板 / 笔记本 / 台式机”后缀由分组标题承接；保留所有品牌、按键及“或”的选择关系。
- 本次属于单张图片的视觉整理，保留原表参考数据，未进行具体机型的按键实测。

## 检查结果

| 检查项 | 状态 | 依据 |
| --- | --- | --- |
| 项目风格 | 通过 | 已查看邻近机制图和封面，成图采用教学青色、浅底、细线和简洁字体。 |
| 数据和图内文字 | 通过 | 对照原图逐行核对：主板 23 条、笔记本 21 条、台式机 10 条，共 54 条；无漏项、错位或按键改变。 |
| 图片布局 | 通过 | 成图已实际查看，品牌和按键对齐，多选按键以“或”连接，未见截断或重叠。 |
| 正文尺寸清晰度 | 通过 | 使用项目 ElegantBook 类、A4 页面和相同页边距，以 `0.85\textwidth`（144.5 mm）制作临时单页样张；编译两次并渲染检查，文字可读，无越界或未定义引用。临时样张不作为教材正文发布。 |
| 整理标记 | 通过 | 修改与检查通过后保存为 `install1_revised.png`；原图 SHA-256 保持 `4d67e69c751f32ea1bce9a4d987bf3fd5425345a0ec91d76df77450864cc7bb2`。 |
| 正文引用同步 | 不适用 | 当前仓库没有 `install1.png` 的正文引用；未插入新的图片引用或修改正文。 |

## 最终生成提示

以下为传入内置图片编辑工具的完整提示；参考图依次为原图、相邻机制图、卷一封面。

```text
Use case: style-transfer / scientific-educational
Asset type: one high-resolution PNG table for a Chinese university textbook.
Primary request: Beautify Image 1 into the CURRENT PROJECT style seen in Images 2 and 3. Image 1 is the edit target and the only source for all table data. Image 2 is a neighboring textbook diagram style reference. Image 3 is the textbook cover style reference. Produce exactly one polished, legible replacement image, not a page mockup.

Style: clean restrained academic illustration, white background, teaching teal #0091A0, cyan accent #1FBABE, very pale teal #F0F8F9 or #E8F7F7, dark ink #16343E. Use thin rules, no heavy black grid. Match the simplicity of reference 2 and typography hierarchy of reference 3. Crisp printed Chinese sans-serif typography, never the distorted handwriting font of the source. No gradients, shadows, 3D, brand logos, texture or decorative illustrations.

Composition: portrait canvas roughly 1040:1167, ideally about 2000 pixels wide with generous edge padding. Title at top “启动菜单按键速查”. Below, three clearly separated adjacent panels headed “组装机主板”, “品牌笔记本”, “品牌台式机”. Inside each panel two columns “品牌” and “启动按键”. Left align brands and align key labels consistently. Light alternating rows, subtly rounded panel corners, thin teal outer border and fine pale dividers. Use compact outlined pale-teal keycaps with dark text. Multi-choice keys show two separate keycaps with the Chinese “或” between them, NOT slash and NOT “和”. End each table at its last populated row; remove all blank source cells. The right shorter table may have a restrained note panel below with exactly “按键可能因型号而异，以开机提示或厂商说明为准。” Leave good white space. Make every line easily readable. Keep the title smaller than a poster heading to give rows enough room.

Content, exact row order, never omit, duplicate, move between panels or alter the brand/key pair:
LEFT PANEL — 23 rows, brand label may omit the redundant suffix 主板 because its heading already specifies it:
华硕 | F8
技嘉 | F12
微星 | F11
映泰 | F9
梅捷 | Esc 或 F12
七彩虹 | Esc 或 F11
华擎 | F11
斯巴达克 | Esc
昂达 | F11
双敏 | Esc
翔升 | F10
精英 | Esc 或 F11
冠盟 | F11 或 F12
富士康 | Esc 或 F12
顶星 | F11 或 F12
铭瑄 | Esc
盈通 | F8
捷波 | Esc
Intel | F12
杰微 | Esc 或 F8
致铭 | F12
磐英 | Esc
磐正 | Esc

MIDDLE PANEL — 21 rows, redundant 笔记本 suffix may be omitted:
联想 | F12
宏碁 | F12
华硕 | Esc
惠普 | F9
联想 ThinkPad | F12
戴尔 | F12
神舟 | F12
东芝 | F12
三星 | F12
IBM | F12
富士通 | F12
海尔 | F12
方正 | F12
清华同方 | F12
微星 | F11
明基 | F9
技嘉 | F12
Gateway | F12
eMachines | F12
索尼 | Esc
苹果 | 长按 Option

RIGHT PANEL — 10 rows, redundant 台式机 suffix may be omitted:
联想 | F12
惠普 | F12
宏碁 | F12
戴尔 | Esc
神舟 | F12
华硕 | F8
方正 | F12
清华同方 | F12
海尔 | F12
明基 | F8

Constraints: all 54 brand/key pairs must appear correctly and only once in their own panel. This is a visual edit of the supplied historical table, not an update to hardware advice. Keep technical meaning unchanged. Remove the stray blue edge button and central watermark from the source. No watermarks, no extra footer, no fake UI, no background frame, no English subtitles, no added technical claims. All glyphs must be accurate and sharp. Output the table image alone.
```
