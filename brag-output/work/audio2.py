"""v2 score + sound design, locked to the v2 composition's cue list (cues.json).
Technological and premium, not EDM: a pulsing filtered-bass sequence, restrained drums that
build through the system and proof sections, low hits on every major transition, and
interface sounds on every UI action. D minor, resolving to D major on the end card. 120 BPM.
Output: score2.wav (48 kHz stereo, pre-normalisation).
"""
import json
import numpy as np
import scipy.signal as sg
from scipy.io import wavfile

# instruments, helpers and reverb from the v1 score
_src = open('audio.py').read().split('# ---------------------------------------------------------------- arrangement')[0]
_src = _src.replace("C = json.load(open('cues.json'))", "C = json.load(open('cues2.json'))")
exec(_src)

BEAT = .5
t_all = np.arange(N) / SR
drums, bassb, keys, padb, arp, sfx, send = buf(), buf(), buf(), buf(), buf(), buf(), buf()

# harmony by section (MIDI voicings)
CH = {
    'Dm9':    ([50, 57, 60, 64, 65], 38),
    'Bbmaj9': ([46, 53, 57, 60, 62], 34),
    'Fmaj9':  ([41, 48, 52, 55, 57], 41),
    'C6':     ([48, 52, 55, 57, 62], 36),
    'Gm9':    ([43, 50, 53, 57, 58], 43),
    'A7sus':  ([45, 52, 55, 59, 62], 33),
    'Dadd9':  ([50, 57, 62, 64, 66, 69], 38),
}
SECTIONS = [(0, 2, 'Dm9'), (2, 4, 'Dm9'), (4, 6, 'Bbmaj9'), (6, 8, 'Fmaj9'), (8, 10, 'C6'),
            (10, 12, 'Dm9'), (12, 14, 'Bbmaj9'), (14, 15, 'Gm9'), (15, 17, 'Dm9'), (17, 19, 'Bbmaj9'),
            (19, 21, 'Gm9'), (21, 22, 'A7sus'), (22, 25, 'Dadd9')]
def chord_at(t):
    for a, b, c in SECTIONS:
        if a <= t < b: return c
    return 'Dadd9'

def energy(t):
    """0..1 build: intro, craft, intelligence, system builds, proof peaks, positioning breathes."""
    return float(np.interp(t, [0, 2, 6, 10, 14.5, 15, 19, 19.01, 22, 25], [.2, .38, .5, .66, .84, 1, 1, .45, .6, 0]))

# ---- pad, all the way through (the bed)
for a, b, c in SECTIONS:
    v, _ = CH[c]
    att = .6 if a == 0 else (.02 if a == 22 else .25)
    place(padb, pad_chord(v, b - a + .1, att=att, rel=.9 if a == 22 else .4), a, .55 if a < 22 else .8)

# ---- pulsing bass sequence: 16ths, root + octave pattern, filter opens with energy
for k in range(int(22 / (BEAT / 4))):
    ts = k * BEAT / 4
    if 19 <= ts < 19.5: continue                          # the breath after the impact
    root = CH[chord_at(ts)][1]
    pat = [0, 12, 0, 7, 0, 12, 10, 12][k % 8]
    v = (.9 if k % 4 == 0 else .55) * (.35 + .65 * energy(ts)) * (1 if ts >= 2 else .5 + .5 * ts / 2)
    place(bassb, bass(root + pat, .1, v), ts, .32)

# ---- drums: restrained, build with energy
kick_times = []
for k in range(int((22 - 2) / BEAT)):
    tb = 2 + k * BEAT
    if 19 <= tb < 19.5 or tb >= 21.75: continue
    if 19.5 <= tb < 22 and k % 2: continue                # half-time in positioning
    kick_times.append(tb)
    place(drums, kick(1.0), tb, .85 * (.4 + .6 * energy(tb)))
for k in range(int((22 - 2) / BEAT)):
    tb = 2 + k * BEAT
    off = tb + BEAT / 2
    if off >= 21.75 or 19 <= off < 19.6: continue
    e = energy(off)
    place(drums, hat(1.0, open_=(e > .8 and k % 2 == 1)), off, .05 + .05 * e, pan=.25)
    if e > .66:                                           # 16th ghost hats once the system builds
        for g in (.25, .75):
            place(drums, hat(.5), tb + g * BEAT, .035 * e, pan=-.25)
    if k % 2 == 1 and tb >= 6 and not (19 <= tb < 22):    # backbeat enters with the agent
        place(drums, clap(1.0), tb, .16 + .12 * e, pan=.05); place(send, clap(1.0), tb, .08)
