"""v3 'after hours' score + sound design, locked to the v3 composition's cue list (cues3.json).
Calm and cinematic: a warm day chord under the brand, a sparse minor night with a soft plucked
pulse while the system works, a slow swell through 'while you sleep', and a D major sunrise.
Typing uses real CC0 keystrokes (Keyboard Soundpack #1 by unicae_games, via the brag skill);
the rest is synthesised. Output: score3.wav (48 kHz stereo, pre-normalisation).
"""
import glob
import subprocess
import numpy as np
import scipy.signal as sg
from scipy.io import wavfile

_src = open('audio.py').read().split('# ---------------------------------------------------------------- arrangement')[0]
_src = _src.replace("C = json.load(open('cues.json'))", "C = json.load(open('cues3.json'))")
exec(_src)

t_all = np.arange(N) / SR
music, sfx, send = buf(), buf(), buf()

# ---- CC0 keystrokes, decoded once
KEYDIR = '/home/user/latent-spaces/brag/skills/brag/assets/sfx/keyboard'
def load_wav(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x / (np.abs(x).max() + 1e-9)
KEYS = [load_wav(p) for p in sorted(glob.glob(f'{KEYDIR}/keypress-*.wav'))]
print('keystrokes loaded:', len(KEYS))

# ---- harmony across the night
CH = {
    'Dmaj9':  [50, 57, 61, 64, 66],
    'Bm11':   [47, 54, 57, 61, 64],
    'Gmaj9':  [43, 50, 54, 57, 62],
    'Em9':    [40, 47, 54, 55, 62],
    'Asus':   [45, 52, 57, 59, 62],
    'Dadd9':  [50, 57, 62, 64, 66, 69],
}
SECTIONS = [(0, 2.72, 'Dmaj9', .5), (2.72, 6.3, 'Bm11', .55), (6.3, 9.4, 'Gmaj9', .5), (9.4, 12.0, 'Em9', .5),
            (12.0, 14.25, 'Bm11', .5), (14.25, 17.35, 'Asus', .62), (17.35, 24.0, 'Dadd9', .75)]
for a, b, c, g in SECTIONS:
    att = 1.4 if c in ('Asus',) else (.9 if a == 0 else .5)
    place(music, pad_chord(CH[c], b - a + .4, att=att, rel=1.4), a, g)
    if c in ('Dmaj9', 'Dadd9'):
        for m in CH[c]:
            x = rhodes(m + 12, min(3.0, b - a), .7); place(music, x, a + .02, .05, pan=((m % 5) - 2) * .15); place(send, x, a, .05)

# ---- night pulse: a soft plucked figure while the system works (≈ 92 BPM eighths)
STEP = 60 / 92 / 2
FIG = {'Bm11': [71, 66, 69, 73], 'Gmaj9': [67, 62, 66, 69], 'Em9': [64, 59, 62, 66], 'Asus': [69, 64, 66, 71]}
def chord_at(t):
    for a, b, c, g in SECTIONS:
        if a <= t < b: return c
    return 'Dadd9'
k = 0; ts = 3.4
while ts < 17.2:
    c = chord_at(ts)
    if c in FIG:
        dens = 1 if 6.3 <= ts < 14.25 else (.5 if ts < 6.3 else .7)
        if dens >= 1 or k % 2 == 0:
            m = FIG[c][k % 4] + (12 if k % 8 >= 6 else 0)
            x = pluck(m, .8 if k % 4 == 0 else .55, .5, bright=.7)
            place(music, x, ts, .045 * (1 if ts > 6.3 else .7), pan=.3 * np.sin(k * .9)); place(send, x, ts, .05)
    k += 1; ts += STEP
# low heartbeat under the night
for tb in np.arange(3.4, 14.25, STEP * 4):
    t = tt(.5); f = 52 + 40 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    place(music, x, tb, .12)

# ---- sound design from cues
def sub_hit(v=1.0, d=1.4, f0=70, f1=32):
    t = tt(d); f = f1 + (f0 - f1) * np.exp(-t * 10)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * 1.5) * np.exp(-t * 2.6) * v
def air(d=.6, f0=2600, f1=500, v=1.0, shape=lambda x: np.sin(np.pi * np.clip(x, 0, 1)) ** 2):
    return noise_sweep(d, f0, f1, shape, 'band', .9, v)
def shimmer(d=.9, v=1.0):
    return noise_sweep(d, 3500, 9500, lambda x: np.sin(np.pi * np.clip(x, 0, 1)) ** 1.5, 'band', 2.5, v)
rk = np.random.default_rng(3)
def key(v=1.0):
    return KEYS[rk.integers(len(KEYS))] * v

