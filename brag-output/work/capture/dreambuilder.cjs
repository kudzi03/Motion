// Capture the live VelaBuilt DreamBuilder demo, driven through its real flow.
// Analytics requests are blocked so automated runs don't count as visitors.
// Never touches the "Build this for my business" enquiry form.
// node dreambuilder.cjs vert|desk
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const MODE = process.argv[2] || 'vert';
const VP = MODE === 'vert' ? { width: 432, height: 936, dpr: 2.5, q: 'mobile' } : { width: 1440, height: 900, dpr: 1.35, q: 'mobile' };
const OUT = `db-${MODE}`;
fs.mkdirSync(OUT, { recursive: true });
const BASE = 'https://velabuilt-dreambuilder.vercel.app/';
const log = (...a) => console.log(new Date().toISOString().slice(11, 19), MODE, ...a);

(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({
    viewport: { width: VP.width, height: VP.height }, deviceScaleFactor: VP.dpr,
    isMobile: MODE === 'vert', hasTouch: MODE === 'vert',
  });
  await ctx.route(/\/api\/(track|lead)|_vercel\/insights|vitals\.vercel/, r => r.abort());
  const page = await ctx.newPage();
  page.setDefaultTimeout(240000);

  const shot = async (name, settle = 2500) => {
    await page.waitForTimeout(settle);
    const t = Date.now();
    await page.screenshot({ path: `${OUT}/${name}.png`, timeout: 300000 });
    log('shot', name, ((Date.now() - t) / 1000).toFixed(0) + 's');
  };
  const open = async (qs = '') => {
    await page.goto(`${BASE}?quality=${VP.q}&motion=reduced${qs}`, { waitUntil: 'domcontentloaded', timeout: 120000 });
    await page.waitForFunction(() => !/Loading the interactive demo/.test(document.body.innerText), null, { timeout: 240000 });
    await page.waitForTimeout(4000);
  };
  const click = async (loc, label) => {
    try { await loc.first().click({ timeout: 60000 }); log('click', label); return true; }
    catch (e) { log('MISS', label, e.message.split('\n')[0]); return false; }
  };
  const btn = name => page.getByRole('button', { name });

  // 1. arrival
  await open();
  await shot('01-intro', 1500);

  // 2. structural steel: the frame, then the full business flow
  await click(page.locator('button.tile', { hasText: 'Structural Steel' }), 'tile steel');
  await shot('02-steel-explore', 9000);
  await click(btn(/Request fabrication quote/), 'cta steel');
  await page.waitForTimeout(1500);
  await click(page.getByRole('radio', { name: /1–3 months/ }), 'timeline');
  await click(page.getByRole('radio', { name: /^WhatsApp$/ }), 'channel');
  await shot('03-steel-qualify', 2000);
  await click(btn(/Send my request/), 'send (demo, local only)');
  await shot('04-flow-early', 2500);
  await shot('05-flow-crm', 5000);
  await shot('06-flow-followup', 3500);
  await click(page.locator('.bubble__slot'), 'slot');
  await shot('07-flow-booked', 3000);
  await shot('08-flow-job', 4000);
  await shot('09-reveal', 6000);

  // 3. other showrooms, straight in
  for (const [id, n] of [['remodeling', '10-kitchen'], ['roofing', '11-roof'], ['solar', '12-solar'], ['landscaping', '13-outdoor']]) {
    await open(`&industry=${id}`);
    await shot(n, 9000);
  }
  await browser.close();
  log('done');
})().catch(e => { console.error(e); process.exit(1); });
