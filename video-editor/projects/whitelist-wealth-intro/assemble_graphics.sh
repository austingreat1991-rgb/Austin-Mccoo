#!/usr/bin/env bash
# Composite branded overlays onto the cut with fades + enable-timing, export 720p (<30MB).
set -euo pipefail
cd "$(dirname "$0")/../.."   # -> video-editor/
J=projects/whitelist-wealth-intro
SRC=$J/outputs/whitelist-wealth.mp4          # 1080p silence-cut master
A=$J/assets
OUT=$J/outputs/whitelist-wealth-graphics.mp4

# -loop 1 PNG inputs never EOF -> MUST bound the OUTPUT with -t (an OUTPUT option,
# just before the file) or ffmpeg encodes forever past the source.
DUR=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$SRC")

ffmpeg -y -hide_banner -loglevel error \
  -i "$SRC" -loop 1 -i "$A/title_card.png" -loop 1 -i "$A/stat_callout.png" -loop 1 -i "$A/logo_bug.png" \
  -filter_complex "\
[1:v]format=rgba,fade=t=in:st=0.5:d=0.4:alpha=1,fade=t=out:st=4.6:d=0.4:alpha=1[tc];\
[2:v]format=rgba,fade=t=in:st=6.0:d=0.4:alpha=1,fade=t=out:st=11.6:d=0.4:alpha=1[sc];\
[3:v]format=rgba,fade=t=in:st=0.3:d=0.5:alpha=1[lg];\
[0:v][lg]overlay=0:0[b0];\
[b0][tc]overlay=0:0:enable='between(t,0.5,5.0)'[b1];\
[b1][sc]overlay=0:0:enable='between(t,6.0,12.0)'[b2];\
[b2]scale=1280:720:flags=bilinear[v]" \
  -map "[v]" -map 0:a \
  -c:v libx264 -preset ultrafast -crf 27 -maxrate 430k -bufsize 900k -pix_fmt yuv420p \
  -c:a aac -b:a 96k -movflags +faststart -t "$DUR" "$OUT"
echo "WROTE $OUT"
