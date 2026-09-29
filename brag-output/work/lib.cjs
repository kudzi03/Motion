// Shared helpers: a static server for the composition and headless Chromium pages pointed at it.
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const COMP = path.resolve(__dirname, process.env.COMP || '../composition-v2');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.json': 'application/json' };

function serve() {
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const p = path.join(COMP, decodeURIComponent(new URL(req.url, 'http://x').pathname));
      if (!p.startsWith(COMP) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

async function openComposition({ width = 1080, height = 1920, pages = 1, dpr = parseFloat(process.env.DPR || '1') } = {}) {
  const srv = await serve();
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--disable-lcd-text'] });
  const url = `http://127.0.0.1:${srv.address().port}/index.html?render=1`;
  const list = [];
  for (let i = 0; i < pages; i++) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: dpr });
    page.on('console', m => { if (['error', 'warning'].includes(m.type())) console.log('[page]', m.type(), m.text()); });
    page.on('pageerror', e => console.log('[pageerror]', e.message));
    await page.goto(url, { waitUntil: 'load' });
    await page.evaluate(() => window.__ready);
    list.push(page);
  }
  const meta = await list[0].evaluate(() => ({ duration: window.__duration, fps: window.__fps, cues: window.__cues, scenes: window.__scenes }));
  const close = async () => { await browser.close(); srv.close(); };
  return { page: list[0], pages: list, meta, close };
}

module.exports = { openComposition, COMP };
