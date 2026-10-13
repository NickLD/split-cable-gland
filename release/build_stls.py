"""Export the ready-made STL set for sites without a Customizer (Printables).
Each file is a full print plate (split body + nut) with notes off; any config
that raises a model warning is rejected."""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
OPENSCAD = next(os.path.join(TOOLS, d, "openscad.com") for d in sorted(os.listdir(TOOLS))
                if os.path.exists(os.path.join(TOOLS, d, "openscad.com")))

def cfg(cables, layout="radial"):
    d = {"cable_count": len(cables), "thread_d": 0, "show_notes": "false", "part": '"all"',
         "cable_layout": '"%s"' % layout}
    for i, c in enumerate(cables):
        d["cable_%d_d" % (i + 1)] = c
    return d

SETS = [
    ("1x3mm", cfg([3])), ("1x4mm", cfg([4])), ("1x5mm", cfg([5])), ("1x6mm", cfg([6])),
    ("1x8mm", cfg([8])), ("1x10mm", cfg([10])),
    ("2x4mm", cfg([4, 4])), ("2x5mm", cfg([5, 5])), ("2x6mm", cfg([6, 6])),
    ("3x4mm", cfg([4, 4, 4])), ("3x5mm", cfg([5, 5, 5])),
    ("4x4mm", cfg([4, 4, 4, 4])),
]

def build(item):
    name, d = item
    tmp = os.path.join(HERE, "stl", name + ".tmp.stl")
    args = [OPENSCAD, "--backend=manifold", "--export-format", "binstl", "-o", tmp]
    for k, v in d.items():
        args += ["-D", "%s=%s" % (k, v)]
    args.append(os.path.join(ROOT, "cable_gland.scad"))
    p = subprocess.run(args, capture_output=True, text=True)
    out = p.stdout + p.stderr
    warns = re.findall(r'WARNING: ([^"]+)', out)
    m = re.search(r'"Thread: M([\d.]+)', out)
    drill = re.search(r'Panel hole: drill ([\d.]+) mm', out)
    if p.returncode or not m or warns:
        return name, None, warns or out[-500:]
    final = os.path.join(HERE, "stl", "cable_gland_%s_M%s_drill%smm.stl" % (name, m.group(1), drill.group(1)))
    os.replace(tmp, final)
    return name, os.path.basename(final), None

if __name__ == "__main__":
    bad = 0
    with ThreadPoolExecutor(os.cpu_count() or 4) as ex:
        for name, f, err in ex.map(build, SETS):
            print(("ok   " + f) if f else ("FAIL %s: %s" % (name, err)))
            bad += f is None
    sys.exit(bad)
