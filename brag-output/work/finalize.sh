#!/usr/bin/env bash
# Poster + final mux. Run from brag-output/work after render.cjs and audio.py.
#   POSTER_T: the strongest settled frame (hero headline fully in, sphere lit)
set -euo pipefail
cd "$(dirname "$0")"
POSTER_T="${POSTER_T:-2.30}"

# 1. poster straight from the composition (lossless PNG), then the shareable JPEG
node stills.cjs poster "$POSTER_T"
cp "poster/t$(printf '%05.2f' "$POSTER_T").png" poster.png
ffmpeg -hide_banner -loglevel error -y -i poster.png -q:v 2 ../brag.jpg

# 2. final: poster replaces frame 0 (same frame count, audio untouched), score muxed in
ffmpeg -hide_banner -loglevel error -y -i video.mp4 -loop 1 -framerate 30 -i poster.png -i score_norm.wav \
  -filter_complex "[1:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[p];[0:v][p]overlay=shortest=1:enable='eq(n,0)'[v]" \
  -map "[v]" -map 2:a \
  -c:v libx264 -preset slow -crf 16 -tune animation -profile:v high -level 4.2 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -t 22.5 -movflags +faststart ../brag.mp4

ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels -of compact ../brag.mp4
