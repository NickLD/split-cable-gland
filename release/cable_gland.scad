// Configurable split, threaded cable pass-through gland
//
// Inspired by "Locking Threaded 4mm Cable Pass Through Grommet"
// (printables.com/model/1151107). The body is split along the cables so it
// can be closed around a cable that already has connectors on both ends. The
// threaded shank goes through a panel hole and the hex nut clamps the panel
// against the flange while squeezing the split body closed around the
// cable(s).
//
// Extras over the original:
//  - 1 to 8 cables, each with its own diameter
//  - radial (ring) or inline cable layout; the body splits into one segment
//    per cable in radial mode, or two halves in inline mode
//  - optional tapered cable holes: loose at the tip, tight at the thread root,
//    so the grip builds up as the nut runs down toward the flange
//  - optional tapered thread: the nut wedges the segments together harder the
//    further it is screwed on
//  - printable alignment keys between segments: vertical (dovetail or
//    straight) tabs standing on the bed, mating slots cut through the flange,
//    so no supports or bridges
//
// Single file, no libraries, so it works with Thingiverse / MakerWorld /
// Printables customizers.

/* [What to render] */
// Print layout lays every part flat, ready to slice
part = "all"; // [all:Print layout (all parts), body:Body segments only, nut:Nut only, assembly:Assembled preview]

/* [Cables] */
// Number of cables passing through
cable_count = 1; // [1:1:8]
// Cable diameters (only the first cable_count are used)
cable_1_d = 4.0; // [1:0.1:20]
cable_2_d = 4.0; // [1:0.1:20]
cable_3_d = 4.0; // [1:0.1:20]
cable_4_d = 4.0; // [1:0.1:20]
cable_5_d = 4.0; // [1:0.1:20]
cable_6_d = 4.0; // [1:0.1:20]
cable_7_d = 4.0; // [1:0.1:20]
cable_8_d = 4.0; // [1:0.1:20]
// radial: cables evenly spaced on a ring, one body segment per cable. inline: cables in a row, body splits in two halves
cable_layout = "radial"; // [radial, inline]
// Ring radius for radial layout (0 = as tight as cable_web allows)
cable_ring_radius = 0; // [0:0.1:30]
// Minimum plastic between neighbouring holes
cable_web = 1.6; // [0.8:0.1:6]
// Rotate the cable pattern (degrees)
layout_rotation = 0; // [0:1:359]

/* [Cable hole sealing] */
// Extra diameter of each hole at the thread tip (the whole hole if hole_taper is off)
hole_clearance = 0.3; // [0:0.05:1.5]
// Taper the holes from loose at the thread tip to tight at the thread root. Off by default: the tight part pinches the cable so hard the halves (and dovetail keys) cannot close. Try it with soft cable jackets and a small hole_squeeze
hole_taper = false;
// How much smaller than the cable the hole is at the thread root and through the flange (needs hole_taper)
hole_squeeze = 0.3; // [0:0.05:1.5]
// 45 degree chamfer where the cable leaves the thread tip, so no sharp edge bites into it (limited by the surrounding wall). The bed end of the hole uses bottom_chamfer instead
hole_chamfer = 0.6; // [0:0.1:2]

/* [Thread] */
// Thread major diameter at the tip (0 = auto from cables). This is what the nut screws onto
thread_d = 12; // [0:0.5:60]
// Length of the threaded shank (panel thickness + nut height + a little)
thread_length = 12; // [3:0.5:60]
// Thread pitch
thread_pitch = 2.5; // [1:0.1:5]
// Included thread angle. 90 = 45 degree flanks, nothing overhangs more than 45 degrees when printed upright (recommended). 60 = ISO-style, deeper but the flanks overhang 60 degrees
thread_angle = 90; // [60:5:100]
// Width of the flat at the thread crest and root, roughly your nozzle width so the slicer can lay a full line there
thread_flat = 0.4; // [0.1:0.05:1]
// Extra diameter at the flange end of the thread. >0 makes the nut squeeze the split body shut as it tightens. Keep it <= split_gap
thread_taper = 0; // [0:0.05:1]
// Minimum wall between the cable holes and the thread root (used by auto thread_d and warnings)
min_wall = 1.5; // [0.8:0.1:5]

