// Render the finished agent conversation as a still for the system flow's "AI response" step.
const { openComposition } = require('./lib.cjs');
(async () => {
  const { page, close } = await openComposition({ dpr: 2 });
  await page.evaluate(() => window.__seek(8.95));
  await page.locator('#chat').screenshot({ path: 'agent-card.png' });
  await close();
})();
