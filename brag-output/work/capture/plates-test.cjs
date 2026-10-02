// Clean 3D plates from the live DreamBuilder: UI hidden, subject centred, same camera, two times of day.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const Q = process.argv[2] || 'high';
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 432, height: 768 }, deviceScaleFactor: 2.5 });
  await ctx.route(/\/api\/(track|lead)|_vercel\/insights|vitals\.vercel/, r => r.abort());
  const page = await ctx.newPage();
  page.setDefaultTimeout(600000);
  const t0 = Date.now(); const log = (...a) => console.log(((Date.now() - t0) / 1000).toFixed(0) + 's', ...a);
  await page.goto(`https://velabuilt-dreambuilder.vercel.app/?quality=${Q}&motion=reduced&debug`, { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForFunction(() => window.__store?.getState().sceneReady, null, { timeout: 400000, polling: 500 });
  log('scene ready');
  await page.evaluate(() => { window.__settle = true; });
  await page.addStyleTag({ content: '.topbar,.panel,.intro,.hint,.compare,.switcher,.flow,.reveal,.loader,.callout,.tag3d,.pin,.skip,[class*="toast"]{display:none!important}' });
  const frames = async n => { const s = await page.evaluate(() => window.__frames || 0); await page.waitForFunction(t => (window.__frames || 0) >= t, s + n, { timeout: 900000, polling: 250 }); };
  for (const [name, evening] of [['garden-day', false], ['garden-night', true]]) {
    await page.evaluate(ev => { window.__bare = true; const s = window.__store.getState(); s.selectIndustry('landscaping'); s.setInsets({ top: 0, right: 0, bottom: 0, left: 0 }); s.set({ landscaping: { ...s.landscaping, evening: ev } }); }, evening);
    await page.waitForTimeout(2000);
    await frames(8);
    await page.screenshot({ path: `plates/${name}-${Q}.png`, timeout: 600000 });
    log('shot', name, JSON.stringify(await page.evaluate(() => { const s = window.__store.getState(); return { phase: s.phase, ind: s.industry, evening: s.landscaping?.evening }; })));
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