/* [Flange and split] */
// Flange size: diameter, or across flats for hex (0 = auto: thread + 2 x flange_rim, grown if the keys need more room)
flange_d = 0; // [0:0.5:100]
// Width of the flange ring outside the thread when flange_d is auto
flange_rim = 5; // [2:0.5:20]
// Flange thickness
flange_t = 3; // [1.5:0.1:10]
flange_shape = "round"; // [round, hex]
// Edge chamfer on the flange
flange_chamfer = 0.6; // [0:0.1:2]
// Material removed at each split so the segments can be clamped together
split_gap = 0.2; // [0:0.05:1]
// 45 degree chamfer on every edge that sits on the bed (split faces, keys, key slots, cable holes, nut) so elephant's foot can't stop the segments closing. Off by default: it shrinks the first layer of the thin shank keys and walls, which then may not stick. Prefer your slicer's elephant foot compensation; try 0.2-0.4 if parts still won't close
bottom_chamfer = 0; // [0:0.05:1]
// Keys that align and lock the segments. All are vertical prisms (print flat, no supports) and the segments slide together along the cable. arc: curved tab that follows the circle around the axis, so it can reach deep into the neighbour and hooks against pulling apart. dovetail: classic flared tab. straight: simple locating tab, does not lock
key_style = "arc"; // [arc, dovetail, straight, none]
// Where the keys go. shank: inside the threaded part, between the cable hole and the thread root, running the full height of the body for long engagement (shrunk to fit the wall there). flange: in the flange ring outside the thread. both: one of each at every split
key_location = "both"; // [both, shank, flange]
// Key width where it leaves the split face (arc keys in the shank use whatever fits between hole and thread root, up to this)
key_width = 2; // [1:0.1:6]
// How far the key reaches into the neighbouring segment (along the curve for arc keys; dovetail and straight shank keys shrink to fit)
key_length = 4; // [1:0.1:10]
// Dovetail flare angle (each side)
key_angle = 12; // [5:1:25]
// Gap per side between key and slot
key_clearance = 0.1; // [0:0.05:0.5]
// Minimum plastic either side of a shank key slot (to the cable hole and to the thread root). 0.8 is two lines with a 0.4 mm nozzle. Auto thread_d grows to keep it
key_wall = 0.8; // [0.4:0.05:2]

/* [Nut] */
nut_height = 6; // [2:0.5:30]
// Across flats (0 = auto: thread_d + 8)
nut_af = 0; // [0:0.5:100]
// Radial clearance between body thread and nut thread
nut_clearance = 0.15; // [0:0.05:0.8]
// Classic 30 degree corner chamfer on the top of the nut. The bed face only gets a 45 degree bottom_chamfer, so nothing overhangs
nut_chamfer = 0.8; // [0:0.1:3]

/* [Quality and layout] */
// Segments per turn of the thread (higher = smoother, slower)
thread_fn = 120; // [36:6:360]
// Facets for round parts
round_fn = 96; // [24:4:180]
// Gap between parts in the print layout
part_spacing = 4; // [1:0.5:20]
// Draw notes beside the model: the panel drill size when thread_d is auto, and any problems (keys skipped, thin walls, ...) in red. It is real geometry, so it also ends up in the exported file: turn this off before exporting for print
show_notes = true;
// Engrave the panel drill size (mm, and the nearest inch drill) on top of the nut
label_nut = true;

/* [Hidden] */
eps = 0.01;
all_cable_d = [cable_1_d, cable_2_d, cable_3_d, cable_4_d,
               cable_5_d, cable_6_d, cable_7_d, cable_8_d];
N = max(1, min(8, round(cable_count)));
cable_d = [for (i = [0:N-1]) all_cable_d[i]];
hole_loose_d = [for (d = cable_d) d + hole_clearance];   // at the thread tip
hole_tight_d = [for (d = cable_d) hole_taper ? d - hole_squeeze : d + hole_clearance];   // root + flange

// Trapezoid profile: crest and root flats of thread_flat, straight flanks at
// thread_angle / 2 from the radial plane. Depth follows from pitch and angle.
flat_frac = min(thread_flat / thread_pitch, 0.3);
thread_depth = thread_pitch * (1 - 2 * flat_frac) / (2 * tan(thread_angle / 2));
thread_flank = thread_depth * tan(thread_angle / 2) / thread_pitch;   // fraction of pitch
thread_crest = flat_frac;
thread_root = 1 - 2 * thread_flank - thread_crest;

// ---- cable positions ----
function inline_x(k) = k == 0 ? 0
    : inline_x(k - 1) + (hole_loose_d[k - 1] + hole_loose_d[k]) / 2 + cable_web;
inline_shift = (inline_x(N - 1) + hole_loose_d[N - 1] / 2 - hole_loose_d[0] / 2) / 2;

ring_pair_need = [for (i = [0:N-1]) (hole_loose_d[i] + hole_loose_d[(i + 1) % N]) / 2 + cable_web];
ring_r = N == 1 ? 0
    : cable_ring_radius > 0 ? cable_ring_radius
    : max(ring_pair_need) / (2 * sin(180 / N));

is_inline = cable_layout == "inline" || N == 1;
cable_pos = [for (k = [0:N-1])
    is_inline
        ? [cos(layout_rotation), sin(layout_rotation)] * (inline_x(k) - inline_shift)
        : ring_r * [cos(layout_rotation + k * 360 / N), sin(layout_rotation + k * 360 / N)]];

// Radius of the circle that encloses every hole
envelope_r = max([for (k = [0:N-1]) norm(cable_pos[k]) + hole_loose_d[k] / 2]);

