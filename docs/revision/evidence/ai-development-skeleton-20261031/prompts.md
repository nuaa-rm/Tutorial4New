# 骨架占位脱敏：内置 imagegen 提示词

2026-10-31，使用内置 `image_gen.imagegen` 编辑两张已经脱敏的截图，不使用 CLI/API。以下为两次调用的完整提示词，`transparent_background=false`，各调用只附对应的本地图片。生成候选仅在原隐私区通过 ImageMagick 蒙版合入，其他区域保留真实截图像素。

## 主界面

输入：`01-基础通识/images/ai/desktop-overview_revised.png`（Git 基线 `bc7b581`）。

```text
Use case: precise-object-edit. Edit target: attached 2560x1495 dark Codex desktop screenshot for a Chinese beginner programming textbook. This is a privacy-redaction aesthetic correction. Keep canvas dimensions/aspect ratio, original application layout, every unmasked real control/icon/label/model selector, the composer and file changes chip, and cyan numbered circles 1,2,3,4 exactly in their original locations. Change ONLY the crude gray opaque privacy rectangles and their Chinese redaction captions. Remove those captions. Replace masked surfaces with background that seamlessly matches the app's near-black #141414 theme, and render tasteful static SKELETON LOADING PLACEHOLDERS over the hidden content: low contrast charcoal rounded bars in varied lengths, radii 6-10px, clean spacing, subtle gray-to-charcoal horizontal sheen, no glow. The title is a short single rounded skeleton bar. The sidebar has individual short skeleton bars aligned with the existing folder icons and nested chat positions, with comfortable vertical gaps; keep its actual icons and section labels. The large conversation redaction should be replaced with 2-3 beautifully spaced skeleton message groups in a centered normal-width conversation column (roughly x1020-1950), including a right-aligned user bubble with 2 placeholder lines, a left-aligned assistant reply with 3 placeholder lines and a compact code-shaped skeleton panel, then another short reply below. Replace the masked account corner with a small neutral circular avatar skeleton. Do not add any literal example text, gibberish, text saying hidden/loading, invented buttons, fake commands, fake status results, logos, borders around the former mask, or a giant empty gray panel. Invariants: all non-private real screenshot pixels should be preserved as faithfully as possible, especially the bottom composer controls and readable original Chinese UI labels. Cyan instructional numbers remain unchanged. Result should look like a polished privacy-sanitized screenshot, not a redesigned app. Opaque flattened RGB, no private information can be reconstructed.
```

## 差异面板

输入：`01-基础通识/images/ai/review-pane_revised.png`（同一基线）。

```text
Use case: precise-object-edit. Input image: edit target, a real dark-mode Git diff screenshot used in a Chinese programming textbook. Make a very narrow privacy-redaction aesthetic correction. Change ONLY the opaque gray file-path strip and the text 文件路径已隐藏, in the header at approximately x48..865, y131..166 of the original 1070x860 image. Remove that rectangle and its caption, match its background seamlessly to the surrounding near-black #141414 header, and put in its place ONE subtle rounded skeleton placeholder bar of about 280x13 pixels at x64,y143, with a very low-contrast charcoal gradient, radius 6px. It is an intentional static privacy placeholder. Keep the real file icon immediately to its left. Preserve EVERYTHING ELSE exactly, including the original canvas aspect ratio, tab 变更, range 未暂存, all Git counts, every toolbar icon, the +54 -0 count, the green diff background, every original code character and line number. Do not generate replacement filenames, arbitrary text, extra bars or UI. Do not redesign or recolor the app. The skeleton is quiet and integrated, not black censorship tape. Only the path is private; all original code and controls are instructional evidence and must remain untouched.
```

## 最终合成

生成的主图为 1641×958，差异图为 1399×1124；脚本先对齐基图尺寸，再仅合入已知隐私区。四个青色标号由蒙版保护，输入区、代码与工具栏始终来自原图。用户指出的左上 Dot 行与左下头像残留在蒙版内以同主题背景、圆角短条及圆形占位整理，最后重新核对全部保护区域。生成候选不作为整张软件截图使用。
