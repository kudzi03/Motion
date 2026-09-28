"""Original score + SFX for the VelaBuilt brag, synthesised from scratch and locked to the
composition's cue list (cues.json, written by render.cjs). D major, 120 BPM, drop on 3.0s,
impact on the 19.0s downbeat. Output: work/score.wav (48 kHz stereo, pre-loudness-normalisation).
"""
import json
import numpy as np
import scipy.signal as sg
from scipy.io import wavfile

SR = 48000
C = json.load(open('cues.json'))
DUR = C['duration']
N = int(round(DUR * SR))
rng = np.random.default_rng(11)

BPM = 120
BEAT = 60 / BPM
DROP, IMPACT = 3.0, 19.0
BARS = [DROP + 2 * BEAT * 2 * k for k in range(8)]          # 3, 5, ... 17
PROG = ['D', 'Bm', 'G', 'A', 'D', 'Bm', 'G', 'Asus']
VOICE = {                                                    # MIDI voicings, maj9 colours
    'D':    [50, 57, 61, 64, 66],
    'Bm':   [47, 54, 57, 61, 62],
    'G':    [43, 50, 54, 57, 59],
    'A':    [45, 52, 57, 61, 64],
    'Asus': [45, 52, 55, 59, 62],
}
ROOT = {'D': 38, 'Bm': 35, 'G': 31, 'A': 33, 'Asus': 33}

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR

def cue_times(kind): return [c for c in C['cues'] if c['type'] == kind]

# ---------------------------------------------------------------- mixing helpers
def buf(): return np.zeros((N, 2))

def place(dst, x, t, gain=1.0, pan=0.0):
    """Add mono (n,) or stereo (n,2) x into dst at time t with equal-power pan."""
    i = int(round(t * SR))
    if i >= N: return
    if x.ndim == 1:
        a = (pan + 1) * np.pi / 4
        x = np.stack([x * np.cos(a), x * np.sin(a)], 1) * np.sqrt(2)
    j = min(N, i + len(x))
    if i < 0: x = x[-i:]; i = 0
    dst[i:j] += x[: j - i] * gain

def sos(kind, f, order=2): return sg.butter(order, f, kind, fs=SR, output='sos')
def filt(x, s): return sg.sosfilt(s, x, axis=0)