// Split planes: half-planes from the axis through each cable (radial) or
// one full plane along the row of cables (inline)
cut_angles = is_inline
    ? [layout_rotation, layout_rotation + 180]
    : [for (k = [0:N-1]) layout_rotation + k * 360 / N];
n_seg = len(cut_angles);

// ---- derived sizes ----
// Wall the shank keys need: room for one at least 1.2 mm wide (or full size if smaller)
sk_min_scale = min(1, 1.2 / key_width);
sk_wall_need = key_style != "none" && key_location != "flange"
    ? sk_min_scale * (key_width + (key_style == "dovetail" ? 2 * key_length * tan(key_angle) : 0))
      + 2 * key_clearance + 2 * key_wall + (key_style == "arc" ? split_gap : 0) + 0.01
    : 0;
auto_thread_d = ceil(2 * (envelope_r + max(min_wall, sk_wall_need) + thread_depth));
tip_d = thread_d > 0 ? thread_d : auto_thread_d;
base_d = tip_d + thread_taper;
tip_minor_d = tip_d - 2 * thread_depth;
af = nut_af > 0 ? nut_af : tip_d + 8;
body_h = flange_t + thread_length;
is_arc = key_style == "arc";
key_flare = key_style == "dovetail" ? tan(key_angle) : 0;
key_tip_w = key_width + 2 * key_length * key_flare;
// An arc slot is swept across the split gap so the nut can still close it,
// which pushes its outer edge out by up to split_gap: reserve that room.
arc_sweep = key_style == "arc" ? split_gap : 0;
key_need = key_tip_w + 2 * key_clearance + 1.2 + arc_sweep;   // flange ring width a key needs (arc: key_tip_w = key_width)

// Shank keys: on each split face, in the strip between the outermost cable
// hole on that face and the thread root. Scaled down (never up) to leave
// key_wall of plastic either side of the slot.
root_r = (tip_d - 2 * thread_depth) / 2;
function ray_hole_out(a) = max(concat([0], [for (k = [0:N-1])
    let (x = cos(a) * cable_pos[k][0] + sin(a) * cable_pos[k][1],
         y = -sin(a) * cable_pos[k][0] + cos(a) * cable_pos[k][1])
    if (abs(y) < 1e-6 && x + hole_loose_d[k] / 2 > 0) x + hole_loose_d[k] / 2]));
sk_in = [for (a = cut_angles) ray_hole_out(a)];
sk_room = [for (r = sk_in) root_r - r - 2 * key_wall - 2 * key_clearance - arc_sweep];   // widest key that fits
// dovetail / straight: width and length scaled together. arc: width fills
// the strip (up to key_width), length stays key_length.
sk_scale = [for (w = sk_room) is_arc ? min(1, w / key_width) : min(1, w / key_tip_w)];
sk_fit = [for (sc = sk_scale) key_style != "none" && key_location != "flange" && sc * key_width >= 0.8];
sk_r = [for (r = sk_in) (r + root_r - arc_sweep) / 2];
// Arc keys turn through at most 0.4 of the segment, so they never reach the
// next split face or its key
seg_span = [for (i = [0:n_seg-1]) (i < n_seg - 1 ? cut_angles[i + 1] : cut_angles[0] + 360) - cut_angles[i]];
function arc_deg(rc, i) = min(key_length / rc * 180 / PI, 0.4 * min(seg_span), 75);
n_shank_keys = len([for (f = sk_fit) if (f) 1]);
flange_keys_wanted = key_style != "none" && (key_location != "shank" || n_shank_keys < n_seg);
auto_fl_d = ceil(2 * (base_d / 2 + max(flange_rim, flange_keys_wanted ? key_need : 0) + flange_chamfer) * 2) / 2;
fl_d = flange_d > 0 ? flange_d : auto_fl_d;
flange_inner_r = fl_d / 2;   // round: radius, hex: inscribed radius
key_band = flange_inner_r - flange_chamfer - base_d / 2;   // flange ring outside the thread
key_r_pos = base_d / 2 + key_band / 2;
keys_fit = key_style != "none" && key_band >= key_need;
// flange key at split i: always with "both"/"flange", with "shank" only where no shank key fits
fl_key = [for (i = [0:n_seg-1]) keys_fit && (key_location != "shank" || !sk_fit[i])];
n_flange_keys = len([for (f = fl_key) if (f) 1]);
any_keys = n_shank_keys + n_flange_keys > 0;

// Smallest plastic web between any two holes
min_hole_web = N == 1 ? 999 : min([for (i = [0:N-2]) for (j = [i+1:N-1])
    norm(cable_pos[i] - cable_pos[j]) - (hole_loose_d[i] + hole_loose_d[j]) / 2]);
hole_wall = tip_minor_d / 2 - envelope_r;
nut_wall = (af - tip_d - 2 * nut_clearance) / 2;
thread_engage = thread_depth - nut_clearance;

