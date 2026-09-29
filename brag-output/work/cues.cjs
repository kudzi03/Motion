// Write the composition's cue list for the audio script.
const fs = require('fs');
const { openComposition } = require('./lib.cjs');
(async () => { const { meta, close } = await openComposition(); fs.writeFileSync(process.argv[2] || 'cues2.json', JSON.stringify(meta, null, 1)); console.log(meta.cues.length, 'cues', meta.duration, 's'); await close(); })();