def tv_filter(x, fc, btype='low', q=0.707, block=256):
    """Time-varying RBJ biquad; fc is an array of cutoff (Hz) per sample."""
    y = np.zeros_like(x)
    mono = x.ndim == 1
    X = x[:, None] if mono else x
    Y = y[:, None] if mono else y
    zi = np.zeros((2, X.shape[1]))
    for s in range(0, len(X), block):
        f = float(np.clip(fc[min(s + block // 2, len(fc) - 1)], 20, SR * .45))
        w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q); cw = np.cos(w)
        if btype == 'low':  b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        elif btype == 'high': b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        else: b = [al, 0, -al]
        a = [1 + al, -2 * cw, 1 - al]
        b = np.array(b) / a[0]; a = np.array(a) / a[0]
        for ch in range(X.shape[1]):
            Y[s:s + block, ch], zi[:, ch] = sg.lfilter(b, a, X[s:s + block, ch], zi=zi[:, ch])
    return y

def make_ir(rt60=1.9, pre=.022, width=1.0):
    n = int(SR * rt60 * 1.25); t = np.arange(n) / SR
    chans = []
    for _ in range(2):
        w = rng.standard_normal(n)
        lo, hi = filt(w, sos('low', 700)), filt(w, sos('high', 3800))
        mid = w - lo - hi
        d = lambda r: np.exp(-6.91 * t / r)
        ir = lo * d(rt60 * 1.15) + mid * d(rt60) + hi * d(rt60 * .42)
        ir *= np.minimum(1, t / .008)                     # soften the onset
        chans.append(np.concatenate([np.zeros(int(pre * SR)), ir]))
    ir = np.stack(chans, 1)
    m = ir.mean(1, keepdims=True); ir = m + (ir - m) * width
    return ir / np.sqrt((ir ** 2).sum(0)).max()

def reverb(x, ir, wet):
    out = np.stack([sg.fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], 1)
    return out * wet

# ---------------------------------------------------------------- instruments
def kick(v=1.0):
    t = tt(.5)
    f = 45 + 105 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.8)
    body = np.tanh(body * 1.7) / np.tanh(1.7)
    click = filt(rng.standard_normal(len(t)), sos('high', 3000)) * np.exp(-t * 300) * .05
    return (body + click) * v

def clap(v=1.0):
    t = tt(.4)
    bp = filt(rng.standard_normal(len(t)), sos('band', [950, 2800]))
    env = np.zeros_like(t)
    for k, off in enumerate([0, .010, .021]):
        m = t >= off; env[m] += np.exp(-(t[m] - off) * 150) * (.7 if k < 2 else 1)
    env += np.where(t >= .021, np.exp(-(t - .021) * 16) * .3, 0)
    return bp * env * v

def hat(v=1.0, open_=False):
    t = tt(.45 if open_ else .09)
    x = filt(rng.standard_normal(len(t)), sos('high', 8000, 4))
    return x * np.exp(-t * (8 if open_ else 60)) * v

def bass(m, d=.2, v=1.0):
    t = tt(d + .08); ph = 2 * np.pi * mtof(m) * t
    x = np.tanh((np.sin(ph) + .3 * np.sin(2 * ph) + .1 * np.sin(3 * ph)) * 1.5)
    env = np.minimum(1, t / .005) * np.where(t < d, 1, np.exp(-(t - d) * 55)) * np.exp(-t * 2.2)
    return x * env * v

def rhodes(m, d, v=1.0):
    t = tt(d + 1.0); f = mtof(m)
    idx = 1.5 * np.exp(-t * 7) + .25
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    x += np.sin(2 * np.pi * f * 7.02 * t) * np.exp(-t * 35) * .05
    env = np.minimum(1, t / .004) * np.exp(-t * 1.4) * np.where(t < d, 1, np.exp(-(t - d) * 7))
    return x * env * v

def saw(f, t):
    dt = f / SR; p = (f * t) % 1.0
    y = 2 * p - 1
    m = p < dt; x = p[m] / dt; y[m] -= x + x - x * x - 1
    m = p > 1 - dt; x = (p[m] - 1) / dt; y[m] -= x * x + x + x + 1
    return y

def pad_chord(ms, d, att=.35, rel=.9, v=1.0):
    t = tt(d + rel); out = np.zeros((len(t), 2))
    for m in ms:
        for k, det in enumerate([-9, -3, 4, 10]):
            x = saw(mtof(m) * 2 ** (det / 1200), t + rng.uniform(0, 1))
            pan = [-.7, -.25, .25, .7][k]
            a = (pan + 1) * np.pi / 4
            out[:, 0] += x * np.cos(a); out[:, 1] += x * np.sin(a)
    env = np.minimum(1, t / att) * np.where(t < d, 1, np.exp(-(t - d) * 5 / rel))
    return out * env[:, None] * v / (len(ms) * 4)

def pluck(m, v=1.0, d=.55, bright=1.0):
    t = tt(d); f = mtof(m); x = np.zeros_like(t)
    for k in range(1, int(min(22, SR / 2 / f - 1)) + 1):
        x += np.sin(2 * np.pi * k * f * t) / k * np.exp(-t * (5 + 2.1 * k / bright))
    return x * np.minimum(1, t / .002) * v * .6

def bell(m, d=2.6, v=1.0, ratio=3.5, index=1.6, decay=1.7):
    t = tt(d); f = mtof(m)
    x = np.sin(2 * np.pi * f * t + index * np.exp(-t * 3.2) * np.sin(2 * np.pi * f * ratio * t))
    return x * np.minimum(1, t / .003) * np.exp(-t * decay) * v

def noise_sweep(d, f0, f1, shape, btype='band', q=1.2, v=1.0):
    t = tt(d); x = rng.standard_normal((len(t), 2)) * [1, 1]
    fc = f0 * (f1 / f0) ** (t / d)
    return tv_filter(x, fc, btype, q) * shape(t / d)[:, None] * v

def tick(v=1.0, f=2600):
    t = tt(.04)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 320) + filt(rng.standard_normal(len(t)), sos('band', [2500, 7000])) * np.exp(-t * 700) * .5
    return x * v

def blip(m1, m2, v=1.0):
    out = np.zeros(int(.3 * SR))
    for k, m in enumerate([m1, m2]):
        t = tt(.18); x = np.sin(2 * np.pi * mtof(m) * t) * np.minimum(1, t / .006) * np.exp(-t * 22)
        i = int(k * .075 * SR); out[i:i + len(x)] += x
    return out * v

def pop(m, v=1.0):
    t = tt(.16); f = mtof(m) * (1 + .5 * np.exp(-t * 90))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    c = tick(.3, 3200); x[: len(c)] += c
    return x * v

def thock(v=1.0):
    t = tt(.2); f = 190 * (1 - .45 * (1 - np.exp(-t * 40)))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26)
    c = tick(.25, 1400); x[: len(c)] += c
    return x * v

