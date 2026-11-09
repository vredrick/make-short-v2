"""BEACH set: a Micronesian atoll shore (painted sand, lagoon, palms, thatched huts, outrigger canoes, a tortoiseshell
trading cutter and the crew's landing boat). Built at ORIGIN. Characters face -Y; the sea is at +Y behind them, the camera sits at -Y.
Anchors returned: isl1..isl4, sail1..sail3, hart, boat, ship, shore, cam_hint_*  (empties, like the other sets).
Textures: lib/beach_tex.py (generated with system python if missing).
"""
import math, random, os
import bpy, bmesh
from mathutils import Vector
import sets
from sets import box, cyl, sph, beam, join, inked, empty, sky, toon_mat, lathe, rope, barrel, crate, sack, coil, M, TEX

ORIGIN = (1500, 0, 0)
_MAT = {}


def _ensure_tex():
    if not os.path.exists(os.path.join(TEX, 'sand.png')):
        import subprocess
        subprocess.check_call([os.environ.get('PYTHON', 'python3'), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'beach_tex.py')])


def _m(name, rgb, ink=True, tex=None, scale=None):
    """BCH_ material. tex = file in tex/, scale = painted tile scale (smaller = bigger tiles), ink=False for big flat ground/water."""
    if name in _MAT and _MAT[name].name in bpy.data.materials: return _MAT[name]
    m = toon_mat('BCH_' + name, rgb, os.path.join(TEX, tex) if tex else None, ink=ink)
    if scale and m.node_tree:
        for nd in m.node_tree.nodes:
            if nd.bl_idname == 'ShaderNodeMapping' and any(l.to_node.bl_idname == 'ShaderNodeTexImage' for o in nd.outputs for l in o.links):
                nd.inputs['Scale'].default_value = (scale, scale, scale)
    _MAT[name] = m
    return m


def _bake(o):
    """freeze the object's own transform into its mesh (join() keeps the first part's transform), so it can be placed/parented cleanly."""
    from mathutils import Matrix
    o.data.transform(o.matrix_basis); o.matrix_basis = Matrix.Identity(4)
    return o


def _frond(c, nm, base, yaw, length, droop, mat, seed=0):
    """one palm frond: a curved, tapering, slightly folded leaf strip with a sawtooth edge (leaflets)."""
    rnd = random.Random(seed); bm = bmesh.new(); n = 14
    rows = []
    for i in range(n + 1):
        t = i / n
        d = length * t; z = 0.35 * length * t - droop * length * t * t
        w = 0.42 * math.sin(math.pi * min(1.0, t * 1.15)) * (1.0 if i % 2 == 0 else 0.72) + 0.03   # sawtooth = leaflets
        ca, sa = math.cos(yaw), math.sin(yaw)
        cx, cy = base[0] + d * ca, base[1] + d * sa
        px, py = -sa * w, ca * w
        fold = 0.12 * w
        rows.append([bm.verts.new((cx + px, cy + py, base[2] + z - fold)), bm.verts.new((cx, cy, base[2] + z + 0.02)), bm.verts.new((cx - px, cy - py, base[2] + z - fold))])
    for i in range(n):
        for k in range(2):
            bm.faces.new((rows[i][k], rows[i][k + 1], rows[i + 1][k + 1], rows[i + 1][k]))
    o = sets._obj(nm, bm, mat, c, uv=True, tile=0.6)
    for p in o.data.polygons: p.use_smooth = True
    return o


