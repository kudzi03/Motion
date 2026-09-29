const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 1100, height: 1300 }, deviceScaleFactor: 3 });
  await ctx.route(/_vercel\/insights|vitals\.vercel/, r => r.abort());
  const page = await ctx.newPage();
  await page.goto('https://velabuilt.com/system-lab', { waitUntil: 'networkidle', timeout: 90000 }).catch(() => {});
  await page.waitForTimeout(2000);
  // the dark module map is the first large dark block after the hero
  const handle = await page.evaluateHandle(() => document.querySelector('.lab-station').closest('ul').parentElement);
  const el = handle.asElement();
  if (!el) { console.log('map not found'); await page.screenshot({ path: 'lab-full.png', fullPage: false }); }
  else { await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(2500); const b = await el.boundingBox(); console.log('map box', JSON.stringify(b)); await el.screenshot({ path: 'lab-map-3x.png' }); }
  await browser.close();
})();
