# VelaBuilt showreel

## v2 (current)

- `showreel-v2.mp4`: 1080×1920, 30fps, 25.0s. H.264 High (CRF 14, up to 24 Mbps) + AAC 320k, -14 LUFS. Every frame is rendered at 2160×3840 and downscaled with Lanczos, so thin lines and small UI text hold up under platform compression. Frame 0 is the poster.
- `showreel-v2.jpg`: the poster (frame 0).
- `share-copy-v2.txt`: caption.
- `v2-plan.md`: the second-by-second plan and the assets it uses.

Every screen in it is real, captured live at high density:
- **Kingson Engineering** and **Cardio Life**: client websites.
- **DreamBuilder**: 3D showrooms, qualification, CRM record, WhatsApp follow-up, booking. Labelled as a VelaBuilt demo with sample data, as the demo labels itself.

The agent conversation was built for the video and is tagged *System demo*. No metrics, testimonials or client results are invented.

### Rebuild v2

Needs Node 22+, ffmpeg, Python 3 with numpy and scipy, and Playwright's Chromium.

```bash
cd work
node render.cjs video2.mp4 --scale 0.5 --crf 12       # DPR=2 env for the supersampled master
node cues.cjs cues2.json && python3 audio2.py           # score + sound design → score2.wav
ffmpeg -y -i score2.wav -af volume=-0.4dB -c:a pcm_s24le score2_norm.wav   # → -14 LUFS
bash finalize2.sh                                       # → ../showreel-v2.mp4, ../showreel-v2.jpg
```

- **Preview:** serve `composition-v2/` and open `index.html`. It loops; use `?t=9.5` to pin a frame.
- **Recapture:** the capture scripts for the live sites are in `work/capture/`. They block analytics and never submit a real form.

## v1

`brag.mp4` / `brag.jpg` / `share-copy.txt` / `brag-plan.md` / `composition/`: the first cut, a velabuilt.com-only piece. Rebuild with `COMP=../composition node render.cjs` plus `audio.py` and `finalize.sh`.