def palm(c, nm, loc, h=6.0, lean=0.25, yaw=0.0, seed=1):
    rnd = random.Random(seed); parts = []
    pts = []
    for i in range(11):   # curved trunk
        t = i / 10
        pts.append(Vector((lean * h * t * t * math.cos(yaw), lean * h * t * t * math.sin(yaw), h * t)))
    bark = _m('palmbark', (1, 1, 1), tex='palm.png', scale=1.2)
    for i in range(10):
        r = 0.24 - 0.09 * i / 10
        parts.append(beam(c, nm + 'tr', pts[i], pts[i + 1], r, bark, 10))
        parts.append(cyl(c, nm + 'ring', r + 0.025, 0.06, tuple(pts[i] + Vector((0, 0, 0.12))), _m('palmring', (0.5, 0.36, 0.22)), seg=10))
    parts.append(lathe(c, nm + 'foot', [(0.0, 0), (0.42, 0), (0.3, 0.12), (0.24, 0.4)], bark, (0, 0, 0), seg=10))
    top = pts[-1]
    trunk = _bake(join(parts, nm + '_trunk')); inked(trunk, 0.02)
    fm = [_m('frond', (1, 1, 1), tex='frond.png', scale=2.0), _m('frond_d', (0.72, 0.85, 0.7), tex='frond.png', scale=2.0)]
    fr = []
    nf = 11
    for k in range(nf):
        a = k / nf * 6.283 + rnd.uniform(-0.25, 0.25)
        fr.append(_frond(c, nm + 'fr', (top.x, top.y, top.z - 0.05), a, rnd.uniform(2.3, 3.1), rnd.uniform(0.75, 1.05), fm[k % 2], seed + k))
    for k in range(5):
        a = k * 1.26
        fr.append(sph(c, nm + 'nut', 0.16, (top.x + 0.2 * math.cos(a), top.y + 0.2 * math.sin(a), top.z - 0.28), _m('coconut', (0.5, 0.36, 0.14)), (1, 1, 1.1), 10))
    leaves = _bake(join(fr, nm + '_fronds')); inked(leaves, 0.018)
    leaves.parent = trunk
    trunk.location = loc
    return trunk


def hut(c, nm, loc, rot_z=0.0, s=1.0):
    ox, oy, oz = loc; parts = []
    post = _m('post', (0.55, 0.38, 0.22), tex='palm.png', scale=2.5)
    for dx in (-1, 1):
        for dy in (-1, 1):
            parts.append(cyl(c, nm + 'post', 0.08 * s, 1.6 * s, (dx * 1.2 * s, dy * 1.0 * s, 0.8 * s), post, seg=6))
    parts.append(box(c, nm + 'floor', (2.8 * s, 2.4 * s, 0.15 * s), (0, 0, 0.35 * s), _m('mat', (1, 1, 1), tex='thatch.png', scale=1.5)))
    for k in range(5):   # woven wall slats at the back
        parts.append(box(c, nm + 'wall', (2.5 * s, 0.05 * s, 0.18 * s), (0, 1.0 * s, (0.6 + 0.22 * k) * s), _m('weave', (0.86, 0.72, 0.48))))
    body = _bake(join(parts, nm + '_frame')); inked(body, 0.02)
    roof = lathe(c, nm + '_roof', [(0.0, 2.7 * s), (2.05 * s, 1.55 * s), (2.15 * s, 1.45 * s), (0.0, 1.45 * s)], _m('thatch', (1, 1, 1), tex='thatch.png', scale=1.4), (0, 0, 0), seg=4, smooth=False)
    roof.rotation_euler = (0, 0, math.pi / 4); roof.scale = (1.2, 0.95, 1); _bake(roof); roof.parent = body; inked(roof, 0.03)
    body.location = loc; body.rotation_euler = (0, 0, rot_z)
    return body


def canoe(c, nm, loc, rot_z=0.0, s=1.0):
    hullm = _m('canoe', (0.62, 0.34, 0.16), tex='palm.png', scale=1.0)
    hull = lathe(c, nm + '_hull', [(0.0, -2.2), (0.22, -1.6), (0.3, -0.6), (0.3, 0.6), (0.22, 1.6), (0.0, 2.2)], hullm, (0, 0, 0.22 * s), (0, math.pi / 2, 0), seg=12, scale=(s * 0.8, s * 1.0, s))
    inner = box(c, nm + '_in', (3.2 * s, 0.34 * s, 0.05 * s), (0, 0, 0.42 * s), _m('canoe_in', (0.3, 0.16, 0.08)))
    out = lathe(c, nm + '_float', [(0.0, -1.3), (0.1, -0.9), (0.11, 0.9), (0.0, 1.3)], hullm, (0, 0.95 * s, 0.1 * s), (0, math.pi / 2, 0), seg=8, scale=(s, s, s))
    post = _m('post', (0.55, 0.38, 0.22))
    arms = [beam(c, nm + 'arm', (dx * s, 0, 0.42 * s), (dx * s, 0.95 * s, 0.2 * s), 0.035 * s, post, 6) for dx in (-0.7, 0.7)]
    paddle = join([beam(c, nm + 'pad', (-0.6 * s, -0.1 * s, 0.45 * s), (0.6 * s, -0.25 * s, 0.5 * s), 0.025 * s, post, 6),
                   sph(c, nm + 'blade', 0.2 * s, (0.75 * s, -0.27 * s, 0.5 * s), post, (1.4, 0.15, 0.6), 8)], nm + 'paddle')
    o = _bake(join([hull, inner, out, paddle] + arms, nm)); inked(o, 0.02)
    o.location = loc; o.rotation_euler = (0, 0, rot_z)
    return o


