const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const q = process.argv[2] || 'mobile';
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
  const t0 = Date.now();
  await page.goto(`https://velabuilt-dreambuilder.vercel.app/?quality=${q}&motion=reduced`, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForFunction(() => !/Loading the interactive demo/.test(document.body.innerText), null, { timeout: 150000 }).catch(() => console.log('still loading'));
  console.log('loaded', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  const ft = await page.evaluate(() => new Promise(r => { const ts = []; const f = t => { ts.push(t); if (ts.length < 6) requestAnimationFrame(f); else r(ts.slice(1).map((x, i) => (x - ts[i]).toFixed(0))); }; requestAnimationFrame(f); }));
  console.log('frame ms', ft.join(','));
  const s0 = Date.now();
  await page.screenshot({ path: `db-intro-${q}.png`, timeout: 240000 });
  console.log('shot', ((Date.now() - s0) / 1000).toFixed(1) + 's');
  await browser.close();
})();
