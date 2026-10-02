#!/usr/bin/env bash
# v3 delivery: mux the supersampled master with the normalised score; poster from the brand frame.
# Frame 0 of v3 is the empty sky the wordmark sharpens into, so the poster is t=1.5 (mark, name and line all in).
set -euo pipefail
cd "$(dirname "$0")"

# poster: rendered at 2x and downscaled, same pipeline as the video
COMP=../composition-v3 DPR=2 node stills.cjs poster3x 1.5
ffmpeg -hide_banner -loglevel error -y -i poster3x/t01.50.png -vf "scale=1080:1920:flags=lanczos" -q:v 2 ../after-hours-v3.jpg

# delivery master: the single-encode supersampled render (CRF 8) with the score muxed in; no second video encode
ffmpeg -hide_banner -loglevel error -y -i video3hq.mp4 -i score3_norm.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -t 24 -movflags +faststart ../after-hours-v3.mp4

ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate -of compact ../after-hours-v3.mp4
