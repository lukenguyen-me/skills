"""Synthesize a royalty-free music bed and UI sound effects for the app preview.

Everything is generated from oscillators and noise, so the output carries no
third-party licensing risk (App Store guideline: no unlicensed music).
Usage: python3 make_audio.py <out_dir>
"""
import os
import sys
import wave

import numpy as np
import scipy.signal as ss

SR = 48000
rng = np.random.default_rng(7)


def tt(d):
    return np.arange(int(d * SR)) / SR


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, f, order=2):
    return ss.sosfilt(ss.butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return ss.sosfilt(ss.butter(order, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return ss.sosfilt(ss.butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def stereo(x, pan=0.0):
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l, x * r], 1) * np.sqrt(2)


def add(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


def reverb(x, secs=1.8, decay=3.2, mix=0.22):
    n = int(secs * SR)
    env = np.exp(-np.arange(n) / SR * decay)
    ir = np.stack([rng.standard_normal(n) * env, rng.standard_normal(n) * env], 1)
    ir = lp(ir.T, 6000).T
    ir /= np.sqrt((ir ** 2).sum(0))
    wet = np.stack([ss.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix * 1.5


def write(path, x, peak_db=-1.0):
    if x.ndim == 1:
        x = stereo(x)
    fade = min(len(x), int(0.004 * SR))
    x[:fade] *= np.linspace(0, 1, fade)[:, None]
    x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# ---------------------------------------------------------------- instruments

def pluck(f, d=0.35, bright=1.0):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.35 * bright * np.sin(4 * np.pi * f * t) + 0.12 * bright * np.sin(6 * np.pi * f * t)
    return x * np.exp(-t * 14) * np.minimum(1, t / 0.002)


def bell(f, d=1.6):
    t = tt(d)
    parts = [(1, 1.0, 3.0), (2.76, 0.45, 5.0), (5.4, 0.25, 8.0), (8.93, 0.12, 12.0)]
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in parts)
    return x * np.minimum(1, t / 0.001)


def saw_pad(notes, d, attack=0.35, release=0.6, cutoff=1700):
    t = tt(d)
    x = np.zeros_like(t)
    for n in notes:
        for det in (-0.07, 0.0, 0.07):
            x += ss.sawtooth(2 * np.pi * hz(n + det) * t + rng.uniform(0, 6.28))
    x = lp(x, cutoff, 2) / (len(notes) * 3)
    env = np.minimum(1, t / attack) * np.minimum(1, (d - t) / release).clip(0, 1)
    return x * env


def kick():
    t = tt(0.42)
    f = 46 + 120 * np.exp(-t * 32)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.5)
    x += hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * 0.25
    return x


def hat(d=0.05):
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 7500) * np.exp(-t * 90)


def clap():
    t = tt(0.25)
    n = bp(rng.standard_normal(len(t)), 900, 3200)
    env = np.zeros_like(t)
    for o in (0, 0.011, 0.022):
        env += (t >= o) * np.exp(-(t - o).clip(0) * (60 if o < 0.02 else 16))
    return n * env * 0.6


def bass(f, d):
    t = tt(d)
    x = ss.sawtooth(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * t)
    return lp(x, 380, 2) * np.exp(-t * 3) * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.02).clip(0, 1)


# ---------------------------------------------------------------- music bed

def music(total=25.0, bpm=120, end_card=22.0):
    beat = 60 / bpm
    bar = beat * 4
    n = int((total + 2.5) * SR)
    drums = np.zeros((n, 2))
    tonal = np.zeros((n, 2))
    arp = np.zeros((n, 2))

    prog = [  # (pad voicing, bass root)  I - V - vi - IV in C
        ([60, 64, 67, 72], 36),
        ([59, 62, 67, 71], 43),
        ([57, 60, 64, 69], 45),
        ([57, 60, 65, 69], 41),
    ]
    bars = int(end_card / bar)  # 11 full bars before the end card
    drop = end_card - beat * 2   # drums drop out for the riser

    for b in range(bars):
        start = b * bar
        chord, root = prog[b % 4]
        add(tonal, stereo(saw_pad(chord, bar + 0.6)) * 0.55, start)
        for e in range(8):  # eighth-note bass, octave bounce on the last
            at = start + e * beat / 2
            if at >= drop:
                break
            r = root + (12 if e in (3, 7) else 0)
            add(tonal, stereo(bass(hz(r), beat / 2 * 0.95)) * 0.55, at)
        tones = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[3] + 12]
        pattern = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 2, 3, 1, 2]
        for s, idx in enumerate(pattern):  # sixteenth-note pluck arp
            at = start + s * beat / 4
            if at >= end_card:
                break
            add(arp, stereo(pluck(hz(tones[idx]), 0.3), 0.35 if s % 2 else -0.35) * (0.55 if s % 4 == 0 else 0.38), at)

    # drums
    k = kick()
    nb = int(drop / beat)
    for i in range(nb):
        at = i * beat
        add(drums, stereo(k) * 0.95, at)
        add(drums, stereo(hat(), 0.25) * 0.22, at + beat / 2)
        if i >= 4:
            add(drums, stereo(hat(0.025), -0.2) * 0.09, at + beat / 4)
            add(drums, stereo(hat(0.025), 0.2) * 0.09, at + 3 * beat / 4)
        if i % 2 == 1 and i >= 4:
            add(drums, stereo(clap()) * 0.42, at)

    # riser into the end card
    t = tt(end_card - drop)
    sweep = np.sin(2 * np.pi * np.cumsum(220 + 900 * (t / t[-1]) ** 2) / SR) * 0.25
    noise = hp(rng.standard_normal(len(t)), 2500) * 0.5
    riser = (sweep + noise) * (t / t[-1]) ** 2.2
    add(drums, stereo(riser) * 0.5, drop)
    for j in range(4):  # snare roll
        for q in range(2 ** (j + 1)):
            at = drop + j * beat / 2 + q * beat / 2 / 2 ** (j + 1)
            add(drums, stereo(clap()) * (0.12 + 0.07 * j), at)

    # final chord + bells on the end card
    final = [48, 55, 60, 64, 67, 72]
    add(tonal, stereo(saw_pad(final, total - end_card + 2.0, attack=0.02, release=2.2, cutoff=2600)) * 0.9, end_card)
    add(drums, stereo(k) * 1.1, end_card)
    for j, m in enumerate([72, 76, 79, 84]):
        add(arp, stereo(bell(hz(m), 2.5), (-0.4, 0.4, -0.2, 0.2)[j]) * 0.45, end_card + j * 0.07)

    # sidechain pump on everything tonal
    duck = np.ones(n)
    tb = (np.arange(n) / SR) % beat
    on = np.arange(n) / SR < drop
    duck[on] = 1 - 0.55 * np.exp(-tb[on] * 9)
    tonal *= duck[:, None]
    arp *= duck[:, None]

    # ping-pong dotted-eighth delay on the arp
    d = int(beat * 0.75 * SR)
    delayed = np.zeros_like(arp)
    delayed[d:, 1] += arp[:-d, 0] * 0.35
    delayed[2 * d:, 0] += arp[: -2 * d, 1] * 0.25
    arp = arp + delayed

    mix = reverb(tonal * 0.8 + arp * 0.7, mix=0.28) + drums
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    mix = mix[: int(total * SR)]
    fade = int(1.4 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    return mix


# ---------------------------------------------------------------- sound effects

def sfx():
    out = {}
    t = tt(0.06)
    out["tap"] = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 260) * 0.5 + np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 120)

    a, b = pluck(hz(88), 0.4, 0.6), pluck(hz(95), 0.5, 0.6)  # two-note marimba "done"
    x = np.zeros(int(0.6 * SR))
    x[: len(a)] += a
    x[int(0.06 * SR): int(0.06 * SR) + len(b)] += b
    out["check"] = reverb(stereo(x), mix=0.18)

    x = np.zeros((int(2.0 * SR), 2))
    for j, m in enumerate([84, 88, 91, 96]):
        add(x, stereo(bell(hz(m), 1.6), (-0.5, -0.15, 0.15, 0.5)[j]) * 0.7, j * 0.075)
    out["chime"] = reverb(x, mix=0.3)

    x = np.zeros((int(1.1 * SR), 2))
    for _ in range(26):
        at = rng.uniform(0, 0.75)
        f = rng.uniform(2400, 6200)
        tb = tt(0.12)
        add(x, stereo(np.sin(2 * np.pi * f * tb) * np.exp(-tb * 45), rng.uniform(-0.8, 0.8)) * rng.uniform(0.3, 0.8), at)
    out["sparkle"] = reverb(x, mix=0.3)

    d = 0.6
    t = tt(d)
    noise = rng.standard_normal(len(t))
    centre = 350 * (9 ** np.sin(np.pi * t / d) )
    y = np.zeros_like(t)
    blk = 256
    zi = None
    for i in range(0, len(t), blk):  # bandpass that sweeps up and back down
        c = centre[i]
        sos = ss.butter(2, [c * 0.6, min(c * 1.6, SR / 2 - 100)], "band", fs=SR, output="sos")
        if zi is None:
            zi = ss.sosfilt_zi(sos) * 0
        y[i:i + blk], zi = ss.sosfilt(sos, noise[i:i + blk], zi=zi)
    env = np.sin(np.pi * t / d) ** 2
    pan = np.linspace(-0.7, 0.7, len(t))
    out["whoosh"] = np.stack([y * env * np.cos((pan + 1) * np.pi / 4), y * env * np.sin((pan + 1) * np.pi / 4)], 1)

    t = tt(0.04)
    out["tick"] = np.sin(2 * np.pi * 2300 * t) * np.exp(-t * 160) + hp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 400) * 0.3

    t = tt(0.5)
    f = 180 * np.exp(-t * 18) + 70
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    out["stamp"] = reverb(stereo(thump + pluck(hz(79), 0.5) * 0.6 + pluck(hz(86), 0.5) * 0.4), mix=0.2)

    t = tt(0.07)
    out["toggle"] = np.sin(2 * np.pi * (900 + 500 * t / t[-1]) * t) * np.exp(-t * 70) + hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 500) * 0.4

    x = np.zeros((int(1.4 * SR), 2))
    add(x, stereo(bell(hz(86), 1.2), -0.2) * 0.8, 0)
    add(x, stereo(bell(hz(81), 1.2), 0.2) * 0.8, 0.13)
    out["notif"] = reverb(x, mix=0.25)

    t = tt(1.6)
    boom = np.sin(2 * np.pi * np.cumsum(42 + 80 * np.exp(-t * 14)) / SR) * np.exp(-t * 3)
    air = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 6) * 0.35
    out["impact"] = reverb(stereo(boom + air), secs=2.2, mix=0.3)
    return out


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out_dir, exist_ok=True)
    write(os.path.join(out_dir, "music.wav"), music(), peak_db=-1.0)
    for name, x in sfx().items():
        write(os.path.join(out_dir, f"{name}.wav"), x, peak_db=-3.0)
    print("wrote", sorted(os.listdir(out_dir)))