def boom(v=1.0):
    t = tt(2.6); f = 36 + 44 * np.exp(-t * 9)
    x = np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.8) * np.exp(-t * 1.6)
    return x * v

# ---------------------------------------------------------------- arrangement
music, drums, bassb, keys, padb, arp, sfx = buf(), buf(), buf(), buf(), buf(), buf(), buf()
send = buf()                      # reverb send (hall)
t_all = np.arange(N) / SR

# sidechain pump from the kick
kicks = [DROP + i * BEAT for i in range(int((18.5 - DROP) / BEAT))]
side = np.ones(N)
for k in kicks:
    i = int(k * SR); seg = t_all[i:i + int(.4 * SR)] - k
    side[i:i + len(seg)] = np.minimum(side[i:i + len(seg)], 1 - .6 * np.exp(-seg / .085))

# --- intro: Gmaj9 pad swelling open, air, and the core "igniting"
intro_pad = pad_chord(VOICE['G'] + [62], DROP + .2, att=1.1, rel=.6, v=1.0)
place(padb, intro_pad, 0, .85)
place(padb, pad_chord([43 + 12, 50 + 12], DROP + .1, att=1.6, rel=.5), 0, .25)
air = noise_sweep(2.2, 900, 5200, lambda x: np.sin(np.pi * np.clip(x, 0, 1)) ** 1.5, 'band', .7, .05)
place(sfx, air, 0.0, 1.0)
for c in cue_times('ignite'):
    for k, m in enumerate([69, 74, 78, 81]):                       # A4 D5 F#5 A5, arpeggiated
        b = bell(m, 2.4, .5 - k * .06, ratio=4.0, index=1.0, decay=1.3)
        place(sfx, b, c['t'] + k * .055, .16, pan=-.3 + k * .2); place(send, b, c['t'] + k * .055, .22)
    bl = boom(.5)[: int(1.4 * SR)] * np.exp(-tt(1.4) * 1.5)
    place(sfx, bl, c['t'], .35)
for c in cue_times('line'):
    x = tick(.6, 1760); place(sfx, x, c['t'], .08, pan=.15); place(send, x, c['t'], .05)

# --- risers into the drop and into the impact
def riser_shape(x): return np.clip(x, 0, 1) ** 2.4
for c in cue_times('riser'):
    d = c['to'] - c['t']
    r = noise_sweep(d, 400, 7000, riser_shape, 'band', 1.4, .9)
    place(sfx, r, c['t'], .11); place(send, r, c['t'], .06)
    tq = tt(d); gl = np.sin(2 * np.pi * np.cumsum(mtof(62) * 2 ** (2 * tq / d)) / SR) * riser_shape(tq / d) * .5
    place(sfx, gl, c['t'], .03)

# --- groove: drums
crash = filt(rng.standard_normal((int(1.8 * SR), 2)), sos('high', 5000)) * np.exp(-tt(1.8) * 2.4)[:, None]
place(drums, crash, DROP, .06); place(send, crash, DROP, .05)
for k in kicks:
    place(drums, kick(1.0), k, .95)
