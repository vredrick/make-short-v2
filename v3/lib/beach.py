"""BEACH set: a Micronesian atoll shore (sand, lagoon, palms, thatched huts, canoes) plus a trading cutter.
Built at sets.ORIGIN['beach']. Characters face -Y; the sea is at +Y behind them, the camera sits at -Y.
Anchors returned: isl1..isl4, sail1..sail3, hart, boat, ship, shore, cam_hint_*  (empties, like the other sets).
"""
import math, random
import bpy
from mathutils import Vector
import sets
from sets import box, cyl, sph, beam, join, inked, empty, sky, toon_mat

ORIGIN = (1500, 0, 0)
_MAT = {}


def _m(name, rgb, ink=True):
    if name not in _MAT or _MAT[name].name not in bpy.data.materials:
        _MAT[name] = toon_mat('BCH_' + name, rgb, ink=ink)   # ink=False for big flat ground/water (grazing angles go black otherwise)
    return _MAT[name]


def palm(c, nm, loc, h=6.0, lean=0.25, yaw=0.0, seed=1):
    rnd = random.Random(seed); parts = []
    pts = []
    for i in range(9):   # curved trunk
        t = i / 8
        pts.append(Vector((lean * h * t * t * math.cos(yaw), lean * h * t * t * math.sin(yaw), h * t)))
    for i in range(8):
        r = 0.26 - 0.1 * i / 8
        parts.append(beam(c, nm + 'tr', pts[i], pts[i + 1], r, _m('palmbark', (0.55, 0.38, 0.22)), 8))
        parts.append(cyl(c, nm + 'ring', r + 0.03, 0.05, tuple(pts[i] + Vector((0, 0, 0.3))), _m('palmring', (0.42, 0.28, 0.16)), seg=8))
    top = pts[-1]
    trunk = join(parts, nm + '_trunk'); inked(trunk, 0.02)
    fr = []
    for k in range(9):   # fronds: drooping flattened leaf blobs
        a = k / 9 * 6.283 + rnd.uniform(-0.2, 0.2)
        for j in range(4):
            d = 0.5 + j * 0.62; z = -0.15 * j * j * 0.5
            fr.append(sph(c, nm + 'fr', 0.55 - 0.08 * j, (top.x + d * math.cos(a), top.y + d * math.sin(a), top.z + z), _m('frond', (0.25, 0.62, 0.22)), (1.3, 0.45, 0.12), 8))
    for k in range(4):
        a = k * 1.57
        fr.append(sph(c, nm + 'nut', 0.17, (top.x + 0.22 * math.cos(a), top.y + 0.22 * math.sin(a), top.z - 0.25), _m('coconut', (0.42, 0.3, 0.12)), (1, 1, 1), 8))
    leaves = join(fr, nm + '_fronds'); inked(leaves, 0.025)
    leaves.parent = trunk
    trunk.location = loc
    return trunk


def hut(c, nm, loc, rot_z=0.0, s=1.0):
    ox, oy, oz = loc; parts = []
    for dx in (-1, 1):
        for dy in (-1, 1):
            parts.append(cyl(c, nm + 'post', 0.08 * s, 1.6 * s, (ox + dx * 1.2 * s, oy + dy * 1.0 * s, oz + 0.8 * s), _m('post', (0.45, 0.3, 0.16)), seg=6))
    parts.append(box(c, nm + 'floor', (2.8 * s, 2.4 * s, 0.15 * s), (ox, oy, oz + 0.35 * s), _m('mat', (0.82, 0.68, 0.42))))
    body = join(parts, nm + '_frame'); inked(body, 0.02)
    roof = cyl(c, nm + '_roof', 2.0 * s, 1.6 * s, (ox, oy, oz + 2.4 * s), _m('thatch', (0.86, 0.68, 0.34)), seg=4, r2=0.05)
    roof.rotation_euler = (0, 0, math.pi / 4 + rot_z); roof.scale = (1.15, 0.95, 1); inked(roof, 0.03)
    return body