# roll into the proof section
for i in range(8):
    tr = 14.5 + i * BEAT / 8
    place(drums, clap(.35 + .65 * i / 7), tr, .1 * (.4 + .6 * i / 7), pan=(-1) ** i * .1)

# ---- plucked arp from the system section: the machinery ticking over
ARP = {'Dm9': [74, 69, 72, 76, 77, 76, 72, 69], 'Bbmaj9': [70, 65, 69, 72, 74, 72, 69, 65], 'Fmaj9': [72, 67, 69, 72, 76, 72, 69, 67],
       'C6': [72, 67, 69, 74, 76, 74, 69, 67], 'Gm9': [70, 67, 69, 74, 77, 74, 69, 67], 'A7sus': [69, 64, 67, 71, 74, 71, 67, 64]}
for k in range(int((19 - 10) / (BEAT / 4))):
    ts = 10 + k * BEAT / 4
    c = chord_at(ts)
    m = ARP[c][k % 8] + (12 if ts >= 15 and k % 8 == 4 else 0)
    x = pluck(m, .8 if k % 4 == 0 else .5, .35, bright=.8 + .4 * energy(ts))
    place(arp, x, ts, .05 + .05 * energy(ts), pan=.35 * np.sin(k * np.pi / 4)); place(send, x, ts, .04)

# ---- keys: sparse maj9 stabs in the craft + agent sections
for bar in range(2, 10, 2):
    for pos, d in [(0, .5), (6, .25)]:
        tk = bar + pos * BEAT / 4
        for m in CH[chord_at(tk)][0]:
            x = rhodes(m + 12, d, .8); place(keys, x, tk, .045, pan=((m % 5) - 2) * .15); place(send, x, tk, .02)

# ---- sound design, from the composition's cues
def sub_hit(v=1.0, d=1.2, f0=62, f1=34):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * 14)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.6) * np.exp(-t * 3.2) * v
def air(d=.5, f0=2600, f1=600, v=1.0):
    return noise_sweep(d, f0, f1, lambda x: np.sin(np.pi * np.clip(x, 0, 1)) ** 2, 'band', .9, v)
def shimmer(d=.9, v=1.0):
    return noise_sweep(d, 3000, 9000, lambda x: np.sin(np.pi * np.clip(x, 0, 1)) ** 1.5, 'band', 2.5, v)