for b in BARS:
    for beat in (1, 3):
        tb = b + beat * BEAT
        if tb < 18.5: place(drums, clap(1.0), tb, .30, pan=.05); place(send, clap(1.0), tb, .12)
for i, k in enumerate(kicks):
    off = k + BEAT / 2
    lift = off >= 11.0
    place(drums, hat(1.0, open_=lift), off, .07 if lift else .09, pan=.25)
    if lift:
        for g in (.25, .75):
            gh = k + g * BEAT
            if gh < 18.5: place(drums, hat(.5), gh, .05, pan=-.25)
# roll into the impact
for i in range(8):
    tr = 18.5 + i * BEAT / 4
    place(drums, clap(.4 + .6 * i / 7), tr, .18 * (.35 + .65 * i / 7), pan=(-1) ** i * .1)
    place(send, clap(1.0), tr, .06)

# --- bass: off-beat house bass on chord roots
for bi, b in enumerate(BARS):
    ch = PROG[bi]
    for beat in range(4):
        tb = b + beat * BEAT + BEAT / 2
        if tb < 18.5: place(bassb, bass(ROOT[ch] + 12 * (ROOT[ch] < 34), .2, 1.0), tb, .5)

# --- keys: syncopated maj9 stabs; pad underneath
for bi, b in enumerate(BARS):
    ch = PROG[bi]
    for pos, d, v in [(0, .34, 1.0), (6, .2, .75), (10, .3, .85)]:
        tk = b + pos * BEAT / 4
        if tk >= 18.5: continue
        for m in VOICE[ch]:
            x = rhodes(m + 12, d, v)
            place(keys, x, tk, .07, pan=((m % 5) - 2) * .15)
            place(send, x, tk, .025)
    place(padb, pad_chord(VOICE[ch], 2 * BEAT * 2 + .05, att=.25, rel=.5), b, .42 if b < 11 else .5)

# --- arp: second half lift
arp_pat = {'D': [74, 69, 76, 78, 81, 76, 73, 69], 'Bm': [71, 66, 73, 74, 78, 73, 69, 66],
           'G': [74, 71, 78, 79, 83, 78, 74, 71], 'A': [76, 73, 79, 81, 85, 81, 76, 73],
           'Asus': [74, 71, 76, 79, 83, 79, 74, 71]}
for bi, b in enumerate(BARS):
    if b < 11.0: continue
    ch = PROG[bi]
    for s in range(16):
        ts = b + s * BEAT / 4
        if ts >= 18.5: break
        m = arp_pat[ch][s % 8]
        x = pluck(m, .9 if s % 4 == 0 else .6, .4, bright=.9)
        place(arp, x, ts, .09, pan=.35 * np.sin(s * np.pi / 4)); place(send, x, ts, .05)

# --- the impact: sub boom, crash, final Dmaj9 ringing out
place(sfx, boom(1.0), IMPACT, .55)
fcrash = filt(rng.standard_normal((int(3.2 * SR), 2)), sos('band', [2500, 11000])) * np.exp(-tt(3.2) * 1.4)[:, None]
place(sfx, fcrash, IMPACT, .05); place(send, fcrash, IMPACT, .08)
final = VOICE['D'] + [69, 73]
place(padb, pad_chord(final, 3.6, att=.02, rel=1.2), IMPACT, .75)
for m in final:
    x = rhodes(m + 12, 3.0, .9); place(keys, x, IMPACT, .07, pan=((m % 5) - 2) * .18); place(send, x, IMPACT, .05)
for k, m in enumerate([74, 78, 81, 86]):
    b = bell(m, 3.2, .7, ratio=4.0, index=1.2, decay=1.1)
    place(sfx, b, IMPACT + .03 + k * .07, .11, pan=-.3 + k * .2); place(send, b, IMPACT + .03 + k * .07, .2)
place(bassb, bass(38, 1.6, 1.0), IMPACT, .55)
for s, m in enumerate([81, 78, 74, 69, 74, 78]):            # a slowing arp as it rings out
    ts = IMPACT + .9 + s * (.25 + s * .04)
    x = pluck(m, .5, .7, bright=.8); place(arp, x, ts, .07, pan=.3 * np.sin(s)); place(send, x, ts, .09)

