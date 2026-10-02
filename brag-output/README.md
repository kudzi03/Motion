# VelaBuilt showreel

## v3: "After hours" (current)

- `after-hours-v3.mp4`: 1080×1920, 30fps, 24.0s. H.264 High, a single encode at CRF 8, + AAC 320k, -14 LUFS (true peak -1.4 dBTP). Rendered at 2160×3840 and downscaled with Lanczos.
- `after-hours-v3.jpg`: the poster (t=1.5, brand over the garden).
- `share-copy-v3.txt`: caption.
- `v3-plan.md`: the idea, the second-by-second plan, and what is real versus sample.

One continuous shot of DreamBuilder's garden, a real VelaBuilt build, running from sunset to night to sunrise.
- **The light:** it is DreamBuilder's own lighting model, recorded live on a virtual clock. The sunrise is the same sequence played backwards.
- **The enquiry:** a single glass object morphs through the whole enquiry: question, AI agent, qualification, WhatsApp follow-up, booking.
- **The end:** the object closes as three ticked pills that merge into the velabuilt.com pill.
- **Sample data:** the conversation is sample data and is labelled *System demo · sample data* on screen.

### Rebuild v3

```bash
cd work
node capture/timelapse2.cjs 16 150          # (optional) re-record the plates → capture/plates/seq2/
COMP=../composition-v3 node cues.cjs cues3.json && python3 audio3.py    # score → score3.wav
ffmpeg -y -i score3.wav -af "volume=0.3dB,alimiter=limit=0.85:attack=3:release=60:level=disabled" -c:a pcm_s24le score3_norm.wav   # → -14 LUFS
COMP=../composition-v3 DPR=2 node render.cjs video3hq.mp4 --scale 0.5 --crf 8   # supersampled master
bash finalize3.sh                            # → ../after-hours-v3.mp4, ../after-hours-v3.jpg
```

To preview, serve `composition-v3/` and open `index.html`. It loops; use `?t=12.7` to pin a frame.

## v2

- `showreel-v2.mp4`: 1080×1920, 30fps, 25.0s. H.264 High, a single encode at CRF 8 (no generational loss), + AAC 320k, -14 LUFS. Every frame is rendered at 2160×3840 and downscaled with Lanczos, so thin lines and small UI text hold up under platform compression. Frame 0 is the poster.
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
DPR=2 node render.cjs video2hq.mp4 --scale 0.5 --crf 8   # supersampled master
node cues.cjs cues2.json && python3 audio2.py           # score + sound design → score2.wav
ffmpeg -y -i score2.wav -af volume=-0.4dB -c:a pcm_s24le score2_norm.wav   # → -14 LUFS
bash finalize2.sh                                       # → ../showreel-v2.mp4, ../showreel-v2.jpg
```

- **Preview:** serve `composition-v2/` and open `index.html`. It loops; use `?t=9.5` to pin a frame.
- **Recapture:** the capture scripts for the live sites are in `work/capture/`. They block analytics and never submit a real form.

## v1

`brag.mp4` / `brag.jpg` / `share-copy.txt` / `brag-plan.md` / `composition/`: the first cut, a velabuilt.com-only piece. Rebuild with `COMP=../composition node render.cjs` plus `audio.py` and `finalize.sh`.
