#!/usr/bin/env python3
"""Test suite for cable_gland.scad.

Renders the model in many configurations with OpenSCAD and checks the
results: geometry validity, part counts, parts sitting on the bed, no
support-needing overhangs, thread and key fits (with negative controls that
prove the probes can detect a collision), hole taper direction, auto sizing,
and that warnings fire when they should and only then.

Usage:
    python tests/run_tests.py            # nightly OpenSCAD from tools/
    python tests/run_tests.py --legacy   # also render with installed 2021.01
    OPENSCAD=/path/to/openscad.com python tests/run_tests.py
"""
import glob
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(ROOT, "cable_gland.scad")
PROBE = os.path.join(ROOT, "tests", "probe.scad")
LEGACY = r"C:\Program Files\OpenSCAD\openscad.com"


def find_openscad():
    if os.environ.get("OPENSCAD"):
        return os.environ["OPENSCAD"]
    hits = sorted(glob.glob(os.path.join(ROOT, "tools", "*", "openscad.com"))
                  + glob.glob(os.path.join(ROOT, "tools", "*", "openscad")))
    if not hits:
        sys.exit("No OpenSCAD found in tools/ (set OPENSCAD=...)")
    return hits[-1]


OPENSCAD = find_openscad()
TMP = tempfile.mkdtemp(prefix="gland_tests_")


# ---------------------------------------------------------------- running --

class Render:
    def __init__(self, out, stl, seconds):
        self.out = out
        self.seconds = seconds
        self.empty = "top level object is empty" in out
        self.error = bool(re.search(r"\bERROR\b", out)) or ("Status:" in out and "NoError" not in out)
        self.warnings = re.findall(r'ECHO: "WARNING: ([^"]*)"', out)
        m = re.search(r'ECHO: "SUMMARY\|([^"]*)"', out)
        self.summary = {}
        if m:
            for kv in m.group(1).split("|"):
                k, v = kv.split("=")
                self.summary[k] = float(v)
        self.tris = read_stl(stl) if (stl and not self.empty and os.path.exists(stl)) else []


def run(scad, defines, exe=None, want_stl=True):
    fd, stl = tempfile.mkstemp(suffix=".stl", dir=TMP)
    os.close(fd)
    os.remove(stl)
    args = [exe or OPENSCAD, "--backend=manifold", "--export-format", "binstl", "-o", stl]
    if exe:  # legacy build has no manifold backend / export-format
        args = [exe, "-o", stl]
    for k, v in defines.items():
        if isinstance(v, bool):
            v = "true" if v else "false"
        elif isinstance(v, str):
            v = '"%s"' % v
        args += ["-D", "%s=%s" % (k, v)]
    args.append(scad)
    t = time.time()
    p = subprocess.run(args, capture_output=True, text=True, timeout=900)
    r = Render(p.stdout + p.stderr, stl, time.time() - t)
    if p.returncode != 0 and not r.empty:
        r.error = True
    return r


def model(**d):
    d.setdefault("show_notes", False)
    d.setdefault("part", "body")
    return run(MODEL, d)


def probe(name, **d):
    d["probe"] = name
    return run(PROBE, d)


# ----------------------------------------------------------- STL analysis --

