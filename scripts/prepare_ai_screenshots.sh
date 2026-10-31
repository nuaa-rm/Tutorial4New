#!/usr/bin/env bash
# 从真实窗口截图生成脱敏教学图；原图不复制到仓库。
set -euo pipefail

if [[ $# -ne 3 ]]; then
  printf '%s\n' '用法：bash scripts/prepare_ai_screenshots.sh 主界面原图 差异面板原图 新输出目录' >&2
  exit 2
fi
task_main=$1
task_review=$2
task_output=$3
for task_input in "$task_main" "$task_review"; do
  [[ -f "$task_input" ]] || { printf '文件不存在：%s\n' "$task_input" >&2; exit 2; }
  # 遮挡坐标只适用本次截图。尺寸不匹配时停止，避免错误脱敏。
  [[ $(magick identify -format '%wx%h' "$task_input") == 2560x1550 ]] || {
    printf '%s\n' '原图必须为本次核对的 2560x1550；其他界面须重新审查遮挡坐标。' >&2
    exit 2
  }
done
[[ ! -e "$task_output" ]] || { printf '%s\n' '输出目录必须尚不存在。' >&2; exit 2; }
mkdir -p "$task_output"
task_font=$(fc-match 'Noto Sans CJK SC' -f '%{file}')

# 实心覆盖项目/聊天名称、账号头像、标题和对话正文；数字是教材标注。
magick "$task_main" \
  -fill '#292b30' \
  -draw 'rectangle 106,160 410,205 rectangle 106,254 410,1284 rectangle 76,1324 410,1549 rectangle 10,1490 61,1549 rectangle 480,65 1400,112 rectangle 460,125 2540,1340' \
  -font "$task_font" -pointsize 35 -fill '#bfc6ce' \
  -annotate +130+320 '项目名称已隐藏' \
  -annotate +940+715 '对话正文已隐藏' \
  -annotate +505+98 '聊天标题已隐藏' \
  -fill '#10bcc4' \
  -draw 'circle 375,233 420,233 circle 520,210 565,210 circle 980,1440 1025,1440 circle 1300,1371 1345,1371' \
  -fill '#ffffff' -pointsize 58 \
  -annotate +357+254 '1' -annotate +502+231 '2' \
  -annotate +962+1461 '3' -annotate +1282+1392 '4' \
  -crop 2560x1495+0+55 +repage -alpha off -strip \
  "$task_output/desktop-overview.png"

# 仅取输入框与改动入口，不包含对话、侧栏、路径或账号。
magick "$task_main" -crop 945x200+1020+1338 +repage \
  -alpha off -strip "$task_output/composer-controls.png"

# 仅取差异面板，遮挡相对文件路径；代码内容为本章教材源码。
magick "$task_review" -fill '#292b30' \
  -draw 'rectangle 1534,186 2350,221' \
  -font "$task_font" -pointsize 23 -fill '#bfc6ce' \
  -annotate +1550+213 '文件路径已隐藏' \
  -crop 1070x860+1486+55 +repage -alpha off -strip \
  "$task_output/review-pane.png"

printf '%s\n' '已生成候选脱敏图。须逐张人工复查隐私、控件和排版后再使用。'
