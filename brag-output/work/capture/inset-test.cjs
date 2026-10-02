// Framing test: reserve the top of the screen so the camera sets the house lower, with open sky above.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const TOP = parseInt(process.argv[2] || '260', 10);
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 432, height: 768 }, deviceScaleFactor: 1.25 });
  await ctx.route(/\/api\/(track|lead)|_vercel\/insights|vitals\.vercel/, r => r.abort());
  const page = await ctx.newPage(); page.setDefaultTimeout(900000);
  await page.goto('https://velabuilt-dreambuilder.vercel.app/?quality=mobile&motion=reduced&debug', { waitUntil: 'domcontentloaded', timeout: 180000 });
  await page.waitForFunction(() => window.__store?.getState().sceneReady, null, { timeout: 400000, polling: 500 });
  await page.addStyleTag({ content: '.topbar,.panel,.intro,.hint,.compare,.switcher,.flow,.reveal,.loader,.callout,.tag3d,.pin,.skip{display:none!important}' });
  const frames = async n => { const s = await page.evaluate(() => window.__frames || 0); await page.waitForFunction(t => (window.__frames || 0) >= t, s + n, { timeout: 900000, polling: 100 }); };
  for (const [name, top] of [['inset', TOP], ['inset2', Math.round(TOP * 1.5)]]) {
    await page.evaluate(top => { window.__settle = true; window.__bare = false; const s = window.__store.getState(); s.selectIndustry('landscaping'); s.setInsets({ top, right: 0, bottom: 0, left: 0 }); s.set({ landscaping: { ...s.landscaping, evening: false } }); }, top);
    await page.waitForTimeout(1500); await frames(8);
    await page.screenshot({ path: `plates/${name}-${top}.png` });
    console.log('shot', name, top);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