def read_stl(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        tris = []
        for f in re.finditer(rb"facet normal\s+(\S+)\s+(\S+)\s+(\S+).*?vertex\s+(\S+)\s+(\S+)\s+(\S+)\s+vertex\s+(\S+)\s+(\S+)\s+(\S+)\s+vertex\s+(\S+)\s+(\S+)\s+(\S+)", data, re.S):
            v = list(map(float, f.groups()))
            tris.append((tuple(v[0:3]), tuple(v[3:6]), tuple(v[6:9]), tuple(v[9:12])))
        return tris
    n = struct.unpack("<I", data[80:84])[0]
    tris = []
    for i in range(n):
        vals = struct.unpack("<12f", data[84 + 50 * i: 84 + 50 * i + 48])
        tris.append((vals[0:3], vals[3:6], vals[6:9], vals[9:12]))
    return tris


def components(tris):
    """Split a triangle soup into connected parts (shared vertices)."""
    parent = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def key(v):
        return (round(v[0], 3), round(v[1], 3), round(v[2], 3))

    for t in tris:
        ks = [key(v) for v in t[1:]]
        for k in ks:
            parent.setdefault(k, k)
        for k in ks[1:]:
            ra, rb = find(ks[0]), find(k)
            if ra != rb:
                parent[ra] = rb
    groups = {}
    for t in tris:
        groups.setdefault(find(key(t[1])), []).append(t)
    return list(groups.values())


def normal(t):
    a, b, c = t[1], t[2], t[3]
    u = [b[i] - a[i] for i in range(3)]
    w = [c[i] - a[i] for i in range(3)]
    n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
    l = sum(x * x for x in n) ** 0.5
    return [x / l for x in n] if l > 0 else [0, 0, 0], l / 2


def volume(tris):
    v = 0.0
    for t in tris:
        a, b, c = t[1], t[2], t[3]
        v += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
              + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return v


def overhang_area(tris, max_nz=-0.9, z_min=0.05):
    """Area of near-horizontal downward faces that are above the bed (= need support / bridging)."""
    area = 0.0
    for t in tris:
        n, a = normal(t)
        if n[2] < max_nz and max(t[1][2], t[2][2], t[3][2]) > z_min:
            area += a
    return area


# ------------------------------------------------------------------ tests --

TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


LAYOUTS = [
    ("default 1 cable", {}),
    ("2 cables radial", dict(cable_count=2, thread_d=0)),
    ("3 mixed radial", dict(cable_count=3, cable_2_d=6, thread_d=0)),
    ("3 inline", dict(cable_count=3, cable_layout="inline", thread_d=0)),
    ("5 inline mixed", dict(cable_count=5, cable_layout="inline", cable_1_d=2, cable_5_d=7, thread_d=0)),
    ("8 radial hex", dict(cable_count=8, cable_3_d=2.5, thread_d=0, flange_shape="hex")),
    ("straight keys", dict(cable_count=3, thread_d=0, key_style="straight")),
    ("no keys", dict(key_style="none")),
    ("no gap/taper", dict(split_gap=0, hole_taper=False)),
    ("thread taper", dict(thread_taper=0.2, split_gap=0.25)),
    ("coarse pitch long", dict(thread_d=13, thread_pitch=3, thread_length=25, nut_height=10)),
    ("ISO 60 profile", dict(thread_angle=60, thread_pitch=2)),
    ("big cable", dict(cable_1_d=12, thread_d=0)),
]


def segs_expected(d):
    n = d.get("cable_count", 1)
    return 2 if (n == 1 or d.get("cable_layout") == "inline") else n


def make_layout_test(name, d):
    def t():
        r = model(part="all", **d)
        check(not r.error, "render error:\n" + r.out[-800:])
        check(r.summary, "no SUMMARY line")
        check(not r.warnings, "unexpected warnings: %s" % r.warnings)
        nseg = segs_expected(d)
        check(r.summary["n_seg"] == nseg, "n_seg %s != %s" % (r.summary["n_seg"], nseg))
        want_keys = 0 if d.get("key_style") == "none" else 1
        check(r.summary["keys"] == want_keys, "keys=%s, expected %s" % (r.summary["keys"], want_keys))
        comps = components(r.tris)
        check(len(comps) == nseg + 1, "%d separate parts, expected %d segments + nut" % (len(comps), nseg))
        for c in comps:
            zmin = min(min(v[2] for v in t[1:]) for t in c)
            check(abs(zmin) < 1e-3, "a part floats at z=%.3f" % zmin)
            check(volume(c) > 0, "a part has non-positive volume (inside-out mesh)")
        oh = overhang_area(r.tris)
        check(oh < 0.5, "%.2f mm^2 of flat downward faces above the bed (needs support)" % oh)
        return "%d segs, keys=%d, flange %g, M%g, %.1fs" % (
            nseg, r.summary["keys"], r.summary["flange_d"], r.summary["thread_d"], r.seconds)
    t.__name__ = "layout: " + name
    return t


for _n, _d in LAYOUTS:
    TESTS.append(make_layout_test(_n, _d))


@test
def printability_checks_detect_problems():
    # negative control for the layout tests: the assembled view has a nut
    # hanging in the air and a panel above the bed, which must be flagged
    r = model(part="assembly")
    oh = overhang_area(r.tris)
    floating = [c for c in components(r.tris) if abs(min(min(v[2] for v in t[1:]) for t in c)) > 1e-3]
    check(oh > 10, "overhang check missed the floating nut/panel (%.1f mm^2)" % oh)
    check(floating, "off-the-bed check missed the assembly parts")
    return "flags %.0f mm^2 overhang, %d parts off the bed in assembly view" % (oh, len(floating))


@test
def other_parts_render():
    out = []
    for part in ("body", "nut", "assembly"):
        r = model(part=part, cable_count=3, thread_d=0)
        check(not r.error and r.tris, "%s failed to render" % part)
        out.append("%s %d tris" % (part, len(r.tris)))
    return ", ".join(out)


@test
def nut_threads_onto_body():
    # aligned nut positions are z = flange_t + 1 + k * pitch (thread phase)
    res = []
    for cfg in (dict(), dict(thread_pitch=3, thread_d=16, cable_count=3), dict(thread_angle=60, thread_pitch=2),
                dict(thread_taper=0.2, split_gap=0.25)):
        p = cfg.get("thread_pitch", 2.5)
        for k in (0, 2):
            r = probe("nut_on_body", nut_z=3 + 1 + k * p, nut_rot=0, **cfg)
            check(not r.error, r.out[-500:])
            check(r.empty, "nut collides with body thread at turn %d (%s)" % (k, cfg))
        res.append("ok %s" % (cfg or "default"))
    # negative control: half a turn out of phase must collide
    r = probe("nut_on_body", nut_z=3 + 1, nut_rot=180)
    check(not r.empty, "probe insensitive: out-of-phase nut did not collide")
    return "; ".join(res) + "; control collides"


@test
def keys_fit_slots_when_clamped():
    res = []
    for cfg in (dict(), dict(cable_count=3, thread_d=0), dict(cable_count=8, thread_d=0),
                dict(key_style="straight", cable_count=3, thread_d=0)):
        r0 = model(**cfg)
        n = int(r0.summary["n_seg"])
        check(r0.summary["keys"] == 1, "keys missing for %s" % cfg)
        for a in range(n):
            r = probe("pair", seg_a=a, seg_b=(a + 1) % n, split_gap=0.01, **cfg)
            check(r.empty, "segments %d/%d overlap (%s)" % (a, (a + 1) % n, cfg))
        res.append("%d joints" % n)
    r = probe("pair", seg_a=0, seg_b=1, split_gap=0.01, key_clearance=-0.1)
    check(not r.empty, "probe insensitive: oversized key did not collide")
    return ", ".join(res) + "; control collides"


@test
def keys_are_real_geometry():
    r = probe("key_outside_wedge", seg_a=0)
    check(not r.empty, "segment 0 has nothing outside its wedge: key missing")
    r = probe("key_outside_wedge", seg_a=0, key_style="none")
    check(r.empty, "with key_style=none something still sticks out of the wedge")
    return "tab present / absent as configured"


@test
def keys_lock_and_slide():
    # halves split on the x axis; segment 1 is the y<0 half
    pull = dict(seg_a=0, seg_b=1, split_gap=0.01, dx=0, dz=0)
    for style in ("arc", "dovetail"):
        for loc in ("both", "shank", "flange"):
            for dy in (-0.5, -0.9, -1.5):
                r = probe("pair_moved", key_style=style, key_location=loc, dy=dy, **pull)
                check(not r.empty, "%s/%s: pulling halves %.1f mm apart did not collide" % (style, loc, -dy))
            r = probe("pair_moved", key_style=style, key_location=loc, seg_a=0, seg_b=1,
                      split_gap=0.01, dx=0, dy=0, dz=5)
            check(r.empty, "%s/%s: sliding along the cable axis collided (cannot assemble)" % (style, loc))
    r = probe("pair_moved", key_style="straight", dy=-1.5, **pull)
    check(r.empty, "straight key: pulling apart collided (should separate freely)")
    # arc keys must still let the nut close the split gap: no collision at the printed gap
    for cfg in (dict(), dict(cable_count=3, thread_d=0)):
        n = int(model(**cfg).summary["n_seg"])
        for a in range(n):
            r = probe("pair", seg_a=a, seg_b=(a + 1) % n, split_gap=0.3, **cfg)
            check(r.empty, "arc keys collide at the printed (unclamped) gap, segs %d/%d %s" % (a, (a + 1) % n, cfg))
    return "arc and dovetail lock at 0.5-1.5 mm pull, slide along axis, allow the gap to close; straight separates"


@test
def shank_keys_full_height():
    r = model()
    check(r.summary["shank_keys"] == 2 and r.summary["flange_keys"] == 2,
          "default: expected 2 shank + 2 flange keys, got %s" % r.summary)
    depth = r.summary["shank_key_len"]
    check(depth >= 4 - 1e-6, "default arc key reaches only %.2f mm" % depth)
    # segment 0 (y > 0 half) carries the tab on the 180 deg face; look near the top of the thread
    top = dict(bx=-6, sx=12, by=-3, sy=6, bz=3 + 12 - 1.5, sz=1)
    r = probe("key_box", seg_a=0, **top)
    check(not r.empty, "no key tab near the top of the threaded part")
    r = probe("key_box", seg_a=0, key_location="flange", **top)
    check(r.empty, "control: key_location=flange still has a key up the shank")
    # the shank dovetail alone locks the halves and still slides along the axis
    # shank only: no flange keys, so the auto flange shrinks back to the rim size
    s = model(key_location="shank").summary
    f = model(key_location="flange").summary
    check(s["flange_keys"] == 0 and s["shank_keys"] == 2, "shank only: %s" % s)
    check(f["shank_keys"] == 0 and f["flange_keys"] == 2, "flange only: %s" % f)
    # auto thread leaves room for a usable shank key in every layout
    res = []
    for cfg in (dict(cable_count=3, thread_d=0), dict(cable_count=8, thread_d=0),
                dict(cable_count=3, cable_layout="inline", thread_d=0), dict(cable_count=2, thread_d=0)):
        m = model(**cfg).summary
        check(m["shank_keys"] == m["n_seg"] and m["shank_key_w"] >= 1.2 - 1e-6,
              "auto thread: shank keys %s, width %s for %s" % (m["shank_keys"], m["shank_key_w"], cfg))
        res.append("%gmm" % round(m["shank_key_w"], 2))
    return "full height, %.1f mm deep; auto threads fit keys " % depth + ", ".join(res)


@test
def shank_key_walls():
    # default M13 x 2.5 (auto), one 4 mm cable: hole r 2.15, root r 5.65.
    # Rings just inside key_wall on either side of the key slot must be
    # solid plastic apart from the two split gaps.
    import math
    base = dict(thread_d=0, split_gap=0.2)
    hole_r, root_r = 2.15, 13 / 2 - 0.85
    def filled(r1, r2, **d):
        r = probe("wall_ring", ring_z=8, ring_d=2 * r1, ring_d2=2 * r2, **dict(base, **d))
        want = (math.pi * (r2 ** 2 - r1 ** 2) - 2 * 0.2 * (r2 - r1)) * 0.2
        return volume(r.tris) / want
    check(model(**base).summary["shank_keys"] == 2, "no shank keys in the auto default")
    res = []
    for name, r1, r2 in (("hole side", hole_r + 0.05, hole_r + 0.75), ("thread side", root_r - 0.75, root_r - 0.05)):
        f = filled(r1, r2)
        check(f > 0.99, "%s wall of the key slot is %.0f%% plastic, expected solid" % (name, f * 100))
        f0 = filled(r1, r2, key_wall=0.4)
        check(f0 < 0.97, "control: key_wall=0.4 should cut into the %s ring (%.0f%% plastic)" % (name, f0 * 100))
        res.append("%s solid (%.0f%% with key_wall 0.4)" % (name, f0 * 100))
    return "; ".join(res)


@test
def hole_taper_tight_at_root():
    base = dict(cable_1_d=4, hole_clearance=0.3, hole_squeeze=0.3)
    on = dict(base, hole_taper=True)
    tight, loose = 3.7, 4.3
    flange_z, root_z, tip_z = 1.0, 3.3, 3 + 12 - 0.9   # clear of the 0.6 mm end chamfers
    cases = [
        ("flange", flange_z, tight - 0.1, True), ("flange", flange_z, tight + 0.15, False),
        ("root", root_z, tight - 0.1, True), ("root", root_z, tight + 0.15, False),
        ("tip", tip_z, tight + 0.15, True), ("tip", tip_z, loose + 0.15, False),
    ]
    for where, z, d, expect_empty in cases:
        r = probe("hole_ring", ring_z=z, ring_d=d, **on)
        check(r.empty == expect_empty, "%s: ring d=%.2f at z=%.1f %s material" % (
            where, d, z, "hit" if not r.empty else "missed"))
    # default (taper off): same loose diameter through flange, root and tip
    for z in (flange_z, root_z, tip_z):
        r = probe("hole_ring", ring_z=z, ring_d=loose - 0.1, **base)
        check(r.empty, "default: hole narrower than loose_d at z=%.1f" % z)
        r = probe("hole_ring", ring_z=z, ring_d=loose + 0.15, **base)
        check(not r.empty, "default: hole wider than loose_d at z=%.1f" % z)
    return "taper on: 3.7 mm through flange/root, 4.3 mm at tip; default off: straight 4.3 mm"


@test
def thread_taper_fattest_at_flange():
    r1 = probe("thread_ring", ring_z=3.5, ring_d=12.15, thread_taper=0.4, split_gap=0.4)
    check(not r1.empty, "with taper, thread does not exceed 12.15 mm near the flange")
    r2 = probe("thread_ring", ring_z=3 + 12 - 2.5, ring_d=12.15, thread_taper=0.4, split_gap=0.4)
    check(r2.empty, "with taper, thread exceeds 12.15 mm near the tip")
    r3 = probe("thread_ring", ring_z=3.5, ring_d=12.15)
    check(r3.empty, "without taper, thread exceeds 12.15 mm near the flange")
    return "major dia grows toward flange only when thread_taper > 0"


@test
def auto_sizes_give_keys_and_walls():
    res = []
    for cfg in (dict(thread_d=12), dict(thread_d=20, cable_count=3), dict(thread_d=25),
                dict(thread_d=40), dict(thread_d=0, cable_count=6, cable_4_d=8),
                dict(thread_d=0, cable_count=4, flange_shape="hex"),
                dict(thread_d=0, cable_count=3, key_width=4, key_length=4, key_angle=20)):
        r = model(**cfg)
        check(r.summary["keys"] == 1, "auto flange lost keys for %s" % cfg)
        check(not r.warnings, "warnings for %s: %s" % (cfg, r.warnings))
        if cfg.get("thread_d") == 0:
            check(r.summary["hole_wall"] >= 1.5 - 1e-6, "auto thread wall %.2f" % r.summary["hole_wall"])
        res.append("M%g->%g" % (r.summary["thread_d"], r.summary["flange_d"]))
    return ", ".join(res)


@test
def warnings_fire():
    cases = [
        (dict(cable_count=3, thread_d=13), "thread root"),
        (dict(cable_count=3, thread_d=18, flange_d=20), "keys skipped"),
        (dict(nut_af=14), "Nut wall"),
        (dict(cable_count=4, cable_ring_radius=2, thread_d=0), "holes only"),
        (dict(thread_taper=0.5, split_gap=0.2), "thread_taper"),
        (dict(flange_d=12.5), "barely larger"),
        (dict(thread_pitch=1.2), "engagement"),
        (dict(thread_d=20, nut_af=22), "too small to cover"),
        (dict(thread_d=9.5), "Shank keys skipped at 2 of 2"),
        (dict(thread_d=9.5, key_location="shank"), "Shank keys skipped"),
        (dict(cable_count=3, thread_d=15), "Shank keys skipped at 3 of 3"),
        (dict(thread_d=9.5, key_location="shank", flange_d=14), "no key at all"),
    ]
    for cfg, text in cases:
        r = model(**cfg)
        check(any(text in w for w in r.warnings), "%s: expected '%s', got %s" % (cfg, text, r.warnings))
    # no shank-key warning when they fit, are not wanted, or the thread is auto-sized
    for cfg in (dict(), dict(thread_d=9.5, key_location="flange"), dict(thread_d=9.5, key_style="none"),
                dict(cable_count=3, thread_d=0), dict(cable_count=8, thread_d=0)):
        r = model(**cfg)
        check(not any("Shank keys" in w for w in r.warnings), "%s: unexpected %s" % (cfg, r.warnings))
    # the suggested thread_d really fits the keys
    for cfg in (dict(thread_d=9.5), dict(cable_count=3, thread_d=15)):
        w = [w for w in model(**cfg).warnings if "Shank keys" in w][0]
        d = float(w.split("thread_d >= ")[1].split(" ")[0])
        fixed = model(**dict(cfg, thread_d=d)).summary
        check(fixed["shank_keys"] == fixed["n_seg"], "suggested thread_d %g still lacks shank keys (%s)" % (d, cfg))
    # warnings drawn into the model only when show_notes is on
    a = model(part="nut", nut_af=14, show_notes=False)
    b = model(part="nut", nut_af=14, show_notes=True)
    check(len(components(b.tris)) > len(components(a.tris)), "show_notes did not add warning text")
    return "%d warning cases + in-model text" % len(cases)


@test
def bed_chamfer_optional():
    # split line runs along the x axis; look between the shank key and the flange key
    gap = 0.2
    box = dict(bx=5.6, sx=1.2, by=-(gap / 2 + 0.25), sy=gap + 0.5, bz=0.02, sz=0.08)
    on = dict(bottom_chamfer=0.4)
    check(probe("box", **dict(box, **on)).empty, "bottom_chamfer=0.4: split edges on the bed are not chamfered")
    check(not probe("box", **box).empty, "default: split edges should sit square on the bed")
    # cable hole ends
    tight, loose, top = 3.7, 4.3, 3 + 12
    bed = dict(ring_z=0.05, ring_d=tight + 0.6)
    check(probe("hole_ring", **dict(bed, **on)).empty, "bottom_chamfer=0.4: bed end of the hole not chamfered")
    check(not probe("hole_ring", **bed).empty, "default: bed end of the hole should be square")
    tip = dict(ring_z=top - 0.1, ring_d=loose + 0.4)
    check(probe("hole_ring", **tip).empty, "default: cable exit at the thread tip is not chamfered")
    check(not probe("hole_ring", hole_chamfer=0, **tip).empty, "control: hole_chamfer=0 should leave a sharp exit")
    # default: shank key tab has its full footprint on the first layer
    tab = dict(seg_a=0, bx=-6, sx=12, by=-3, sy=6, sz=0.1)
    first = volume(probe("key_box", bz=0.0, **tab).tris)
    mid = volume(probe("key_box", bz=8.0, **tab).tris)
    check(abs(first - mid) < 0.02 * mid, "default: key tab first layer %.3f vs mid height %.3f mm^3" % (first, mid))
    small = volume(probe("key_box", bz=0.0, **dict(tab, **on)).tris)
    check(small < 0.8 * mid, "control: bottom_chamfer=0.4 should shrink the tab's first layer")
    return ("off by default: keys keep full first layer (%.0f%% with 0.4 chamfer); "
            "0.4 chamfers split edges and hole; cable exit always chamfered" % (100 * small / mid))


@test
def elephants_foot_tolerated():
    # grow the bottom 0.2 mm of one segment by 0.15 mm, as a squished first
    # layer would, and clamp it against its neighbour (keys and slots included)
    res = []
    for cfg in (dict(bottom_chamfer=0.4), dict(cable_count=3, thread_d=0, bottom_chamfer=0.4)):
        n = int(model(**cfg).summary["n_seg"])
        for a in range(n):
            for b in ((a + 1) % n, (a - 1) % n):
                r = probe("foot_pair", seg_a=a, seg_b=b, split_gap=0.01, **cfg)
                check(r.empty, "elephant's foot on segment %d hits segment %d (%s)" % (b, a, cfg))
        res.append("%d segments" % n)
    r = probe("foot_pair", seg_a=0, seg_b=1, split_gap=0.01)
    check(not r.empty, "control: with the default (no bottom_chamfer) the foot should collide")
    return "bottom_chamfer=0.4: " + ", ".join(res) + " close with 0.15 mm foot; default collides"


@test
def thread_overhang_max_45():
    # faces steeper than ~51 deg overhang (nz < -0.78), above the bed
    res = []
    for part in ("body", "nut"):
        good = overhang_area(model(part=part).tris, max_nz=-0.78)
        iso = overhang_area(model(part=part, thread_angle=60, thread_pitch=2).tris, max_nz=-0.78)
        check(good < 1.0, "%s: %.1f mm^2 overhanging more than 45 deg with the 90 deg profile" % (part, good))
        check(iso > 20, "%s: control failed, ISO 60 profile shows only %.1f mm^2 of steep overhang" % (part, iso))
        res.append("%s %.1f vs ISO %.0f mm^2" % (part, good, iso))
    return "; ".join(res)


@test
def thread_profile_depth():
    r = model()
    check(abs(r.summary["depth"] - 0.85) < 1e-6, "90 deg / 2.5 pitch / 0.4 flat depth %.3f != 0.85" % r.summary["depth"])
    r = model(thread_angle=60, thread_pitch=2)
    want = 2 * (1 - 0.4) / (2 * 0.57735)
    check(abs(r.summary["depth"] - want) < 1e-3, "60 deg depth %.3f != %.3f" % (r.summary["depth"], want))
    return "90deg: 0.85 mm, 60deg: %.2f mm" % want


@test
def drill_size_reported():
    res = []
    for cfg in (dict(), dict(thread_d=0, cable_count=3), dict(thread_taper=0.3, split_gap=0.3), dict(thread_d=27)):
        r = model(**cfg)
        s = r.summary
        base = s["thread_d"] + cfg.get("thread_taper", 0)
        check(s["drill"] >= base + 0.3 - 1e-6, "drill %.2f does not clear thread %.2f" % (s["drill"], base))
        check(s["drill"] * 2 == int(s["drill"] * 2), "drill %.2f is not a 0.5 mm size" % s["drill"])
        check(s["drill"] <= s["drill_max"], "drill %.2f larger than flange/nut can cover (%.2f)" % (s["drill"], s["drill_max"]))
        check(re.search(r'ECHO: "Panel hole: drill %g mm' % s["drill"], r.out), "drill line missing from console")
        res.append("M%g->%g" % (s["thread_d"], s["drill"]))
    # drawn beside the model only in auto mode
    fixed = model(part="nut", show_notes=True)
    auto = model(part="nut", show_notes=True, thread_d=0)
    check(len(components(fixed.tris)) == 1, "note drawn although thread_d is fixed and nothing is wrong")
    check(len(components(auto.tris)) > 1, "drill note not drawn with thread_d = 0")
    return ", ".join(res) + "; note shown only for auto"


@test
def nut_label_engraved():
    plain = model(part="nut", label_nut=False)
    lab = model(part="nut")
    check(lab.summary["nut_label"] == 1, "label not enabled for default nut")
    dv = volume(plain.tris) - volume(lab.tris)
    check(dv > 1, "engraving removed only %.2f mm^3" % dv)
    zmax = max(max(v[2] for v in t[1:]) for t in lab.tris)
    check(abs(zmax - 6) < 1e-3, "label sticks out of the nut (top at %.2f)" % zmax)
    return "engraved %.1f mm^3 into the top face" % dv


@test
def default_render_fast():
    r = model()
    check(r.seconds < 15, "default render took %.1fs" % r.seconds)
    return "%.1fs" % r.seconds


def legacy_test():
    if not os.path.exists(LEGACY):
        return "skipped (no %s)" % LEGACY
    r = run(MODEL, dict(cable_count=3, thread_d=0, show_notes=True), exe=LEGACY)
    check(not r.error and r.tris, "2021.01 failed:\n" + r.out[-800:])
    return "renders on 2021.01 in %.0fs" % r.seconds


# ------------------------------------------------------------------- main --

def main():
    if "--legacy" in sys.argv:
        legacy_test.__name__ = "legacy OpenSCAD 2021.01"
        TESTS.append(legacy_test)
    print("OpenSCAD: %s" % OPENSCAD)
    t0 = time.time()

    def go(fn):
        try:
            return fn.__name__, True, fn() or ""
        except AssertionError as e:
            return fn.__name__, False, str(e)
        except Exception as e:  # noqa
            return fn.__name__, False, "%s: %s" % (type(e).__name__, e)

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        results = list(ex.map(go, TESTS))
    fails = 0
    for name, ok, msg in results:
        fails += not ok
        print("%s  %-32s %s" % ("PASS" if ok else "FAIL", name.replace("_", " "), msg))
    print("\n%d/%d passed in %.0fs" % (len(results) - fails, len(results), time.time() - t0))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
