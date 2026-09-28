// Render QA stills at given times: node stills.cjs out_dir t1 t2 ...
const fs = require('fs');
const path = require('path');
const { openComposition } = require('./lib.cjs');

(async () => {
  const [outDir, ...ts] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const { page, close } = await openComposition();
  for (const t of ts.map(Number)) {
    await page.evaluate(t => window.__seek(t), t);
    await page.screenshot({ path: path.join(outDir, `t${t.toFixed(2).padStart(5, '0')}.png`) });
  }
  await close();
})().catch(e => { console.error(e); process.exit(1); });