// Panel hole: clear the thread (at its fattest, by the flange) by 0.3 mm,
// rounded up to the next 0.5 mm drill. The flange and nut need ~2.5 mm of
// land around the hole to clamp and seal.
drill_min = base_d + 0.3;
drill_mm = ceil(drill_min * 2) / 2;
drill_max = min(fl_d, af) - 5;
drill_in16 = ceil(drill_min / 25.4 * 16);   // nearest 1/16" at or above drill_min
function _frac(n, d) = (n % 2 == 0 && d > 1) ? _frac(n / 2, d / 2) : [n, d];
function inch_str(n16, unit = " in") = let (w = floor(n16 / 16), r = n16 % 16, f = _frac(r, 16))
    str(w > 0 ? str(w) : "", w > 0 && r > 0 ? " " : "", r > 0 ? str(f[0], "/", f[1]) : "", unit);
drill_in_ok = drill_in16 * 25.4 / 16 <= drill_max;
drill_note = str("Panel hole: drill ", drill_mm, " mm", drill_in_ok ? str(" (or ", inch_str(drill_in16), ")") : "",
                 ", anything ", drill_min, "-", drill_max, " mm works. Thread M", tip_d, "x", thread_pitch,
                 ", nut ", af, " AF.");

// Shank keys asked for but some split has no room for one
sk_missing = [for (i = [0:n_seg-1]) if (!sk_fit[i]) i];
sk_warn = key_style != "none" && key_location != "flange" && len(sk_missing) > 0;
sk_have = sk_warn ? min([for (i = sk_missing) root_r - sk_in[i]]) : 0;
sk_need_min = 0.8 / key_width * key_tip_w + 2 * key_clearance + 2 * key_wall + arc_sweep;   // smallest key we make
sk_thread_d = ceil(2 * (max(sk_in) + sk_wall_need + thread_depth));            // room for a 1.2 mm key

warnings = concat(
    sk_warn
        ? [str("Shank keys skipped at ", len(sk_missing), " of ", n_seg, " splits: only ", round(sk_have * 100) / 100,
               " mm between cable hole and thread root, a shank key needs ", round(sk_need_min * 100) / 100,
               ". Use thread_d >= ", sk_thread_d, " (or 0 = auto)",
               keys_fit ? ", or key_location = flange. Flange keys still hold it." : ". These splits have no key at all.")] : [],
    hole_wall < min_wall
        ? [str("Only ", round(hole_wall * 100) / 100, " mm between cable holes and thread root. Use thread_d >= ",
               auto_thread_d, " (or 0 = auto).")] : [],
    min_hole_web < cable_web - eps
        ? [str("Cable holes only ", round(min_hole_web * 100) / 100, " mm apart. Increase cable_ring_radius (or 0 = auto).")] : [],
    flange_keys_wanted && !keys_fit
        ? [str("Alignment keys skipped: flange ring ", round(key_band * 100) / 100, " mm, keys need ",
               round(key_need * 100) / 100, ". Use flange_d >= ", auto_fl_d, " (or 0 = auto).")] : [],
    flange_inner_r <= base_d / 2 + 1
        ? ["Flange is barely larger than the thread."] : [],
    nut_wall < 1.5
        ? [str("Nut wall only ", round(nut_wall * 100) / 100, " mm. Increase nut_af (or 0 = auto).")] : [],
    thread_taper > split_gap + eps
        ? ["thread_taper > split_gap: the nut will bind before the segments close."] : [],
    thread_engage < 0.4
        ? [str("Thread engagement only ", round(thread_engage * 100) / 100,
               " mm. Increase thread_pitch or reduce thread_flat / nut_clearance.")] : [],
    drill_max < drill_min
        ? ["Flange or nut too small to cover the panel hole. Increase flange_d / nut_af (or 0 = auto)."] : []);

echo(str("Cables: ", N, " diameters ", cable_d, " layout ", is_inline ? "inline" : "radial",
         is_inline ? "" : str(" ring r=", ring_r)));
echo(str("Thread: M", tip_d, " x ", thread_pitch, thread_taper > 0 ? str(" (", base_d, " at flange)") : "",
         ", length ", thread_length, ", root dia ", tip_minor_d));
echo(str("Thread depth ", thread_depth, ", engagement ", thread_engage, ".  Flange: ", fl_d,
         flange_d > 0 ? "" : " (auto)", ".  Nut: ", af, " AF x ", nut_height));
echo(drill_note);
echo(str("Body segments: ", n_seg, ", alignment keys: ", any_keys ? key_style : "none",
         ", ", n_shank_keys, " in the shank ", [for (i = [0:n_seg-1]) if (sk_fit[i])
             str(round(sk_scale[i] * key_width * 100) / 100, "x",
                 round((is_arc ? arc_deg(sk_r[i], i) * PI / 180 * sk_r[i] : sk_scale[i] * key_length) * 100) / 100, " mm")],
         ", ", n_flange_keys, " in the flange"));
