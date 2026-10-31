#!/usr/bin/env bash
# 仅将生图候选的骨架占位合入已脱敏截图，保留真实控件与代码像素。
set -euo pipefail

if [[ $# -ne 5 ]]; then
  printf '%s\n' '用法：bash scripts/prepare_ai_screenshots.sh 已脱敏主图 已脱敏差异图 主图生图候选 差异生图候选 新输出目录' >&2
  exit 2
fi
task_main=$1
task_review=$2
task_main_candidate=$3
task_review_candidate=$4
task_output=$5
for task_input in "$task_main" "$task_review" "$task_main_candidate" "$task_review_candidate"; do
  [[ -f "$task_input" ]] || { printf '文件不存在：%s\n' "$task_input" >&2; exit 2; }
done

# 坐标对应已裁剪、已脱敏的入书截图，不可直接用于含隐私的原始截图。
[[ $(magick identify -format '%wx%h' "$task_main") == 2560x1495 ]] || {
  printf '%s\n' '已脱敏主图必须为 2560x1495；其他布局须重新核对坐标。' >&2; exit 2;
}
[[ $(magick identify -format '%wx%h' "$task_review") == 1070x860 ]] || {
  printf '%s\n' '已脱敏差异图必须为 1070x860；其他布局须重新核对坐标。' >&2; exit 2;
}
[[ ! -e "$task_output" ]] || { printf '%s\n' '输出目录必须尚不存在。' >&2; exit 2; }
mkdir -p "$task_output"
task_temp=$(mktemp -d)
trap 'rm -rf -- "$task_temp"' EXIT

# 白色为可替换的原隐私区；黑色保留原图。四个教材标号也从原图保留。
magick -size 2560x1495 xc:black -fill white \
  -draw 'rectangle 106,105 410,150 rectangle 106,199 410,1229 rectangle 76,1269 410,1494 rectangle 10,1435 61,1494 rectangle 480,10 1400,57 rectangle 460,70 2540,1285' \
  -fill black \
  -draw 'circle 375,178 422,178 circle 520,155 567,155 circle 980,1385 1027,1385 circle 1300,1316 1347,1316' \
  "$task_temp/main-mask.miff"
magick "$task_main_candidate" -resize '2560x1495!' \
  -fill '#141414' -draw 'rectangle 106,105 410,150' \
  -fill '#303236' -draw 'roundrectangle 120,119 240,139 8,8' \
  -fill '#111111' -draw 'rectangle 10,1435 61,1494' \
  -fill '#303236' -draw 'circle 35,1465 55,1465' \
  "$task_temp/main-mask.miff" -alpha off -compose CopyOpacity -composite \
  "$task_temp/main-patch.miff"
magick "$task_main" "$task_temp/main-patch.miff" -compose Over -composite \
  -alpha off -strip "$task_output/desktop-overview.png"

# 只替换文件路径条，未暂存范围、真实计数、工具栏、行号与全部代码保持原样。
magick -size 1070x860 xc:black -fill white \
  -draw 'rectangle 48,131 864,166' "$task_temp/review-mask.miff"
magick "$task_review_candidate" -resize '1070x860!' \
  "$task_temp/review-mask.miff" -alpha off -compose CopyOpacity -composite \
  "$task_temp/review-patch.miff"
magick "$task_review" "$task_temp/review-patch.miff" -compose Over -composite \
  -alpha off -strip "$task_output/review-pane.png"

printf '%s\n' '已合入骨架占位候选。须复核隐私、美观、原控件像素及 PDF 实际排版后再使用。'
