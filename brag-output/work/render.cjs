// Frame-accurate render: seek the composition to every frame time, capture, and encode.
// node render.cjs [out.mp4] [--scale 0.5] [--from s] [--to s] [--workers 4]
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { openComposition } = require('./lib.cjs');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const out = path.resolve(args[0] && !args[0].startsWith('--') ? args[0] : path.join(__dirname, 'video.mp4'));
const scale = parseFloat(opt('--scale', '1'));
const workers = parseInt(opt('--workers', '4'), 10);

(async () => {
  const { pages, meta, close } = await openComposition({ pages: workers });
  fs.writeFileSync(path.join(__dirname, 'cues.json'), JSON.stringify({ duration: meta.duration, fps: meta.fps, scenes: meta.scenes, cues: meta.cues }, null, 1));
  const fps = meta.fps;
  const from = parseFloat(opt('--from', '0')), to = parseFloat(opt('--to', String(meta.duration)));
  const f0 = Math.round(from * fps), f1 = Math.round(to * fps);
  const vf = [scale !== 1 ? `scale=iw*${scale}:ih*${scale}:flags=lanczos` : null, 'scale=out_color_matrix=bt709:out_range=tv', 'format=yuv420p'].filter(Boolean).join(',');
  const ff = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    '-vf', vf, '-c:v', 'libx264', '-preset', opt('--preset', 'slow'), '-crf', opt('--crf', '12'), '-aq-mode', '3',
    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
    '-r', String(fps), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });

  // workers take frames round-robin; the writer flushes them to ffmpeg strictly in order
  const done = new Map();
  let next = f0;
  let wake = null;
  const t0 = Date.now();
  const writer = (async () => {
    while (next < f1) {
      if (!done.has(next)) { await new Promise(r => (wake = r)); continue; }
      const buf = done.get(next); done.delete(next);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((next - f0) % 90 === 0) process.stdout.write(`frame ${next}/${f1} (${((Date.now() - t0) / 1000).toFixed(0)}s)\n`);
      next++;
    }
  })();
  await Promise.all(pages.map(async (page, w) => {
    for (let f = f0 + w; f < f1; f += pages.length) {
      while (f > next + pages.length * 6) await new Promise(r => setTimeout(r, 15));
      await page.evaluate(t => window.__seek(t), f / fps);
      done.set(f, await page.screenshot({ type: 'png' }));
      if (wake) { const r = wake; wake = null; r(); }
    }
  }));
  if (wake) wake();
  await writer;
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await close();
  console.log(`done: ${out} in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
})().catch(e => { console.error(e); process.exit(1); });