for (w = warnings) echo(str("WARNING: ", w));
// Machine-readable line for tests/run_tests.py
echo(str("SUMMARY|n_seg=", n_seg, "|keys=", any_keys ? 1 : 0, "|shank_keys=", n_shank_keys,
         "|flange_keys=", n_flange_keys, "|shank_key_len=",
         n_shank_keys > 0 ? min([for (i = [0:n_seg-1]) if (sk_fit[i])
             is_arc ? arc_deg(sk_r[i], i) * PI / 180 * sk_r[i] : sk_scale[i] * key_length]) : 0, "|shank_key_w=",
         n_shank_keys > 0 ? min([for (i = [0:n_seg-1]) if (sk_fit[i]) sk_scale[i] * key_width]) : 0, "|thread_d=", tip_d, "|flange_d=", fl_d,
         "|hole_wall=", hole_wall, "|hole_web=", min_hole_web, "|nut_af=", af,
         "|tight_d=", hole_tight_d[0], "|drill=", drill_mm, "|drill_min=", drill_min,
         "|drill_max=", drill_max, "|depth=", thread_depth, "|nut_label=", label_nut && nut_label_size >= 1.5 ? 1 : 0, "|loose_d=", hole_loose_d[0], "|warnings=", len(warnings)));

// ---- thread ----
// Solid threaded rod, z from 0 to len. Major diameter goes linearly from
// d0 (z=0) to d1 (z=len). The exact tooth profile (root edge, flank, crest,
// flank) is swept along the helix, so crest and root edges are true helical
// lines at any resolution. The tooth sinks into a core cone; consecutive turns
// are separated by the root flat, so the sweep never touches itself.
module threaded_rod(d0, d1, len, pitch, depth) {
    n = thread_fn;
    turns = ceil(len / pitch) + 2;           // one spare turn below 0 and above len
    hb = (1 - thread_root) * pitch / 2;      // tooth half-width at the root
    hc = thread_crest * pitch / 2;           // half-width of the crest flat
    sink = max(0.3, depth / 2);              // how far the tooth reaches into the core
    prof = [[-sink, -hb], [0, -hb], [depth, -hc], [depth, hc], [0, hb], [-sink, hb]];
    m = len(prof);
    function root_r(z) = (d0 + (d1 - d0) * min(max(z / len, 0), 1)) / 2 - depth;
    pts = [for (j = [0:turns * n]) for (q = prof)
        let (a = 360 * j / n,
             z = pitch * (j / n - 1) + pitch / 2 + q[1],
             r = root_r(z) + q[0])
        [r * cos(a), r * sin(a), z]];
    sides = [for (j = [0:turns * n - 1]) for (k = [0:m-1])
        [j * m + k, j * m + (k + 1) % m, (j + 1) * m + (k + 1) % m, (j + 1) * m + k]];
    intersection() {
        union() {
            polyhedron(points = pts,
                       faces = concat([[for (k = [m-1:-1:0]) k]],
                                      [[for (k = [0:m-1]) turns * n * m + k]],
                                      sides),
                       convexity = turns + 2);
            // core at the root diameter (a hair over, so the root flat is clean)
            translate([0, 0, -1])
                cylinder(h = len + 2,
                         d1 = d0 - 2 * depth + 0.002 - (d1 - d0) / len,
                         d2 = d1 - 2 * depth + 0.002 + (d1 - d0) / len, $fn = n);
        }
        translate([-(max(d0, d1) + 2), -(max(d0, d1) + 2), 0])
            cube([2 * max(d0, d1) + 4, 2 * max(d0, d1) + 4, len]);
    }
}

// ---- body ----
module flange_solid() {
    fn = flange_shape == "hex" ? 6 : round_fn;
    k = flange_shape == "hex" ? 1 / cos(30) : 1;   // across flats -> circumscribed
    c = min(flange_chamfer, flange_t / 3);
    hull() {
        cylinder(h = flange_t, d = (fl_d - 2 * c) * k, $fn = fn);
        translate([0, 0, c]) cylinder(h = flange_t - 2 * c, d = fl_d * k, $fn = fn);
    }
}

module shank() {
    ch = thread_depth;
    translate([0, 0, flange_t - eps])
    intersection() {
        threaded_rod(base_d, tip_d, thread_length + eps, thread_pitch, thread_depth);
        // lead-in chamfer at the tip
        union() {
            cylinder(h = thread_length - ch, d = base_d + 2, $fn = round_fn);
            translate([0, 0, thread_length - ch - eps])
                cylinder(h = ch + 2 * eps, d1 = tip_d + 2 * eps, d2 = tip_d - 2 * ch, $fn = round_fn);
        }
    }
}

// Tight (hole_tight_d) through the flange and at the thread root, opening up
// linearly to hole_loose_d at the thread tip
// Chamfer actually used: never more than half the plastic around a hole
hole_ch = max(0, min(hole_chamfer, hole_wall / 2, min_hole_web / 2,
                     n_shank_keys > 0 ? key_wall - 0.1 : 99));   // leave the wall beside a shank key slot
