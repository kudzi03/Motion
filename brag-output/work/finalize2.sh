#!/usr/bin/env bash
# v2 delivery: mux the supersampled master with the normalised score; poster from frame 0.
# Frame 0 of v2 is already the composed hook, so it is the poster and the thumbnail as-is.
set -euo pipefail
cd "$(dirname "$0")"

# poster: frame 0 rendered at 2x and downscaled, same pipeline as the video
DPR=2 node stills.cjs poster2x 0
ffmpeg -hide_banner -loglevel error -y -i poster2x/t00.00.png -vf "scale=1080:1920:flags=lanczos" -q:v 2 ../showreel-v2.jpg

# delivery master: the single-encode supersampled render (CRF 8) with the score muxed in; no second video encode
ffmpeg -hide_banner -loglevel error -y -i video2hq.mp4 -i score2_norm.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -ar 48000 -t 25 -movflags +faststart ../showreel-v2.mp4

ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate -of compact ../showreel-v2.mp4