def canoe(c, nm, loc, rot_z=0.0, s=1.0):
    ox, oy, oz = loc
    hull = sph(c, nm + '_hull', 1.0, (ox, oy, oz + 0.12 * s), _m('canoe', (0.5, 0.26, 0.12)), (2.2 * s, 0.32 * s, 0.22 * s), 14)
    out = sph(c, nm + '_float', 1.0, (ox, oy + 0.95 * s, oz + 0.08 * s), _m('canoe', (0.5, 0.26, 0.12)), (1.4 * s, 0.12 * s, 0.1 * s), 10)
    arms = [beam(c, nm + 'arm', (ox + dx * s, oy, oz + 0.28 * s), (ox + dx * s, oy + 0.95 * s, oz + 0.16 * s), 0.035 * s, _m('post', (0.45, 0.3, 0.16)), 6) for dx in (-0.6, 0.6)]
    o = join([hull, out] + arms, nm); inked(o, 0.02)
    o.rotation_euler = (0, 0, rot_z)
    return o


def ship(c, nm, loc):
    """single-mast trading cutter, ~9 m long, bow toward +X."""
    ox, oy, oz = loc; P = lambda x, y, z: (ox + x, oy + y, oz + z)
    wood, dark, sail, red = _m('hull', (0.36, 0.2, 0.1)), _m('hulld', (0.18, 0.1, 0.06)), _m('sail', (0.96, 0.92, 0.8)), _m('pennant', (0.8, 0.12, 0.1))
    hull = sph(c, nm + '_hull', 1.0, P(0, 0, 0.3), wood, (4.6, 1.3, 1.1), 20)
    stripe = sph(c, nm + '_stripe', 1.0, P(0, 0, 0.55), dark, (4.65, 1.32, 0.22), 20)
    deck = box(c, nm + '_deck', (8.2, 2.2, 0.15), P(0, 0, 1.15), _m('deck', (0.7, 0.52, 0.3)))
    cabin = box(c, nm + '_cabin', (1.8, 1.4, 0.7), P(-2.4, 0, 1.55), wood)
    mast = cyl(c, nm + '_mast', 0.12, 9.0, P(0.6, 0, 5.6), dark, seg=8)
    boom = beam(c, nm + '_boom', P(0.6, 0, 2.4), P(-3.6, 0, 2.6), 0.07, dark, 6)
    main = box(c, nm + '_main', (4.0, 0.06, 6.2), P(-1.4, 0, 5.6), sail); main.rotation_euler = (0, math.radians(-4), 0)
    jib_v = [P(0.7, 0, 9.6), P(4.8, 0, 1.4), P(0.8, 0, 1.6)]
    me = bpy.data.meshes.new(nm + '_jib'); me.from_pydata([Vector(v) - Vector(P(0, 0, 0)) for v in jib_v], [], [(0, 1, 2)])
    jib = bpy.data.objects.new(nm + '_jib', me); c.objects.link(jib); jib.location = P(0, 0, 0); jib.data.materials.append(sail)
    bowsprit = beam(c, nm + '_bow', P(4.0, 0, 1.3), P(5.6, 0, 1.6), 0.06, dark, 6)
    flag = box(c, nm + '_flag', (0.9, 0.03, 0.4), P(1.05, 0, 10.0), red)
    o = join([hull, stripe, deck, cabin, mast, boom, main, bowsprit, flag], nm)
    inked(o, 0.035); inked(jib, 0.03); jib.parent = o; jib.location = (0, 0, 0)
    return o