node_notes = [62, 65, 69, 72]
for c in C['cues']:
    t, k = c['t'], c['type']
    if k == 'hook':
        place(sfx, sub_hit(1.0, 1.6, 70, 36), t, .5); place(sfx, tick(.8, 2400), t, .06)
        place(sfx, noise_sweep(1.6, 400, 2200, lambda x: np.exp(-x * 2.2), 'band', .7, 1), t, .03)
    elif k == 'lock':
        place(sfx, tick(.7, 1900 + 150 * (t * 10 % 4)), t, .05, pan=.2)
    elif k == 'deal':
        place(sfx, air(.35, 1800, 500), t - .05, .05, pan=rng.uniform(-.4, .4)); place(sfx, thock(.5), t + .25, .06)
    elif k == 'riser':
        d = c['to'] - t
        r = noise_sweep(d, 500, 6500, lambda x: np.clip(x, 0, 1) ** 2.2, 'band', 1.3, 1)
        place(sfx, r, t, .08); place(send, r, t, .04)
    elif k in ('hit', 'proof'):
        n = c.get('n', 0)
        place(sfx, sub_hit(.9, .9, 66 - n * 3, 36), t, .42 if k == 'hit' else .36)
        place(sfx, air(.3, 3500, 900), t - .02, .035, pan=(-1) ** n * .3)
        place(sfx, tick(.6, 1500), t, .05)
    elif k == 'cut':
        place(sfx, air(.4, 3000, 700), t - .12, .05, pan=.2); place(sfx, tick(.5, 2200), t, .04)
    elif k == 'whoosh':
        w = air(.55, 3400, 450); place(sfx, w, t - .05, .07); place(send, w, t, .03)
    elif k == 'msg':
        place(sfx, blip(76, 81, .9), t, .06, pan=.2); place(send, blip(76, 81, .9), t, .04)
    elif k == 'reply':
        place(sfx, blip(81, 86, .9), t, .065, pan=-.2); place(send, blip(81, 86, .9), t, .05)
    elif k == 'qualify':
        for j, m in enumerate([74, 77, 81]):
            b = bell(m, 1.2, .6, ratio=4.0, index=.8, decay=3.0); place(sfx, b, t + .1 + j * .12, .06, pan=-.2 + .2 * j)
        place(sfx, shimmer(.8), t + .05, .03)
    elif k == 'tap':
        place(sfx, tick(1.0, 1800), t, .1); place(sfx, thock(.5), t, .05)
    elif k == 'booked':
        for j, m in enumerate([81, 86]):
            b = bell(m, 1.6, .8, ratio=4.0, index=1.2, decay=2.4); place(sfx, b, t + j * .08, .09, pan=.15); place(send, b, t + j * .08, .1)
    elif k == 'node':
        n = c['n']
        x = pluck(node_notes[n], 1.0, .45, bright=1.2); place(sfx, x, t, .11, pan=-.3 + .2 * n); place(send, x, t, .05)
        place(sfx, tick(.6, 2000 + 200 * n), t, .05)
    elif k == 'done':
        place(sfx, sub_hit(.8, .9, 60, 36), t, .32)
        for j, m in enumerate([74, 78, 81]):
            b = bell(m, 1.8, .8, ratio=4.0, index=1.0, decay=2.0); place(sfx, b, t + j * .05, .08); place(send, b, t + j * .05, .1)
    elif k == 'impact':
        place(sfx, sub_hit(1.0, 2.2, 74, 32), t, .6)
        cr = filt(rng.standard_normal((int(2.4 * SR), 2)), sos('band', [2500, 10000])) * np.exp(-tt(2.4) * 1.8)[:, None]
        place(sfx, cr, t, .035); place(send, cr, t, .06)
    elif k == 'word':
        place(sfx, tick(.8, 1700), t, .06); place(sfx, sub_hit(.4, .5, 60, 40), t, .14)
    elif k == 'connect':
        place(sfx, shimmer(1.2), t, .05); place(send, shimmer(1.2), t, .05)
        for j in range(8):
            place(sfx, tick(.4, 2600 + j * 120), t + .07 * j + .05, .025, pan=-.5 + j / 7)
    elif k == 'ignite':
        for j, m in enumerate([69, 74, 77, 81]):
            b = bell(m, 2.2, .5, ratio=4.0, index=1.0, decay=1.4); place(sfx, b, t + j * .05, .06, pan=-.3 + .2 * j); place(send, b, t + j * .05, .12)
    elif k == 'end':
        place(sfx, sub_hit(1.0, 2.8, 62, 30), t, .55)
        for j, m in enumerate([74, 78, 81, 86]):
            b = bell(m, 3.0, .7, ratio=4.0, index=1.1, decay=1.0); place(sfx, b, t + .03 + j * .07, .08, pan=-.3 + .2 * j); place(send, b, t + .03 + j * .07, .16)
        for m in CH['Dadd9'][0]:
            x = rhodes(m + 12, 2.6, .9); place(keys, x, t, .06, pan=((m % 5) - 2) * .18); place(send, x, t, .05)
    elif k == 'url':
        place(sfx, tick(.8, 2200), t, .05); place(send, tick(.8, 2200), t, .04)

# ---- mix (same chain as v1)
side = np.ones(N)
for kt in kick_times:
    i = int(kt * SR); seg = t_all[i:i + int(.4 * SR)] - kt
    side[i:i + len(seg)] = np.minimum(side[i:i + len(seg)], 1 - .55 * np.exp(-seg / .09))
cut = np.interp(t_all, [0, 1.9, 2.0, 6, 10, 15, 19, 19.01, 21.9, 22, 25], [300, 900, 700, 900, 1300, 2600, 2600, 800, 1600, 2200, 700])
padb = tv_filter(padb, cut, 'low', .8)
bassb = tv_filter(bassb, np.interp(t_all, [0, 1.95, 2, 6, 10, 15, 19, 22], [180, 380, 420, 600, 900, 1500, 700, 700]), 'low', 1.1)
keys = filt(keys, sos('high', 180)); arp = filt(arp, sos('high', 300))
padb *= side[:, None] ** .9; keys *= side[:, None] ** .6; bassb *= side[:, None] ** .7; arp *= side[:, None] ** .5
music = drums + bassb + keys + padb + arp
wet = reverb(send + keys * .5 + padb * .25, make_ir(2.2), .55)
mix = filt(music + sfx + wet, sos('high', 28))
env = np.abs(mix).max(1)
env = sg.lfilter([1 - np.exp(-1 / (.12 * SR))], [1, -np.exp(-1 / (.12 * SR))], env)
gain = np.minimum(1, (np.maximum(env, 1e-6) / .5) ** (-.25))
mix *= np.where(env > .5, gain, 1)[:, None]
mix *= (np.clip((DUR - t_all) / .9, 0, 1) ** 1.5)[:, None]
mix *= np.minimum(1, t_all / .004)[:, None]
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.1) / np.tanh(1.1) * .89
wavfile.write('score2.wav', SR, (mix * 32767).astype(np.int16))
print(f'score2.wav {DUR:.2f}s cues={len(C["cues"])}')
