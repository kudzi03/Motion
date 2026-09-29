// Section-by-section captures of live sites at high DPR. Read-only: no form is ever submitted.
// node sites.cjs <name> <url> vert|desk [steps]
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const [name, url, mode = 'vert', stepsArg = '14'] = process.argv.slice(2);
const VP = mode === 'vert' ? { width: 432, height: 936, dpr: 2.5 } : { width: 1440, height: 900, dpr: 1.5 };
const OUT = `${name}-${mode}`;
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: VP.width, height: VP.height }, deviceScaleFactor: VP.dpr, isMobile: mode === 'vert', hasTouch: mode === 'vert' });
  await ctx.route(/\/api\/(track|lead|enquiry)|_vercel\/insights|vitals\.vercel|google-analytics|googletagmanager/, r => r.abort());
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 }).catch(() => {});
  await page.waitForTimeout(2500);
  for (const t of ['Accept', 'Accept all', 'Got it', 'OK', 'Not now']) {
    const b = page.getByRole('button', { name: t, exact: true });
    if (await b.count()) await b.first().click({ timeout: 1500 }).catch(() => {});
  }
  const H = await page.evaluate(() => document.documentElement.scrollHeight);
  const step = Math.round(VP.height * 0.85);
  const n = Math.min(parseInt(stepsArg, 10), Math.ceil(H / step));
  for (let i = 0; i < n; i++) {
    await page.evaluate(y => window.scrollTo(0, y), i * step);
    await page.waitForTimeout(1600);
    await page.screenshot({ path: `${OUT}/${String(i).padStart(2, '0')}.png` });
  }
  console.log(name, mode, 'height', H, 'shots', n);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