def ship(c, nm, loc):
    """single-mast trading cutter, ~9 m long, bow toward +X. Origin at the waterline centre."""
    P = lambda x, y, z: (x, y, z)
    wood = _m('hull', (1, 1, 1), tex='palm.png', scale=0.8); dark = _m('hulld', (0.2, 0.12, 0.07)); sail = _m('sail', (0.97, 0.93, 0.82), tex='thatch.png', scale=0.15)
    red, white, yel = _m('pennant', (0.8, 0.12, 0.1)), _m('hullw', (0.95, 0.92, 0.85)), _m('hully', (0.95, 0.75, 0.2))
    hull = lathe(c, nm + '_hull', [(0.0, -4.6), (0.9, -4.2), (1.3, -2.5), (1.35, 1.0), (1.05, 3.4), (0.0, 4.9)], wood, P(0, 0, 0.55), (0, math.pi / 2, 0), seg=16, scale=(0.85, 1.0, 1.0))
    stripe = lathe(c, nm + '_stripe', [(0.0, -4.62), (0.92, -4.22), (1.32, -2.5), (1.37, 1.0), (1.07, 3.4), (0.0, 4.92)], white, P(0, 0, 0.92), (0, math.pi / 2, 0), seg=16, scale=(0.18, 1.0, 1.0))
    deck = box(c, nm + '_deck', (8.0, 2.1, 0.12), P(-0.1, 0, 1.4), _m('deck', (1, 1, 1), tex='palm.png', scale=1.5))
    rail = [box(c, nm + '_rail', (8.0, 0.08, 0.25), P(-0.1, s * 1.08, 1.6), dark) for s in (-1, 1)]
    cabin = box(c, nm + '_cabin', (1.8, 1.4, 0.75), P(-2.4, 0, 1.85), wood)
    cabin_roof = box(c, nm + '_croof', (2.0, 1.6, 0.1), P(-2.4, 0, 2.27), dark)
    win = [box(c, nm + '_win', (0.3, 0.02, 0.22), P(-2.4 + dx, -0.71, 1.9), yel) for dx in (-0.45, 0.45)]
    mast = cyl(c, nm + '_mast', 0.12, 9.0, P(0.6, 0, 5.9), dark, seg=8)
    boom = beam(c, nm + '_boom', P(0.6, 0, 2.6), P(-3.6, 0, 2.8), 0.07, dark, 6)
    gaff = beam(c, nm + '_gaff', P(0.6, 0, 8.4), P(-3.2, 0, 8.9), 0.06, dark, 6)
    bowsprit = beam(c, nm + '_bow', P(4.2, 0, 1.5), P(6.0, 0, 1.9), 0.06, dark, 6)
    flag = box(c, nm + '_flag', (0.9, 0.03, 0.4), P(1.05, 0, 10.3), red)
    barrels = [barrel(c, nm + '_bar', P(1.6 + 0.85 * i, 0.4 * (-1) ** i, 1.46), 0.7) for i in range(2)]
    hullj = _bake(join([hull, stripe, deck, cabin, cabin_roof, mast, boom, gaff, bowsprit, flag] + rail + win + barrels, nm))
    # sails: a gaff mainsail (quad with belly) and a jib triangle, both cloth-shaded
    def sheet(name, pts, rows=6):
        bm = bmesh.new(); grid = []
        (a, b, cc, d) = [Vector(p) for p in pts]   # foot-aft, foot-fore, head-fore, head-aft
        for j in range(rows + 1):
            v = j / rows; row = []
            for i in range(rows + 1):
                u = i / rows
                p = (a.lerp(b, u)).lerp(d.lerp(cc, u), v)
                p.y += 0.35 * math.sin(math.pi * u) * math.sin(math.pi * min(1, v * 1.1 + 0.1))   # belly
                row.append(bm.verts.new(p))
            grid.append(row)
        for j in range(rows):
            for i in range(rows):
                bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        o = sets._obj(name, bm, sail, c, uv=True, tile=0.6)
        for p in o.data.polygons: p.use_smooth = True
        o.data.materials.append(sail); return inked(o, 0.025)
    main = sheet(nm + '_main', [P(-3.5, 0, 2.85), P(0.5, 0, 2.7), P(0.5, 0, 8.35), P(-3.1, 0, 8.85)])
    jib = sheet(nm + '_jib', [P(0.8, 0, 1.8), P(5.8, 0, 1.95), P(0.75, 0, 9.7), P(0.72, 0, 9.6)], rows=5)
    for s_ in (main, jib): s_.parent = hullj
    stays = [rope(c, nm + '_stay', P(0.6, 0, 10.2), P(6.0, 0, 1.9), 0.0, 0.015, dark), rope(c, nm + '_shr', P(0.6, 0, 9.6), P(0.6, -1.1, 1.6), 0.0, 0.012, dark),
             rope(c, nm + '_shr', P(0.6, 0, 9.6), P(0.6, 1.1, 1.6), 0.0, 0.012, dark), rope(c, nm + '_shr', P(0.6, 0, 9.6), P(-4.2, 0, 1.6), 0.0, 0.012, dark)]
    for s_ in stays:
        if s_: _bake(s_); s_.parent = hullj
    inked(hullj, 0.035)
    hullj.location = loc
    return hullj


