"""Render the listing images into showcase/img/.

    python showcase/render.py            # everything
    python showcase/render.py hero nut   # just some shots

Each shot is rendered at 2x with OpenSCAD and downsampled for smooth edges,
then the gallery and cover cards are composed with Pillow.
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "img")
RAW = os.path.join(OUT, "raw")
SCENE = os.path.join(HERE, "showcase.scad")
OPENSCAD = next(os.path.join(ROOT, "tools", d, "openscad.com") for d in sorted(os.listdir(os.path.join(ROOT, "tools")))
                if os.path.exists(os.path.join(ROOT, "tools", d, "openscad.com")))
W, H = 1600, 1200
BG = (248, 248, 248)


def scad_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"%s"' % v
    return str(v)


INFO = {}   # name -> thread size the model reported, e.g. "M15"


def render(name, defines, rot=(62, 0, 32), size=(W, H), dist=None, center=(0, 0, 0)):
    """Render one shot to RAW/name.png at 2x, return the downsampled image path.
    With dist the camera is fixed (same scale for every shot), otherwise it
    frames the whole scene."""
    os.makedirs(RAW, exist_ok=True)
    big = os.path.join(RAW, name + "@2x.png")
    cam = "%g,%g,%g,%g,%g,%g,%s" % (tuple(center) + tuple(rot) + (dist or 0,))
    args = [OPENSCAD, "--backend=manifold", "--render", "--camera=" + cam,
            "--imgsize=%d,%d" % (size[0] * 2, size[1] * 2), "--colorscheme=Tomorrow", "-o", big]
    if not dist:
        args += ["--viewall", "--autocenter"]
    for k, v in defines.items():
        args += ["-D", "%s=%s" % (k, scad_value(v))]
    args.append(SCENE)
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(big):
        raise RuntimeError("%s failed:\n%s" % (name, p.stderr[-2000:]))
    for line in (p.stdout + p.stderr).splitlines():
        if '"Thread: M' in line:
            INFO[name] = line.split('"Thread: ')[1].split(" ")[0]
    small = os.path.join(RAW, name + ".png")
    Image.open(big).convert("RGB").resize(size, Image.LANCZOS).save(small)
    return small


def font(size, bold=False):
    for f in (("arialbd.ttf" if bold else "arial.ttf"), ("segoeuib.ttf" if bold else "segoeui.ttf"),
              "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def subject_box(img):
    from PIL import ImageChops
    diff = ImageChops.difference(img, Image.new("RGB", img.size, BG)).convert("L")
    return diff.point(lambda v: 255 if v > 12 else 0).getbbox()


def trim(img, pad=40, box=None):
    """Crop the background around the subject (or box), keeping pad pixels."""
    box = box or subject_box(img)
    if not box:
        return img
    l, t, r, b = box
    return img.crop((max(0, l - pad), max(0, t - pad), min(img.width, r + pad), min(img.height, b + pad)))


def fit(img, w, h):
    """Scale img to fit inside w x h and centre it on the background."""
    img = trim(img)
    s = min(w / img.width, h / img.height)
    img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), BG)
    canvas.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return canvas


def caption(img, title, sub=None, title_size=54):
    """Title (and subtitle) across the top of an image."""
    d = ImageDraw.Draw(img)
    d.text((60, 44), title, fill=(34, 38, 43), font=font(title_size, True))
    if sub:
        d.text((62, 44 + title_size + 14), sub, fill=(95, 102, 110), font=font(int(title_size * 0.55)))
    return img


def card(src, out, title, sub=None):
    img = fit(Image.open(src).convert("RGB"), W, H - 150)
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(img, (0, 150))
    caption(canvas, title, sub).save(os.path.join(OUT, out))


# ---- shots ----
HERO = dict(cable_count=3, cable_1_d=6, cable_2_d=4, cable_3_d=4, thread_d=0)
LAYOUTS = [
    ("1 cable", dict(cable_count=1, cable_1_d=5, thread_d=0)),
    ("2 cables", dict(cable_count=2, cable_1_d=5, cable_2_d=5, thread_d=0)),
    ("3 mixed sizes", dict(cable_count=3, cable_1_d=6, cable_2_d=4, cable_3_d=3, thread_d=0)),
    ("4 inline", dict(cable_count=4, cable_layout="inline", cable_1_d=3, cable_2_d=5, cable_3_d=5, cable_4_d=3,
                      thread_d=0)),
    ("5 radial", dict(cable_count=5, thread_d=0)),
    ("8 radial", dict(cable_count=8, cable_1_d=3, cable_2_d=3, cable_3_d=3, cable_4_d=3, cable_5_d=3, cable_6_d=3,
                      cable_7_d=3, cable_8_d=3, thread_d=0)),
]
SIZES = [
    ("3 mm cable", dict(cable_count=1, cable_1_d=3, thread_d=0)),
    ("6 mm cable", dict(cable_count=1, cable_1_d=6, thread_d=0)),
    ("2 x 10 mm", dict(cable_count=2, cable_1_d=10, cable_2_d=10, thread_d=0)),
]
NOTES = dict(show_notes=False)


def shots():
    """name -> (defines, rot)"""
    s = {
        "hero": (dict(HERO, scene="hero"), (62, 0, 32)),
        "exploded": (dict(HERO, scene="exploded", explode=9), (58, 0, 32)),
        "arc_key": (dict(scene="segment", seg_pick=0, thread_d=0, cable_1_d=4), (55, 0, 340)),
        "keys_top": (dict(scene="plate", thread_d=0, cable_1_d=4), (0, 0, 0)),
        "nut": (dict(HERO, scene="nut"), (35, 0, 15)),
        "plate": (dict(HERO, scene="plate"), (35, 0, 10)),
    }
    for i, (_, d) in enumerate(LAYOUTS):
        s["layout%d" % i] = (dict(d, scene="body"), (50, 0, 25))
    for i, (_, d) in enumerate(SIZES):
        s["size%d" % i] = (dict(d, scene="hero"), (62, 0, 32), dict(dist=150, center=(0, 0, 6)))
    return s


def grid(names, labels, cols, out, title, sub, uniform=False):
    rows = (len(names) + cols - 1) // cols
    top = 170
    cw, ch = W // cols, (H - top) // rows
    canvas = Image.new("RGB", (W, H), BG)
    if uniform:   # same camera for all: crop every shot to the union of their subjects, keep the scale
        boxes = [subject_box(Image.open(os.path.join(RAW, n + ".png")).convert("RGB")) for n in names]
        union = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    d = ImageDraw.Draw(canvas)
    for i, (n, label) in enumerate(zip(names, labels)):
        x, y = (i % cols) * cw, top + (i // cols) * ch
        img = Image.open(os.path.join(RAW, n + ".png")).convert("RGB")
        if uniform:   # same camera for all: keep the scale, crop the middle
            img = trim(img, 20, union)
            sc = min((cw - 20) / img.width, (ch - 60) / img.height)
            img = img.resize((int(img.width * sc), int(img.height * sc)), Image.LANCZOS)
            cell = Image.new("RGB", (cw - 20, ch - 60), BG)
            cell.paste(img, ((cell.width - img.width) // 2, (cell.height - img.height) // 2))
            img = cell
        else:
            img = fit(img, cw - 20, ch - 60)
        canvas.paste(img, (x + 10, y))
        f = font(34, True)
        tw = d.textlength(label, font=f)
        d.text((x + (cw - tw) / 2, y + ch - 58), label, fill=(60, 66, 74), font=f)
    caption(canvas, title, sub).save(os.path.join(OUT, out))


def cover():
    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    # assembled on top, exploded underneath
    for src, label, y, h in (("hero.png", "Assembled", 130, 520), ("exploded.png", "Exploded", 660, 530)):
        canvas.paste(fit(Image.open(os.path.join(RAW, src)).convert("RGB"), 900, h), (20, y))
        d.text((60, y + 6), label, fill=(120, 127, 135), font=font(28, True))
    d.text((60, 40), "Customizable Split Cable Gland", fill=(34, 38, 43), font=font(64, True))
    bullets = [
        ("1 to 8 cables", "each with its own diameter"),
        ("Radial or inline", "holes spaced for you"),
        ("Your dimensions, or auto-fit", "set thread, flange and nut, or let it decide"),
        ("Arc keys", "lock the split body together"),
        ("Prints flat", "no supports, 45 deg max overhang"),
        ("Drill size on the nut", "metric and imperial"),
        ("Easy to customize", "set your cables, everything else adapts"),
    ]
    y = 200
    for head, rest in bullets:
        d.ellipse((960, y + 14, 980, y + 34), fill=(255, 122, 26))
        d.text((1000, y), head, fill=(34, 38, 43), font=font(40, True))
        d.text((1000, y + 50), rest, fill=(95, 102, 110), font=font(30))
        y += 135
    canvas.save(os.path.join(OUT, "00_cover.png"))


def main(want):
    os.makedirs(OUT, exist_ok=True)
    todo = {n: v for n, v in shots().items() if not want or any(n.startswith(w) for w in want)}
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        def go(kv):
            name, v = kv
            render(name, dict(NOTES, **v[0]), v[1], **(v[2] if len(v) > 2 else {}))
            return name
        for n in ex.map(go, todo.items()):
            print("rendered", n)
    have = lambda *ns: all(os.path.exists(os.path.join(RAW, n + ".png")) for n in ns)
    if have("hero", "exploded"):
        cover()
    if have("hero"):
        card(os.path.join(RAW, "hero.png"), "01_hero.png", "Seal cables through any panel",
             "Split body clamps around the cables, the nut locks it in the panel")
    if have("exploded"):
        card(os.path.join(RAW, "exploded.png"), "02_exploded.png", "Split body closes around the cables",
             "Close the segments around the cables, slide the keys together, screw the nut down")
    if have(*["layout%d" % i for i in range(len(LAYOUTS))]):
        grid(["layout%d" % i for i in range(len(LAYOUTS))], [l for l, _ in LAYOUTS], 3, "03_layouts.png",
             "Any cable count, any size", "Set the diameters, pick radial or inline, the body sizes itself")
    if have("arc_key", "keys_top"):
        card(os.path.join(RAW, "arc_key.png"), "04_arc_keys.png", "Arc keys lock the halves together",
             "Run the full height of the thread and hook against pulling apart, yet print flat")
        img = Image.open(os.path.join(OUT, "04_arc_keys.png"))
        inset = fit(Image.open(os.path.join(RAW, "keys_top.png")).convert("RGB"), 460, 345)
        d = ImageDraw.Draw(inset)
        d.rectangle((0, 0, inset.width - 1, inset.height - 1), outline=(200, 205, 210), width=3)
        d.text((16, 10), "from above", fill=(95, 102, 110), font=font(26))
        img.paste(inset, (W - inset.width - 40, H - inset.height - 40))
        img.save(os.path.join(OUT, "04_arc_keys.png"))
    if have("nut"):
        card(os.path.join(RAW, "nut.png"), "05_nut_label.png", "The drill size is on the nut",
             "Panel hole in mm and the nearest imperial drill, engraved on top")
    if have("plate"):
        card(os.path.join(RAW, "plate.png"), "06_print_plate.png", "Prints flat, no supports",
             "Thread flanks and chamfers never overhang more than 45 degrees")
    if have(*["size%d" % i for i in range(len(SIZES))]):
        labels = ["%s  →  %s" % (l, INFO.get("size%d" % i, "?")) for i, (l, _) in enumerate(SIZES)]
        grid(["size%d" % i for i in range(len(SIZES))], labels, 3, "07_sizes.png",
             "Tiny to chunky", "Auto mode picks the thread, flange and nut for your cables (shown to scale)",
             uniform=True)


if __name__ == "__main__":
    main(sys.argv[1:])
