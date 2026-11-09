"""Ngatik bean clips on the BEACH set (standalone integrator, does not touch scene.py / the 60 s example).
blender -b -P beach_scene.py -- gate OUTDIR [shot ids...]        middle frame of every shot (or listed ids)
blender -b -P beach_scene.py -- frames OUTDIR A B                frames A..B-1 as PNG
Shots (30 fps, one timeline, cut into separate clips afterwards):
  b1   0- 90  line 2  sailors on the beach, ship behind (the killers who stayed)
  b2  90-210  line 6  islanders refuse, Hart's crew runs back to the boat
  b3 210-330  line 8  islanders wait on the shore with clubs, the ship comes in
  b4 330-450  line 11 the cutter sails off, two sailors stay behind waving
"""
import bpy, sys, os, math
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + '/lib')
import look, sets, chars, beach

args = sys.argv[sys.argv.index('--') + 1:]
MODE, OUT = args[0], args[1]
SHOTS = [dict(id='b1', f_in=0, f_out=90), dict(id='b2', f_in=90, f_out=210), dict(id='b3', f_in=210, f_out=330), dict(id='b4', f_in=330, f_out=450)]
END = SHOTS[-1]['f_out']

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 0, END
look.setup_render(sc)
if os.environ.get('NATIVE'):
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sets.ensure_textures()
coll = sets.newcoll('set_beach')
A = beach.build_beach(coll)
OX = beach.ORIGIN[0]
comp = look.setup_compositor(sc)
for _ in range(2): look.apply_mood(sc, 'day', 0, END, fill_x=OX)


def W(x, y, z=0.0):   # set-local -> world
    return (OX + x, y, z)


def at(name, dx=0.0, dy=0.0):
    p = A[name].location
    return (p.x + dx, p.y + dy, 0.0)


# ---------------------------------------------------------------- cast
CH = {'hart': chars.make_char('captain', 'Hart'), 's1': chars.make_char('sailor', 'Sail1'), 's2': chars.make_char('sailor2', 'Sail2'),
      'i1': chars.make_char('islander', 'Isl1'), 'i2': chars.make_char('islander2', 'Isl2'), 'i3': chars.make_char('islander', 'Isl3'), 'i4': chars.make_char('islander2', 'Isl4')}
chars.ALIVE_TIMING = '/nonexistent'   # no word-bobs from the example's VO
LAST = {}


def put(k, f, loc, rz=0.0):
    """hard placement: holds the previous spot until f-1, so nobody slides across a cut."""
    c = CH[k]
    if k in LAST and LAST[k][0] < f - 1: c.place(f - 1, LAST[k][1], LAST[k][2])
    c.place(f, tuple(loc), rz); LAST[k] = (f, tuple(loc), rz)


OFF = (-300, 0, 0)
for k, c in CH.items():
    put(k, -5, OFF, 0); c.pose(-5, 'idle'); c.face(-5, 'neutral')


def club(nm):   # a short wooden war club
    o = sets.join([sets.cyl(coll, nm + 'h', 0.035, 0.7, (0, 0, 0), beach._m('post', (0.45, 0.3, 0.16)), seg=8),
                   sets.sph(coll, nm + 'k', 0.11, (0, 0, 0.38), beach._m('club', (0.38, 0.22, 0.1)), (1, 1, 1.3), 10)], nm)
    sets.inked(o, 0.012); o.location = (-300, 0, 0); return o


CLUBS = {k: club('club_' + k) for k in ('i1', 'i2', 'i3', 'i4')}
ship = A['ship_obj']; ship_home = Vector(ship.location)

# ---------------------------------------------------------------- b1 (0-90): the sailors on the beach, cutter at anchor behind
f0 = 0
put('hart', f0, at('hart', -1.0, -0.6), 0.25); CH['hart'].pose(f0, 'idle'); CH['hart'].face(f0, 'smug')
put('s1', f0, at('sail1', -1.8, -0.2), -0.1); CH['s1'].pose(f0, 'idle'); CH['s1'].face(f0, 'smug')
put('s2', f0, at('sail2', -1.2, -1.0), -0.35); CH['s2'].pose(f0, 'idle'); CH['s2'].face(f0, 'determined')
CH['hart'].react(18, 'proud_puff', hold=20); CH['s1'].react(24, 'nod'); CH['s2'].react(30, 'lookaround')
ship.location = ship_home; ship.keyframe_insert('location', frame=0)

# ---------------------------------------------------------------- b2 (90-210): islanders refuse, crew runs back to the boat
f0 = 90
for k, a, rz in (('i1', 'isl1', -0.6), ('i2', 'isl2', -0.45), ('i3', 'isl3', -0.7)):
    put(k, f0, at(a, 0.6, -0.6), rz); CH[k].pose(f0, 'idle'); CH[k].face(f0, 'determined')
put('hart', f0, at('hart', 0.6, -0.8), 0.9); CH['hart'].pose(f0, 'point'); CH['hart'].face(f0, 'smug')
put('s1', f0, at('sail1', 0.2, -1.3), 0.7); CH['s1'].pose(f0, 'idle'); CH['s1'].face(f0, 'neutral')
put('s2', f0, OFF, 0)
CH['i1'].react(100, 'shrug'); CH['i2'].react(104, 'tilt'); CH['i3'].react(108, 'shrug')
CH['i1'].face(118, 'determined'); CH['i1'].react(128, 'jump'); CH['i3'].react(131, 'cheer'); CH['i2'].react(134, 'point_jab')
CH['hart'].react(138, 'shock', hold=6); CH['s1'].react(140, 'shock', hold=4)
CH['hart'].face(140, 'shock'); CH['s1'].face(141, 'shock')
for k, lag in (('hart', 0), ('s1', 3)):   # turn and run for the boat
    put(k, 150 + lag, at('hart' if k == 'hart' else 'sail1', 0.6 if k == 'hart' else 0.2, -0.8 if k == 'hart' else -1.3), math.pi * 0.85)
    CH[k].pose(150 + lag, 'walk', dur=4)
    put(k, 206, at('boat', -0.6 + 0.8 * (k == 's1'), -0.4), math.pi * 0.85)
