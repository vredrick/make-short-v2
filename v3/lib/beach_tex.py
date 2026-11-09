"""Painted textures for the BEACH set (same hand as sets._gen_textures). Run with system python (numpy + PIL):
    python3 lib/beach_tex.py      -> tex/sand.png, sand_wet.png, lagoon.png, sea.png, thatch.png, palm.png, frond.png, plank.png, net.png
"""
import os, math
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, '..', 'tex'))
rng = np.random.default_rng(37)
S = 512


def tn(gh, gw, size=S):   # tileable value noise 0..1
    g = rng.random((gh, gw)).astype('float32')
    t = np.tile(g, (3, 3))
    im = Image.fromarray((t * 255).astype('uint8')).resize((3 * size, 3 * size), Image.BICUBIC)
    return np.asarray(im)[size:2 * size, size:2 * size].astype('float32') / 255


def col(c): return np.array(c, 'float32')


def save(name, a, blur=0.0):
    im = Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im.save(os.path.join(TEX, name))


def dab(a, x, y, w, h, c, k=1.0):
    """soft painted blob, wrapped (tileable)"""
    yy, xx = np.mgrid[-h:h + 1, -w:w + 1]
    m = np.clip(1 - (xx / max(w, 1)) ** 2 - (yy / max(h, 1)) ** 2, 0, 1) ** 0.6 * k
    ys = (np.arange(y - h, y + h + 1) % S)[:, None]; xs = (np.arange(x - w, x + w + 1) % S)[None, :]
    a[ys, xs] = a[ys, xs] * (1 - m[..., None]) + col(c) * m[..., None]


def gen():
    os.makedirs(TEX, exist_ok=True)
    yy, xx = np.mgrid[0:S, 0:S].astype('float32')

    # dry sand: warm cream with big soft tone patches, wind ripples, dark/light grains, little shell flecks
    a = col((240, 214, 160))[None, None, :] * (0.86 + 0.22 * tn(8, 8) + 0.08 * tn(30, 30))[..., None]
    rip = np.sin((yy + 18 * tn(4, 4) * S / 64) * 2 * math.pi / 21.333)   # 24 ripples, tile-safe
    a *= (1 + 0.045 * rip * (0.4 + tn(6, 6)))[..., None]
    for _ in range(2600):
        x, y = int(rng.integers(0, S)), int(rng.integers(0, S))
        a[y, x] = a[y, x] * (0.7 if rng.random() < 0.6 else 1.15)
    for _ in range(46):
        dab(a, int(rng.integers(0, S)), int(rng.integers(0, S)), int(rng.integers(2, 5)), int(rng.integers(1, 3)),
            [(255, 246, 232), (238, 196, 186), (250, 232, 200)][int(rng.integers(0, 3))])
    save('sand.png', a, 0.5)

    # wet sand: darker, glossy streaks
    a = col((198, 162, 112))[None, None, :] * (0.84 + 0.26 * tn(10, 10))[..., None]
    a *= (1 + 0.06 * np.sin((xx + 30 * tn(3, 3)) * 2 * math.pi / 64))[..., None]
    for _ in range(60):
        x, y = int(rng.integers(0, S - 80)), int(rng.integers(0, S - 3)); L = int(rng.integers(30, 80))
        a[y:y + 2, x:x + L] = a[y:y + 2, x:x + L] * 0.6 + col((236, 222, 196)) * 0.4
    save('sand_wet.png', a, 0.6)

    # lagoon: turquoise, sun-net caustics + painted white ripple dashes
    n1, n2 = tn(9, 9), tn(22, 22)
    caust = np.abs(np.sin((n1 * 6 + n2 * 3) * math.pi)) ** 6
    a = col((70, 205, 205))[None, None, :] * (0.8 + 0.3 * n1)[..., None]
    a += caust[..., None] * col((70, 50, 30))
    for _ in range(90):
        x, y = int(rng.integers(0, S - 50)), int(rng.integers(0, S - 3)); L = int(rng.integers(14, 46))
        a[y:y + 3, x:x + L] = col((226, 250, 248))
    save('lagoon.png', a, 0.6)

    # deep sea: ultramarine with dashes
    a = col((30, 105, 200))[None, None, :] * (0.78 + 0.4 * tn(8, 8))[..., None]
    for _ in range(120):
        x, y = int(rng.integers(0, S - 60)), int(rng.integers(0, S - 3)); L = int(rng.integers(20, 60))
        a[y:y + 3, x:x + L] = col((176, 220, 250))
    save('sea.png', a, 0.5)

    # thatch: rows of straw strands, overlapping layers, darker under each row
    a = np.zeros((S, S, 3), 'float32') + col((214, 168, 88))
    rows = 8; ph = S // rows
    for r in range(rows):
        y0 = r * ph
        for _ in range(420):
            x = int(rng.integers(0, S)); L = int(rng.integers(ph // 2, ph + 10)); c = col([(232, 190, 104), (196, 146, 70), (240, 206, 126), (170, 120, 58)][int(rng.integers(0, 4))])
            ys = np.arange(y0, y0 + L) % S
            a[ys, x % S] = c; a[ys, (x + 1) % S] = c * 0.92
        a[(np.arange(y0 + ph - 8, y0 + ph) % S)] *= 0.62
    save('thatch.png', a, 0.6)

    # palm trunk: horizontal growth rings, grey-brown with fibres
    a = col((150, 112, 76))[None, None, :] * (0.78 + 0.3 * tn(4, 30))[..., None]
    ring = (yy % 42)
    a = np.where((ring < 5)[..., None], a * 0.55, a)
    a = np.where(((ring >= 5) & (ring < 9))[..., None], a * 1.18, a)
    a *= (0.88 + 0.2 * tn(6, 60))[..., None]
    save('palm.png', a, 0.6)

    # frond: green with a central rib + leaflet stripes
    a = col((80, 168, 64))[None, None, :] * (0.78 + 0.32 * tn(6, 6))[..., None]
    a *= (1 + 0.12 * np.sin(xx * 2 * math.pi / 16))[..., None]
    a = np.where((np.abs(yy - S / 2) < 6)[..., None], a * 0.0 + col((176, 214, 96)), a)
    save('frond.png', a, 0.8)

    # rope net: diamond mesh of brown cord on transparent-ish dark
    a = np.zeros((S, S, 3), 'float32') + col((96, 76, 52))
    m = (np.abs(((xx + yy) % 64) - 32) < 3) | (np.abs(((xx - yy) % 64) - 32) < 3)
    a = np.where(m[..., None], col((200, 168, 112)), a)
    save('net.png', a, 0.5)


if __name__ == '__main__':
    gen(); print('beach textures ok', TEX)
