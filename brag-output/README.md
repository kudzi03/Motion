# VelaBuilt launch video

- `brag.mp4`: 1080×1920, 30fps, 22.5s, H.264 + AAC, loudness -14 LUFS. The poster is baked in as frame 0.
- `brag.jpg`: the poster (hero headline + sphere).
- `share-copy.txt`: caption.
- `brag-plan.md`: angle, rubric, storyboard.

## Rebuild

Needs Node 22+, ffmpeg, Python 3 with numpy and scipy, and Playwright's Chromium.

```bash
cd work
node render.cjs video.mp4          # frames → video track; also writes cues.json
python3 audio.py                   # original score + SFX locked to cues.json → score.wav
ffmpeg -y -i score.wav -af volume=-3.63dB -c:a pcm_s24le score_norm.wav   # → -14 LUFS
bash finalize.sh                   # poster frame, mux → ../brag.mp4, ../brag.jpg
```

Preview in a browser: serve `composition/` and open `index.html` (it loops), or `index.html?t=9.5` to pin a frame. `node stills.cjs out 2.3 9.9` writes PNG stills.

Every frame is a pure function of time (`window.__seek(t)`). Scene timings are in the `S` object at the top of the composition script. The audio reads the same cue list, so it stays in sync when scenes move.
