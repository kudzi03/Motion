const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.log('pageerror', e.message.slice(0, 200)));
  const t0 = Date.now();
  await page.goto('https://velabuilt-dreambuilder.vercel.app/?quality=standard', { waitUntil: 'domcontentloaded', timeout: 90000 });
  for (let i = 0; i < 12; i++) {
    await page.waitForTimeout(5000);
    const st = await page.evaluate(() => ({ txt: document.body.innerText.slice(0, 300).replace(/\n+/g, ' | '), canvas: !!document.querySelector('canvas') }));
    console.log(((Date.now() - t0) / 1000).toFixed(0) + 's', JSON.stringify(st));
    if (!/Loading/i.test(st.txt) && i > 1) break;
  }
  await page.screenshot({ path: 'db-intro.png' });
  const btns = await page.$$eval('button, a', els => els.map(e => (e.getAttribute('aria-label') || e.innerText || '').trim().replace(/\s+/g, ' ')).filter(Boolean).slice(0, 60));
  console.log(btns.join(' || '));
  await browser.close();
})();
