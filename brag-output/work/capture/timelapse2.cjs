// A real time-lapse from DreamBuilder's own lighting model: the garden view goes from day to
// blue hour (sun sinking, rooms and facade lamps coming on, the far town lighting up).
// The page runs on a virtual clock so each captured frame is exactly STEP ms of scene time
// apart, however slowly the software renderer draws. UI hidden, analytics blocked, no forms.
//   node timelapse.cjs [frames=26] [stepMs=200]
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const N = parseInt(process.argv[2] || '26', 10), STEP = parseFloat(process.argv[3] || '200');
const OUT = 'plates/seq2';
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 432, height: 768 }, deviceScaleFactor: 2.5 });
  await ctx.route(/\/api\/(track|lead)|_vercel\/insights|vitals\.vercel/, r => r.abort());
  await ctx.addInitScript(() => {
    const realNow = performance.now.bind(performance), realRaf = window.requestAnimationFrame.bind(window);
    const V = (window.__vclock = { manual: false, t: 0 });
    performance.now = () => (V.manual ? V.t : realNow());
    window.requestAnimationFrame = cb => realRaf(ts => cb(V.manual ? V.t : ts));
    V.freeze = () => { V.t = realNow(); V.manual = true; };
  });
  const page = await ctx.newPage();
  page.setDefaultTimeout(900000);
  const t0 = Date.now(), log = (...a) => console.log(((Date.now() - t0) / 1000).toFixed(0) + 's', ...a);
  await page.goto('https://velabuilt-dreambuilder.vercel.app/?quality=mobile&motion=reduced&debug', { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForFunction(() => window.__store?.getState().sceneReady, null, { timeout: 400000, polling: 500 });
  await page.addStyleTag({ content: '.topbar,.panel,.intro,.hint,.compare,.switcher,.flow,.reveal,.loader,.callout,.tag3d,.pin,.skip{display:none!important}' });
  const frames = async n => { const s = await page.evaluate(() => window.__frames || 0); await page.waitForFunction(t => (window.__frames || 0) >= t, s + n, { timeout: 900000, polling: 100 }); };

  // daylight garden, settled
  // the camera only re-fits to a changed inset once the garden is the active scene, so select it
  // first, then move the inset (260 -> 390: the same path as the framing test)
  for (const top of [260, 390]) {
    await page.evaluate(top => { window.__settle = true; window.__bare = false; const s = window.__store.getState(); s.selectIndustry('landscaping'); s.setInsets({ top, right: 0, bottom: 0, left: 0 }); s.set({ landscaping: { ...s.landscaping, evening: false } }); }, top);
    await page.waitForTimeout(1500); await frames(8);
  }
  await page.screenshot({ path: `${OUT}/_check.png`, scale: 'css' });
  log('day settled');

  // freeze time, switch the garden lighting on, then step the clock
  await page.evaluate(() => { window.__settle = false; window.__vclock.freeze(); });
  await frames(2);
  await page.evaluate(() => { const s = window.__store.getState(); s.set({ landscaping: { ...s.landscaping, evening: true } }); });
  for (let k = 0; k < N; k++) {
    if (k > 0) { await page.evaluate(step => { window.__vclock.t += step; }, STEP); await frames(2); }
    else await frames(2);
    await page.screenshot({ path: `${OUT}/d${String(k).padStart(2, '0')}.png`, timeout: 900000 });
    log('frame', k, 'scene t =', (k * STEP / 1000).toFixed(2) + 's');
  }
  // the settled night, for the long middle of the piece
  await page.evaluate(() => { window.__vclock.manual = false; window.__settle = true; });
  await page.waitForTimeout(1500); await frames(6);
  await page.screenshot({ path: `${OUT}/night.png`, timeout: 900000 });
  log('night settled');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