# --- UI sound effects, in key and under the music
for c in C['cues']:
    t, k = c['t'], c['type']
    if k == 'whoosh':
        w = noise_sweep(.55, 3200, 500, lambda x: np.sin(np.pi * np.clip(x, 0, 1)) ** 2, 'band', .9, 1.0)
        place(sfx, w, t - .05, .07); place(send, w, t, .03)
    elif k in ('land', 'land2'):
        th = thock(.8); place(sfx, th, t + .12, .12, pan=-.1 if k == 'land' else .2)
    elif k == 'listen':
        x = blip(74, 81, 1.0); place(sfx, x, t, .08, pan=-.1); place(send, x, t, .06)
    elif k == 'speak':
        x = blip(78, 86, 1.0); place(sfx, x, t, .08, pan=.1); place(send, x, t, .06)
    elif k == 'tick':
        x = tick(c.get('gain', 1), 2200); place(sfx, x, t, .045, pan=rng.uniform(-.3, .3))
    elif k == 'soft':
        for j, m in enumerate([78, 81]):
            b = bell(m, 1.4, .6, ratio=4.0, index=.8, decay=2.5); place(sfx, b, t + j * .06, .07); place(send, b, t + j * .06, .08)
    elif k == 'check':
        m = 86 if c.get('up') else 81
        x = pop(m, 1.0); place(sfx, x, t, .09, pan=.15); place(send, x, t, .05)
    elif k == 'notify':
        for j, m in enumerate([81, 86]):
            b = bell(m, 1.8, .9, ratio=4.0, index=1.4, decay=2.2); place(sfx, b, t + j * .09, .12, pan=.2); place(send, b, t + j * .09, .14)
    elif k == 'stop':
        place(sfx, thock(1.0), t, .12)
    elif k == 'step':
        m = [74, 76, 78][c['n']]
        x = pluck(m, 1.0, .35, bright=1.2); place(sfx, x, t, .12, pan=-.2 + .2 * c['n']); place(send, x, t, .05)
    elif k == 'booked':
        for j, m in enumerate([81, 86, 90]):
            b = bell(m, 1.6, .8, ratio=4.0, index=1.1, decay=2.4); place(sfx, b, t + j * .045, .1, pan=-.2 + .2 * j); place(send, b, t + j * .045, .12)

# ---------------------------------------------------------------- mix
padb = tv_filter(padb, np.interp(t_all, [0, 2.8, 3.0, 11, 11.01, 18.4, 19.0, 22.5], [260, 1500, 1100, 1300, 1700, 2600, 2400, 900]), 'low', .8)
keys = filt(keys, sos('high', 180))
bassb = filt(bassb, sos('low', 900))
arp = filt(arp, sos('high', 300))
padb *= side[:, None] ** .9 * 1.0
keys *= side[:, None] ** .6
bassb *= side[:, None] ** .8
arp *= side[:, None] ** .5

music = drums + bassb + keys + padb + arp
ir = make_ir(2.1, width=1.0)
wet = reverb(send + keys * .5 + padb * .25, ir, .55)
mix = music + sfx + wet
mix = filt(mix, sos('high', 28))

# gentle glue compression, then a soft limiter
env = np.abs(mix).max(1)
env = sg.lfilter([1 - np.exp(-1 / (.12 * SR))], [1, -np.exp(-1 / (.12 * SR))], env)
gain = np.minimum(1, (np.maximum(env, 1e-6) / .5) ** (-.25))
mix *= np.where(env > .5, gain, 1)[:, None]
# fade the last 0.7s so the ring-out ends exactly with the picture
fade = np.clip((DUR - t_all) / .7, 0, 1) ** 1.5
mix *= fade[:, None]
mix *= np.minimum(1, t_all / .01)[:, None]
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.1) / np.tanh(1.1) * .89
wavfile.write('score.wav', SR, (mix * 32767).astype(np.int16))
print(f'score.wav  {DUR:.2f}s  peak(pre)={peak:.3f}  cues={len(C["cues"])}')