def build_beach(c):
    o = ORIGIN; ox, oy, oz = o; P = lambda x, y, z=0: (ox + x, oy + y, oz + z)
    A = {}
    sand, sand_w, sea, lagoon, foam = _m('sand', (0.98, 0.86, 0.6), False), _m('sandwet', (0.86, 0.72, 0.5), False), _m('sea', (0.1, 0.5, 0.8), False), _m('lagoon', (0.25, 0.8, 0.84), False), _m('foam', (1, 1, 1), False)
    box(c, 'ground_sand', (160, 40, 0.4), P(0, -14, -0.2), sand)
    box(c, 'ground_wet', (160, 3.0, 0.4), P(0, 6.4, -0.24), sand_w)
    box(c, 'lagoon_shallow', (160, 14, 0.2), P(0, 14.5, -0.32), lagoon)
    box(c, 'sea_deep', (400, 300, 0.2), P(0, 170, -0.36), sea)
    rnd = random.Random(11)
    for i in range(26):
        box(c, 'ripple', (rnd.uniform(1.2, 3.5), 0.08, 0.01), P(rnd.uniform(-18, 18), rnd.uniform(8.2, 40), -0.2), foam)
    for i in range(18):
        box(c, 'foamline', (rnd.uniform(1.5, 4), 0.22, 0.02), P(-24 + i * 2.8, 7.95 + rnd.uniform(-0.15, 0.15), -0.12), foam)
    sky(c, o)
    for i in range(5):   # distant islets of the atoll ring on the horizon
        x = -70 + i * 34 + rnd.uniform(-5, 5)
        sph(c, 'hill_islet', 1.0, P(x, 120 + rnd.uniform(-8, 8), -0.6), _m('islet', (0.3, 0.55, 0.32)), (rnd.uniform(9, 16), 3, 2.2), 14)
    for i, (x, y, h, ln, yaw) in enumerate(((-7.5, 1.5, 7.0, 0.22, 0.4), (-10.5, -2.5, 6.0, 0.3, 2.6), (8.5, 2.0, 6.6, 0.26, 2.9), (11.5, -3.0, 7.4, 0.2, 0.2),
                                             (-15, 3.5, 6.2, 0.25, 1.2), (16, 1.0, 6.0, 0.3, 3.4), (-4.5, -9, 6.8, 0.18, 1.9), (5, -10, 6.3, 0.22, 2.2),
                                             (-5.8, 3.0, 6.4, 0.24, 2.8), (4.0, 5.0, 6.8, 0.22, 0.3), (6.2, 1.6, 5.8, 0.28, 0.1), (-3.6, 5.6, 7.2, 0.2, 2.2))):
        palm(c, f'palm{i}', P(x, y), h, ln, yaw, seed=i)
    hut(c, 'hut0', P(-9.0, -6.5), 0.2, 1.1); hut(c, 'hut1', P(9.5, -7.5), -0.3, 1.0); hut(c, 'hut2', P(-14, -9), 0.5, 0.9)
    canoe(c, 'canoe0', P(-5.2, 4.6), 0.3); canoe(c, 'canoe1', P(-3.0, 5.4), -0.15, 0.9)
    for i in range(7):   # shells and rocks on the sand
        sph(c, 'rock', rnd.uniform(0.12, 0.3), P(rnd.uniform(-10, 10), rnd.uniform(-2.5, 5), 0.02), _m('stone', (0.5, 0.46, 0.42)), (1, 0.8, 0.6), 8, 0.2, i)
    shp = ship(c, 'cutter', P(9.0, 34.0, -0.1)); A['ship_obj'] = shp
    lb = sph(c, 'longboat', 1.0, P(4.2, 5.8, 0.15), _m('hull', (0.36, 0.2, 0.1)), (1.7, 0.6, 0.35), 14); inked(lb, 0.02); A['longboat_obj'] = lb
    # anchors (rot_z: 0 faces the camera at -Y)
    for k, (x, y, r) in dict(isl1=(-2.6, 0.0, -0.5), isl2=(-3.6, 0.9, -0.35), isl3=(-1.8, 1.2, -0.6), isl4=(-4.4, -0.4, -0.3),
                             hart=(1.6, 0.4, 0.5), sail1=(2.6, 1.2, 0.4), sail2=(3.3, 0.0, 0.55), sail3=(2.2, 2.1, 0.3)).items():
        A[k] = empty(c, k, P(x, y), r)
    A['boat'] = empty(c, 'boat', P(4.2, 5.8)); A['ship'] = empty(c, 'ship', P(9.0, 34.0)); A['shore'] = empty(c, 'shore', P(0, 6.5))
    A['cam_hint_wide'] = empty(c, 'cam_hint_wide', P(0, -12, 3.0), 0, P(0, 4, 1.5))
    return A