bot_ch = max(0, min(bottom_chamfer, flange_t / 3));
hole_ch_bed = min(hole_ch, bot_ch);   // bed end of the holes

module cable_holes() {
    for (k = [0:N-1])
        translate([cable_pos[k][0], cable_pos[k][1], 0]) {
            if (hole_ch_bed > 0)
                translate([0, 0, -1])
                    cylinder(h = 1 + hole_ch_bed + eps, d1 = hole_tight_d[k] + 2 * hole_ch_bed + 2,
                             d2 = hole_tight_d[k], $fn = round_fn / 2);
            if (hole_ch > 0) {
                translate([0, 0, body_h - hole_ch])
                    cylinder(h = hole_ch + 1, d1 = hole_loose_d[k], d2 = hole_loose_d[k] + 2 * hole_ch + 2,
                             $fn = round_fn / 2);
            }
            translate([0, 0, -1])
                cylinder(h = flange_t + 1 + eps, d = hole_tight_d[k], $fn = round_fn / 2);
            // extend past the tip along the same slope so the top edge is clean
            translate([0, 0, flange_t])
                cylinder(h = thread_length + 1,
                         d1 = hole_tight_d[k],
                         d2 = hole_loose_d[k] + (hole_loose_d[k] - hole_tight_d[k]) / thread_length,
                         $fn = round_fn / 2);
        }
}

big_r = max(fl_d, base_d, af) * 2;

module split_slabs() {
    for (a = cut_angles) rotate([0, 0, a]) {
        if (split_gap > 0)
            translate([0, -split_gap / 2, -1]) cube([big_r, split_gap, body_h + 2]);
        // V-groove along the split on the bed face: chamfers both split edges
        if (bot_ch > 0)
            rotate([90, 0, 90]) linear_extrude(height = big_r)
                polygon([[-split_gap / 2 - bot_ch - 1, -1], [split_gap / 2 + bot_ch + 1, -1],
                         [split_gap / 2, bot_ch], [-split_gap / 2, bot_ch]]);
    }
}

module body_whole() {
    difference() {
        union() { flange_solid(); shank(); }
        cable_holes();
        split_slabs();
    }
}

module wedge(a0, a1) {
    steps = max(2, ceil((a1 - a0) / 5));
    translate([0, 0, -2])
    linear_extrude(height = body_h + 4)
        polygon(concat([[0, 0]],
            [for (s = [0:steps]) big_r * [cos(a0 + (a1 - a0) * s / steps), sin(a0 + (a1 - a0) * s / steps)]]));
}

// Key profile on the split plane at angle a, in a frame where the plane is
// the x axis and +y points into the segment with the larger angle. Width is
// key_width at y = y_face and flares (dovetail) as y grows. Extruded the full
// flange height so it prints standing on the bed; the slot it fits into goes
// right through the flange, so nothing overhangs.
// rc is the key's distance from the axis, sc scales its width and length.
function key_poly(y_face, y0, y1, extra, rc, sc) =
    let (w0 = sc * key_width + 2 * (y0 - y_face) * key_flare + 2 * extra,
         w1 = sc * key_width + 2 * (y1 - y_face) * key_flare + 2 * extra)
    [[rc - w0 / 2, y0], [rc + w0 / 2, y0],
     [rc + w1 / 2, y1], [rc - w1 / 2, y1]];

// Tab on the face at angle a (belongs to the segment below that angle),
// h tall. Its bed edges are chamfered.
module key_tab(a, h, rc, sc) {
    c = max(0, min(bot_ch, sc * key_width * 0.4, sc * key_length * 0.4));
    y_face = -split_gap / 2;
    y0 = y_face - 1;
    y1 = y_face + sc * key_length;
    rotate([0, 0, a]) hull() {
        linear_extrude(height = eps) polygon(key_poly(y_face, y0, y1 - c, -c, rc, sc));
        translate([0, 0, c]) linear_extrude(height = h - c)
            polygon(key_poly(y_face, y0, y1, 0, rc, sc));
    }
}

// Slot on the face at angle a (belongs to the segment above that angle),
// right through the h-tall part. Sized for the clamped state, when the split
// gap has closed; the mouth on the bed is opened up by bot_ch.
module key_slot(a, h, rc, sc) {
    y_face = split_gap / 2;
    y0 = y_face - 1;
    y1 = y_face + sc * key_length + key_clearance;
    rotate([0, 0, a]) {
        translate([0, 0, -1]) linear_extrude(height = h + 2)
            polygon(key_poly(y_face, y0, y1, key_clearance, rc, sc));
        if (bot_ch > 0) hull() {
            translate([0, 0, -1]) linear_extrude(height = 1)
                polygon(key_poly(y_face, y0, y1 + bot_ch, key_clearance + bot_ch, rc, sc));
            translate([0, 0, bot_ch]) linear_extrude(height = eps)
                polygon(key_poly(y_face, y0, y1, key_clearance, rc, sc));
        }
    }
}