for k in ('i1', 'i2', 'i3'):
    CH[k].pose(150, 'walk', dur=6)
    put(k, 150, LAST[k][1], -0.4 + math.pi * 0.6)
    put(k, 209, tuple(Vector(LAST[k][1]) + Vector((3.2, 2.4, 0))), -0.4 + math.pi * 0.7)

# ---------------------------------------------------------------- b3 (210-330): islanders on the shore with clubs, the cutter comes in
f0 = 210
put('hart', f0, OFF, 0); put('s1', f0, OFF, 0)
for i, k in enumerate(('i1', 'i2', 'i3', 'i4')):
    x = -2.4 + i * 1.5; y = 3.4 + (0.6 if i % 2 else 0)
    put(k, f0, W(x, y), math.pi + (0.15 if i < 2 else -0.15)); CH[k].pose(f0, 'idle', dur=1); CH[k].face(f0, 'determined')
    cl = CLUBS[k]; cl.location = (0, 0, 0); CH[k].hold(f0, cl)
CH['i2'].react(250, 'lookaround'); CH['i3'].react(262, 'nod'); CH['i1'].react(285, 'lean_in'); CH['i4'].react(290, 'tilt')
ship.location = ship_home + Vector((-26, 24, 0)); ship.keyframe_insert('location', frame=210)
ship.location = ship_home + Vector((-8, -10, 0)); ship.keyframe_insert('location', frame=329)

# ---------------------------------------------------------------- b4 (330-450): the cutter sails off, two sailors stay behind
f0 = 330
for k in ('i1', 'i2', 'i3', 'i4'):
    CH[k].hold(f0, None); put(k, f0, OFF, 0)
put('s1', f0, W(-0.6, 4.2), math.pi * 0.08); CH['s1'].pose(f0, 'idle', dur=1); CH['s1'].face(f0, 'smug')
put('s2', f0, W(0.9, 4.6), -math.pi * 0.08); CH['s2'].pose(f0, 'idle', dur=1); CH['s2'].face(f0, 'neutral')
CH['s1'].react(338, 'cheer'); CH['s2'].react(346, 'cheer'); CH['s1'].react(392, 'proud_puff', hold=12); CH['s2'].react(400, 'nod')
ship.location = ship_home + Vector((-4, -6, 0)); ship.keyframe_insert('location', frame=330)
ship.location = ship_home + Vector((18, 6, 0)); ship.keyframe_insert('location', frame=449)
for fc in chars._fcurves(ship):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'

for c in CH.values():
    if c.layers is not None: c.bake(0, END)

# ---------------------------------------------------------------- camera (cuts are hard: CONSTANT at shot boundaries)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.clip_end = 600; cam.data.clip_start = 0.05; cam.data.sensor_width = 36; cam.data.sensor_fit = 'HORIZONTAL'
cam.data.dof.use_dof = False
CAM = {   # shot: [(frame, pos(local), target(local), lens, roll_deg)]
    'b1': [(0, (1.0, -4.6, 1.0), (1.5, 4.0, 1.25), 27, -2), (89, (1.2, -3.8, 0.95), (1.6, 4.0, 1.3), 29, 1)],
    'b2': [(90, (-0.3, -6.0, 1.15), (-0.3, 2.0, 0.95), 24, 2), (150, (-0.2, -5.6, 1.1), (0.0, 2.0, 0.95), 25, -1), (209, (0.6, -4.6, 1.3), (1.8, 4.0, 0.9), 24, -3)],
    'b3': [(210, (0.0, -1.6, 1.05), (0.0, 14.0, 1.7), 26, 0), (329, (0.0, -0.8, 1.0), (0.3, 14.0, 1.7), 28, 1)],
    'b4': [(330, (0.2, 0.4, 1.05), (2.0, 20.0, 2.0), 26, 2), (449, (0.4, 0.9, 1.0), (3.0, 20.0, 2.0), 27, -1)],
}
for sid, keys in CAM.items():
    for f, p, t, lens, roll in keys:
        pw, tw = Vector(W(*p)), Vector(W(*t))
        q = (tw - pw).to_track_quat('-Z', 'Y'); e = q.to_euler(); e.rotate_axis('Z', math.radians(roll))
        cam.location = pw; cam.rotation_euler = e; cam.data.lens = lens
        cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f); cam.data.keyframe_insert('lens', frame=f)
cuts = [s['f_in'] for s in SHOTS[1:]]
for fc in chars._fcurves(cam) + chars._fcurves(cam.data):
    for kp in fc.keyframe_points:
        kp.interpolation = 'CONSTANT' if int(round(kp.co[0])) + 1 in cuts else 'BEZIER'

# ---------------------------------------------------------------- render
os.makedirs(OUT, exist_ok=True)
if MODE == 'gate':
    ids = args[2:] or [s['id'] for s in SHOTS]
    for s in SHOTS:
        if s['id'] not in ids: continue
        f = (s['f_in'] + s['f_out']) // 2
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f"{s['id']}.png")
        bpy.ops.render.render(write_still=True); print('GATE', s['id'], f)
elif MODE == 'frames':
    a, b = int(args[2]), int(args[3])
    for f in range(a, b):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f"f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
    print('FRAMES', a, b)
elif MODE == 'blend':
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'beach.blend'))
