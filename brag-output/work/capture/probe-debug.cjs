const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const Q = process.argv[2] || 'mobile';
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 432, height: 768 }, deviceScaleFactor: 1 });
  await ctx.route(/\/api\/(track|lead)|_vercel\/insights|vitals\.vercel/, r => r.abort());
  const page = await ctx.newPage();
  page.on('pageerror', e => console.log('pageerror', e.message.slice(0, 160)));
  const t0 = Date.now();
  await page.goto(`https://velabuilt-dreambuilder.vercel.app/?quality=${Q}&motion=reduced&debug`, { waitUntil: 'domcontentloaded', timeout: 180000 });
  for (let i = 0; i < 16; i++) {
    await page.waitForTimeout(8000);
    const st = await page.evaluate(() => ({ store: !!window.__store, vb: !!window.__vb, frames: window.__frames, keys: window.__store ? Object.keys(window.__store.getState()).filter(k => typeof window.__store.getState()[k] !== 'function').join(',') : '', ready: window.__store?.getState().sceneReady, phase: window.__store?.getState().phase, loading: /Loading the interactive demo/.test(document.body.innerText) }));
    console.log(((Date.now() - t0) / 1000).toFixed(0) + 's', JSON.stringify(st).slice(0, 400));
    if (st.ready) break;
  }
  await browser.close();
})();