// Arc key: a sector of the ring rc +- w/2 around the gland axis, from just
// behind the split face to deg degrees into the neighbour. Pulling the
// segments apart drives its inner edge into the neighbour, so it hooks.
function arc_pts(r1, r2, f0, f1) =
    [r2 * [cos(f0), sin(f0)], r2 * [cos(f1), sin(f1)], r1 * [cos(f1), sin(f1)], r1 * [cos(f0), sin(f0)]];

// Built from short pieces so each can be hulled (for the bed chamfer)
// without filling in the curve.
module arc_tab(a, h, rc, w, deg) {
    c = max(0, min(bot_ch, w * 0.4));
    f0 = -(1 + split_gap) / rc * 180 / PI;
    n = max(1, ceil((deg - f0) / 4));
    rotate([0, 0, a]) for (i = [0:n-1]) {
        g0 = f0 + (deg - f0) * i / n;
        g1 = f0 + (deg - f0) * (i + 1) / n;
        hull() {
            linear_extrude(height = eps)
                polygon(arc_pts(rc - w / 2 + c, rc + w / 2 - c, g0, i == n - 1 ? g1 - c / (rc + w / 2) * 180 / PI : g1));
            translate([0, 0, c]) linear_extrude(height = h - c) polygon(arc_pts(rc - w / 2, rc + w / 2, g0, g1));
        }
    }
}

// The slot is the tab plus clearance, swept across the split gap: the
// segments close by split_gap when the nut clamps them, and an arc does not
// slide along the face normal the way a straight key does.
module arc_slot(a, h, rc, w, deg) {
    r1 = rc - w / 2 - key_clearance;
    r2 = rc + w / 2 + key_clearance;
    f0 = -(1 + split_gap) / rc * 180 / PI;
    f1 = deg + key_clearance / r1 * 180 / PI;
    n = max(1, ceil((f1 - f0) / 4));
    rotate([0, 0, a]) for (i = [0:n-1]) {
        g0 = f0 + (f1 - f0) * i / n;
        g1 = f0 + (f1 - f0) * (i + 1) / n;
        hull() for (t = [0, split_gap]) translate([0, t, -1])
            linear_extrude(height = h + 2) polygon(arc_pts(r1, r2, g0, g1));
        if (bot_ch > 0) hull() for (t = [0, split_gap]) translate([0, t, 0]) {
            translate([0, 0, -1]) linear_extrude(height = 1)
                polygon(arc_pts(r1 - bot_ch, r2 + bot_ch, g0, i == n - 1 ? g1 + bot_ch / (r2 + bot_ch) * 180 / PI : g1));
            translate([0, 0, bot_ch]) linear_extrude(height = eps) polygon(arc_pts(r1, r2, g0, g1));
        }
    }
}

module any_key(tab, i, a, h, rc, sc) {
    if (is_arc) {
        if (tab) arc_tab(a, h, rc, sc * key_width, arc_deg(rc, i));
        else arc_slot(a, h, rc, sc * key_width, arc_deg(rc, i));
    } else {
        if (tab) key_tab(a, h, rc, sc); else key_slot(a, h, rc, sc);
    }
}

// All key tabs (tabs = true) or slots on split i, the face at angle a
module split_keys(i, a, tabs) {
    if (fl_key[i]) any_key(tabs, i, a, flange_t, key_r_pos, 1);
    if (sk_fit[i]) any_key(tabs, i, a, body_h, sk_r[i], sk_scale[i]);
}

// Read-only accessors for files that use<> this one (tests, showcase renders)
function n_segments() = n_seg;
function seg_color(k) = seg_colors[k % 8];
function cable_positions() = cable_pos;
function cable_diameters() = cable_d;
function body_height() = body_h;
function flange_thickness() = flange_t;
function flange_radius() = flange_outer_r;
function nut_across_flats() = af;
function panel_drill() = drill_mm;
function split_angles() = cut_angles;
function print_spread() = layout_spread;
function thread_size() = tip_d;
function seg_a0(k) = cut_angles[k];
function seg_a1(k) = k < n_seg - 1 ? cut_angles[k + 1] : cut_angles[0] + 360;

module segment(k) {
    a0 = seg_a0(k);
    a1 = seg_a1(k);
    difference() {
        union() {
            intersection() { body_whole(); wedge(a0, a1); }
            split_keys((k + 1) % n_seg, a1, true);
        }
        split_keys(k, a0, false);
        cable_holes();   // keep shank tabs out of the hole chamfers
    }
}

