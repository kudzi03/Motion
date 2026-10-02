const { openComposition } = require('./lib.cjs');
(async () => {
  const { page, close } = await openComposition();
  const at = async (t, sel) => { await page.evaluate(t => window.__seek(t), t); return page.evaluate(sel => { const r = document.querySelector(sel).getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)].join(','); }, sel); };
  console.log('send @8.9', await at(8.9, '#send'));
  console.log('slotA @13.1', await at(13.1, '#slotA'));
  console.log('obj @12.5', await at(12.5, '#obj'));
  console.log('booked @13.6', await at(13.6, '#booked'));
  console.log('obj @11.5', await at(11.5, '#obj'));
  console.log('qRow @11.6', await at(11.6, '#qRow'));
  await close();
})();