def longboat(c, nm, loc, rot_z=0.0):
    wood = _m('hull', (1, 1, 1), tex='palm.png', scale=0.8)
    hull = lathe(c, nm + '_hull', [(0.0, -1.9), (0.5, -1.5), (0.72, -0.4), (0.72, 0.6), (0.5, 1.5), (0.0, 2.0)], wood, (0, 0, 0.32), (0, math.pi / 2, 0), seg=12, scale=(0.55, 1, 1))
    inside = box(c, nm + '_in', (3.0, 0.9, 0.05), (0, 0, 0.62), _m('hulld', (0.2, 0.12, 0.07)))
    seats = [box(c, nm + '_seat', (0.16, 1.0, 0.07), (x, 0, 0.66), _m('deck', (1, 1, 1), tex='palm.png', scale=1.5)) for x in (-0.8, 0.2, 1.0)]
    oars = [beam(c, nm + '_oar', (x, -0.1, 0.72), (x + 0.5, -1.7, 0.2), 0.03, _m('post', (0.55, 0.38, 0.22)), 6) for x in (-0.5, 0.6)]
    o = _bake(join([hull, inside] + seats + oars, nm)); inked(o, 0.02)
    o.location = loc; o.rotation_euler = (0, 0, rot_z)
    return o


def shell_pile(c, nm, loc, n=7, seed=3):
    """stacked hawksbill tortoiseshell plates: the trade good of the story (amber with dark brown mottling)."""
    rnd = random.Random(seed); parts = []
    mats = [_m('tshell', (0.82, 0.52, 0.2)), _m('tshell_d', (0.42, 0.22, 0.08)), _m('tshell_l', (0.95, 0.72, 0.36))]
    for i in range(n):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0, 0.25)
        o = sph(c, nm + 'pl', 0.26, (r * math.cos(a), r * math.sin(a), 0.05 + 0.06 * i), mats[i % 3], (1.1, 0.8, 0.18), 12)
        o.rotation_euler = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), rnd.uniform(0, 3.1)); parts.append(o)
    pile = _bake(join(parts, nm)); inked(pile, 0.012); pile.location = loc
    return pile