for c in C['cues']:
    t, kd = c['t'], c['type']
    if kd == 'open':
        place(sfx, shimmer(1.6), t, .03)
    elif kd == 'del':
        place(sfx, key(.8), t, .1, pan=.1)
    elif kd == 'portal':
        r = noise_sweep(.7, 6000, 300, lambda x: np.clip(x, 0, 1) ** .6 * np.clip(1 - x, 0, 1) ** .3 * 2, 'band', 1.1, 1)
        place(sfx, r, t - .1, .08); place(send, r, t, .06)
        place(sfx, sub_hit(1.0, 1.8, 66, 30), t + .55, .26)
    elif kd == 'line':
        place(sfx, air(.5, 1800, 700), t - .1, .03)
    elif kd == 'sleep':
        place(sfx, air(.8, 1500, 600), t - .1, .035)
        sw = noise_sweep(3.0, 300, 4000, lambda x: np.clip(x, 0, 1) ** 2.2, 'band', 1.4, 1)
        place(sfx, sw, t + .2, .04); place(send, sw, t + .2, .05)
    elif kd == 'pill':
        place(sfx, thock(.5), t, .08); place(sfx, air(.4, 2400, 900), t - .05, .03)
    elif kd == 'key':
        # the on-screen typing is sped up (~27 chars/s); a click on every other character reads as a fast typist, not a rattle
        if c['i'] % 2 == 0: place(sfx, key(.65 + .35 * rk.random()), t + rk.uniform(0, .012), .09, pan=rk.uniform(-.15, .15))
    elif kd == 'send':
        place(sfx, tick(.9, 1900), t, .09); place(sfx, air(.45, 900, 3600, shape=lambda x: np.clip(x, 0, 1) ** .5 * (1 - np.clip(x, 0, 1))), t + .03, .05)
    elif kd == 'think':
        place(sfx, shimmer(.8), t, .035)
    elif kd in ('reply', 'msg'):
        x = blip(81 if kd == 'reply' else 76, 86 if kd == 'reply' else 81, .9); place(sfx, x, t, .06, pan=-.15 if kd == 'reply' else .15); place(send, x, t, .05)
    elif kd == 'qualified':
        for j, m in enumerate([78, 81]):
            b = bell(m, 1.4, .6, ratio=4.0, index=.8, decay=2.6); place(sfx, b, t + j * .07, .06); place(send, b, t + j * .07, .08)
    elif kd == 'sent':
        place(sfx, air(.5, 900, 3200, shape=lambda x: np.clip(x, 0, 1) ** .6 * (1 - np.clip(x, 0, 1))), t, .045)
    elif kd == 'tap':
        place(sfx, tick(1.0, 1700), t, .1); place(sfx, thock(.45), t, .05)
    elif kd == 'booked':
        for j, m in enumerate([81, 86]):
            b = bell(m, 1.6, .8, ratio=4.0, index=1.1, decay=2.4); place(sfx, b, t + j * .08, .08, pan=.15); place(send, b, t + j * .08, .1)
    elif kd == 'dawn':
        place(sfx, sub_hit(.6, 2.2, 58, 34), t, .22)
        for j, m in enumerate([62, 69, 74, 78, 81]):
            b = bell(m, 3.0, .6, ratio=4.0, index=.9, decay=1.0); place(sfx, b, t + .05 + j * .09, .06, pan=-.4 + .2 * j); place(send, b, t + .05 + j * .09, .14)
    elif kd == 'check':
        m = [74, 78, 81][c['n']]
        b = bell(m, 1.4, .8, ratio=4.0, index=1.0, decay=2.4); place(sfx, b, t, .08, pan=-.2 + .2 * c['n']); place(send, b, t, .08)
        place(sfx, tick(.5, 2400), t, .04)
    elif kd == 'end':
        place(sfx, sub_hit(.7, 2.4, 62, 32), t, .24)
        for j, m in enumerate([74, 78, 81, 86]):
            b = bell(m, 3.0, .6, ratio=4.0, index=1.0, decay=1.0); place(sfx, b, t + .04 + j * .08, .06, pan=-.3 + .2 * j); place(send, b, t + .04 + j * .08, .14)
    elif kd == 'url':
        place(sfx, tick(.7, 2200), t, .05)

# ---- mix
cut = np.interp(t_all, [0, 2.7, 2.75, 6.3, 12, 14.25, 17.3, 24], [1800, 1800, 600, 800, 900, 900, 2600, 1800])
music = tv_filter(music, cut, 'low', .7)
wet = reverb(send + music * .35, make_ir(2.8, pre=.03), .6)
mix = filt(music + sfx + wet, sos('high', 30))
env = np.abs(mix).max(1)
env = sg.lfilter([1 - np.exp(-1 / (.15 * SR))], [1, -np.exp(-1 / (.15 * SR))], env)
gain = np.minimum(1, (np.maximum(env, 1e-6) / .5) ** (-.22))
mix *= np.where(env > .5, gain, 1)[:, None]
mix *= (np.clip((DUR - t_all) / 1.2, 0, 1) ** 1.5)[:, None]
mix *= np.minimum(1, t_all / .05)[:, None]
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.05) / np.tanh(1.05) * .89
wavfile.write('score3.wav', SR, (mix * 32767).astype(np.int16))
print(f'score3.wav {DUR:.2f}s cues={len(C["cues"])}')