// ---- nut ----
module nut() {
    bore = tip_d + 2 * nut_clearance;
    c = min(nut_chamfer, nut_height / 4);
    corner_d = af / cos(30);
    difference() {
        intersection() {
            // hex, 45 degree chamfer on the bed face (elephant's foot, no overhang)
            hull() {
                cylinder(h = eps, d = (af - 2 * bot_ch) / cos(30), $fn = 6);
                translate([0, 0, bot_ch]) cylinder(h = nut_height - bot_ch, d = corner_d, $fn = 6);
            }
            // classic chamfer on the hex corners, top face only
            hull() {
                cylinder(h = nut_height, d = af - 2 * c, $fn = round_fn);
                cylinder(h = nut_height - c, d = corner_d + 2 * c, $fn = round_fn);
            }
        }
        translate([0, 0, -1])
            threaded_rod(bore, bore, nut_height + 2, thread_pitch, thread_depth);
        // countersinks so the thread starts cleanly
        translate([0, 0, -eps])
            cylinder(h = thread_depth + eps, d1 = bore + 2 * eps, d2 = bore - 2 * thread_depth, $fn = round_fn);
        translate([0, 0, nut_height - thread_depth])
            cylinder(h = thread_depth + eps, d1 = bore - 2 * thread_depth, d2 = bore + 2 * eps, $fn = round_fn);
        if (label_nut && nut_label_size >= 1.5)
            translate([0, 0, nut_height - 0.4])
                linear_extrude(height = 1) {
                    arc_text(str("DRILL ", drill_mm, "MM"), nut_label_r, nut_label_size, 90);
                    if (drill_in_ok)
                        arc_text(str("OR ", inch_str(drill_in16, "\"")), nut_label_r, nut_label_size, 270);
                }
    }
}

// Label ring on the nut's top face, between the bore and the chamfered flats
nut_label_r = (tip_d / 2 + nut_clearance + af / 2 - min(nut_chamfer, nut_height / 4)) / 2;
nut_label_size = min(3.5, (af / 2 - min(nut_chamfer, nut_height / 4) - tip_d / 2 - nut_clearance) * 0.6);

// Characters laid along a circle of radius r, centred on angle `at`. Text on
// the top half reads clockwise, on the bottom half counter-clockwise, so both
// read left to right.
module arc_text(txt, r, size, at) {
    n = len(txt);
    step = size * 0.8 / r * 180 / PI;
    flip = at > 180;
    for (i = [0:n-1]) {
        a = flip ? at + (i - (n - 1) / 2) * step : at - (i - (n - 1) / 2) * step;
        rotate([0, 0, a]) translate([r, 0]) rotate([0, 0, flip ? 90 : -90])
            text(txt[i], size = size, halign = "center", valign = "center",
                 font = "Liberation Sans:style=Bold", $fn = 24);
    }
}

// ---- output ----
module body_parts(spread) {
    for (k = [0:n_seg-1]) {
        mid = (seg_a0(k) + seg_a1(k)) / 2;
        translate(spread * [cos(mid), sin(mid), 0]) segment(k);
    }
}

// Push segments apart along their bisectors so neighbours (and their keys)
// end up at least part_spacing apart
layout_spread = (part_spacing + (any_keys ? key_length : 0)) / (2 * sin(180 / n_seg));
flange_outer_r = flange_shape == "hex" ? fl_d / 2 / cos(30) : fl_d / 2;

show_drill_note = thread_d == 0;
module notes_text() {
    if (show_notes && (show_drill_note || len(warnings) > 0)) {
        x0 = -(flange_outer_r + layout_spread);
        y0 = -(max(flange_outer_r, af / 2 / cos(30)) + layout_spread + 8);
        color("DimGray") linear_extrude(height = 0.6)
            translate([x0, y0]) text("NOTES (set show_notes = false before exporting for print):", size = 3);
        if (show_drill_note)
            color("RoyalBlue") linear_extrude(height = 0.6)
                translate([x0, y0 - 5]) text(drill_note, size = 3);
        for (i = [0:len(warnings) - 1])
            color("Red") linear_extrude(height = 0.6)
                translate([x0, y0 - 5 * (i + 1 + (show_drill_note ? 1 : 0))])
                    text(str("! ", warnings[i]), size = 3);
    }
}

seg_colors = ["OrangeRed", "DarkOrange", "Gold", "Tomato", "Coral", "Orange", "SandyBrown", "Chocolate"];

notes_text();

if (part == "body") {
    body_parts(layout_spread);
} else if (part == "nut") {
    nut();
} else if (part == "assembly") {
    for (k = [0:n_seg-1]) color(seg_colors[k % 8]) segment(k);
    // pretend 3 mm panel
    color("SteelBlue", 0.35) translate([0, 0, flange_t]) difference() {
        cylinder(h = 3, d = max(fl_d, af) + 12, $fn = round_fn);
        translate([0, 0, -1]) cylinder(h = 5, d = drill_mm, $fn = round_fn);
    }
    color("DimGray") translate([0, 0, flange_t + 3]) nut();
    color("Black", 0.6)
        for (k = [0:N-1]) translate([cable_pos[k][0], cable_pos[k][1], -15])
            cylinder(h = body_h + 30, d = cable_d[k], $fn = 32);
} else {
    body_parts(layout_spread);
    translate([flange_outer_r + layout_spread + part_spacing + af / 2 / cos(30), 0, 0]) nut();
}