def net_rack(c, nm, loc, rot_z=0.0):
    post = _m('post', (0.55, 0.38, 0.22), tex='palm.png', scale=2.5)
    parts = [cyl(c, nm + 'p', 0.06, 1.8, (x, 0, 0.9), post, seg=6) for x in (-1.2, 1.2)]
    parts.append(beam(c, nm + 'bar', (-1.25, 0, 1.75), (1.25, 0, 1.75), 0.04, post, 6))
    frame = _bake(join(parts, nm)); inked(frame, 0.015)
    bm = bmesh.new(); grid = []
    for j in range(7):
        row = []
        for i in range(9):
            u = i / 8; v = j / 6
            row.append(bm.verts.new((-1.15 + 2.3 * u, 0.04 * math.sin(u * 9), 1.72 - 1.4 * v - 0.25 * math.sin(math.pi * u) * v)))
        grid.append(row)
    for j in range(6):
        for i in range(8):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    net = sets._obj(nm + '_net', bm, _m('net', (1, 1, 1), tex='net.png', scale=1.6, ink=False), c, uv=True)
    net.parent = frame
    frame.location = loc; frame.rotation_euler = (0, 0, rot_z)
    return frame


def build_beach(c):
    _ensure_tex()
    o = ORIGIN; ox, oy, oz = o; P = lambda x, y, z=0: (ox + x, oy + y, oz + z)
    A = {}
    sand = _m('sand', (1, 1, 1), False, 'sand.png', 0.18)
    sand_w = _m('sandwet', (1, 1, 1), False, 'sand_wet.png', 0.25)
    lagoon = _m('lagoon', (1, 1, 1), False, 'lagoon.png', 0.12)
    sea = _m('sea', (1, 1, 1), False, 'sea.png', 0.05)
    foam = _m('foam', (1, 1, 1), False)
    box(c, 'ground_sand', (160, 40, 0.4), P(0, -14, -0.2), sand)
    box(c, 'ground_wet', (160, 3.0, 0.4), P(0, 6.4, -0.235), sand_w)
    box(c, 'lagoon_shallow', (160, 22, 0.2), P(0, 18.9, -0.33), lagoon)
    box(c, 'sea_deep', (500, 400, 0.2), P(0, 229.9, -0.37), sea)
    rnd = random.Random(11)
    for i in range(30):   # foam line along the shore (white, wavy), plus a second faint one
        box(c, 'foamline', (rnd.uniform(1.4, 3.6), 0.18, 0.02), P(-30 + i * 2.1, 7.95 + rnd.uniform(-0.15, 0.15), -0.2), foam, (0, 0, rnd.uniform(-0.06, 0.06)))
    for i in range(16):
        box(c, 'reefline', (rnd.uniform(3, 7), 0.35, 0.02), P(-40 + i * 5.3, 29.8 + rnd.uniform(-0.4, 0.4), -0.22), foam)
    sky(c, o)
    for i in range(6):   # the rest of the atoll ring on the horizon: low green islets with palm dots
        x = -90 + i * 36 + rnd.uniform(-6, 6); y = 130 + rnd.uniform(-10, 10)
        sph(c, 'hill_islet', 1.0, P(x, y, -0.6), _m('islet', (0.32, 0.6, 0.34)), (rnd.uniform(10, 18), 3, 2.6), 14)
        box(c, 'islet_sand', (rnd.uniform(22, 34), 6, 0.2), P(x, y - 1.5, -0.3), _m('sand_far', (0.98, 0.9, 0.7), False))
    palms = ((-7.5, 1.5, 7.0, 0.22, 0.4), (-10.5, -2.5, 6.0, 0.3, 2.6), (8.5, 2.0, 6.6, 0.26, 2.9), (11.5, -3.0, 7.4, 0.2, 0.2),
             (-15, 3.5, 6.2, 0.25, 1.2), (16, 1.0, 6.0, 0.3, 3.4), (-4.5, -9, 6.8, 0.18, 1.9), (5, -10, 6.3, 0.22, 2.2),
             (-5.8, 3.0, 6.4, 0.24, 2.8), (4.0, 5.0, 6.8, 0.22, 0.3), (6.2, 1.6, 5.8, 0.28, 0.1), (-3.6, 5.6, 7.2, 0.2, 2.2),
             (-1.2, -6.5, 6.0, 0.3, 1.0), (2.8, -6.8, 6.5, 0.25, 2.0))
    for i, (x, y, h, ln, yaw) in enumerate(palms):
        palm(c, f'palm{i}', P(x, y), h, ln, yaw, seed=i)
    hut(c, 'hut0', P(-8.5, -4.5), 0.2, 1.1); hut(c, 'hut1', P(9.5, -5.5), -0.3, 1.0); hut(c, 'hut2', P(-13, -8), 0.5, 0.9); hut(c, 'hut3', P(-4.6, -7.4), -0.1, 1.0)
    canoe(c, 'canoe0', P(-5.2, 4.6), 0.3); canoe(c, 'canoe1', P(-3.0, 5.4), -0.15, 0.9); canoe(c, 'canoe2', P(-10.0, 5.2), 0.1, 1.0)
    net_rack(c, 'netrack', P(-6.6, 0.6), 0.25)
    A['shells_obj'] = shell_pile(c, 'shells', P(-2.0, -1.6), 9, 4)
    shell_pile(c, 'shells2', P(-6.0, -2.4), 6, 8)
    # the crew's cargo where they landed
    crate(c, 'bcrate', P(5.6, 3.3), (0.8, 0.8, 0.7), (0, 0, 0.3)); crate(c, 'bcrate2', P(6.3, 4.0), (0.7, 0.7, 0.6), (0, 0, -0.2))
    barrel(c, 'bbarrel', P(4.9, 4.2), 0.9); sack(c, 'bsack', P(6.6, 3.2), 1.0, rot_z=0.4); coil(c, 'bcoil', P(5.2, 2.6), 1.0)
    # driftwood, coconuts, rocks, beach grass + shells scatter (the dense painted-ground look of the camp set)
    drift = _m('drift', (0.82, 0.74, 0.62), tex='palm.png', scale=1.4)
    for i, (x, y, a, L) in enumerate(((-3.8, -3.6, 0.3, 2.4), (3.6, -3.0, -0.4, 1.8), (-9, 2.2, 1.2, 2.8), (8.0, -1.0, 0.9, 2.2))):
        inked(beam(c, 'drift', P(x - L / 2 * math.cos(a), y - L / 2 * math.sin(a), 0.12), P(x + L / 2 * math.cos(a), y + L / 2 * math.sin(a), 0.16), 0.13, drift, 8), 0.015)
    for i in range(12):
        sph(c, 'coco', 0.15, P(rnd.uniform(-9, 9), rnd.uniform(-4, 4.5), 0.12), _m('coconut', (0.5, 0.36, 0.14)), (1, 1, 1.1), 8)
    for i in range(6):
        sets.rock(c, 'brock', P(rnd.uniform(-12, 12), rnd.uniform(2.5, 6), 0.05), rnd.uniform(0.2, 0.45), i)
    avoid = [(0.6, 0.4, 1.8), (2.6, 1.0, 1.4), (-2.6, 0.2, 1.8), (-2.0, -1.6, 0.6), (4.2, 5.8, 1.6), (0, 3.8, 3.2)]
    sets._surface_ground(c, o, 'beach', dict(tl=(0.5, 0.72, 0.3), td=(0.34, 0.52, 0.22), peb=(0.98, 0.95, 0.9), flw=(0.98, 0.55, 0.62), patch=(0.92, 0.8, 0.56)),
                         avoid, (-14, 14, -9, 5.2), n_t=260, n_p=90, n_f=22, patches=8, seed=41)
    shp = ship(c, 'cutter', P(9.0, 34.0, -0.3)); A['ship_obj'] = shp
    lb = longboat(c, 'longboat', P(4.2, 5.8, 0.0), 0.5); A['longboat_obj'] = lb
    # anchors (rot_z: 0 faces the camera at -Y)
    for k, (x, y, r) in dict(isl1=(-2.6, 0.0, -0.5), isl2=(-3.6, 0.9, -0.35), isl3=(-1.8, 1.2, -0.6), isl4=(-4.4, -0.4, -0.3),
                             hart=(1.6, 0.4, 0.5), sail1=(2.6, 1.2, 0.4), sail2=(3.3, 0.0, 0.55), sail3=(2.2, 2.1, 0.3)).items():
        A[k] = empty(c, k, P(x, y), r)
    A['boat'] = empty(c, 'boat', P(4.2, 5.8)); A['ship'] = empty(c, 'ship', P(9.0, 34.0)); A['shore'] = empty(c, 'shore', P(0, 6.5))
    A['cam_hint_wide'] = empty(c, 'cam_hint_wide', P(0, -12, 3.0), 0, P(0, 4, 1.5))
    return A
