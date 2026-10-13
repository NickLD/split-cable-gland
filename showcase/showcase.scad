// Scenes for the listing images. Rendered by showcase/render.py; gland
// parameters come in with -D like any customizer setting.
use <../cable_gland.scad>

scene = "hero";      // hero, exploded, body, segment, slide, nut, plate
lift = 10;           // slide: how far the second half is still above the first
explode = 8;         // exploded: how far the segments move out
seg_pick = 1;        // segment: which one

pal = ["#FF7A1A", "#19A7A0", "#F4C430", "#8E5BD9", "#E84A5F", "#3FA34D", "#2D7DD2", "#F28C28"];
cable_cols = ["#202124", "#C0392B", "#2459A8", "#E6E6E6", "#2E7D32", "#F9A825", "#6A1B9A", "#202124"];
nut_col = "#AEB6BF";

echo(str("Thread: M", thread_size(), " "));

function mid_angle(k) = let (a = split_angles(), n = len(a))
    (a[k] + (k < n - 1 ? a[k + 1] : a[0] + 360)) / 2;

module segments(e = 0)
    for (k = [0:n_segments() - 1])
        color(pal[k % 8]) translate(e * [cos(mid_angle(k)), sin(mid_angle(k)), 0]) segment(k);

module cables(below = 22, above = 28) {
    p = cable_positions();
    d = cable_diameters();
    for (k = [0:len(p) - 1])
        color(cable_cols[k % 8]) translate([p[k][0], p[k][1], -below]) {
            cylinder(h = body_height() + below + above, d = d[k], $fn = 48);
            // stripped end: copper conductors poking out of the jacket
            color("#C47A3A") translate([0, 0, body_height() + below + above - 0.01])
                cylinder(h = 3, d = d[k] * 0.45, $fn = 24);
        }
}

// Panel the gland is mounted in, with a quarter cut away (cut_at = where the
// gap faces) so the flange underneath shows
cut_at = 300;
module panel(t = 3) {
    r = max(flange_radius(), nut_across_flats() / 2 / cos(30)) + 10;
    color("#59646F") translate([0, 0, flange_thickness()]) difference() {
        cylinder(h = t, r = r, $fn = 160);
        translate([0, 0, -1]) cylinder(h = t + 2, d = panel_drill(), $fn = 96);
        rotate([0, 0, cut_at - 45]) translate([0, 0, -1]) cube([r + 1, r + 1, t + 2]);
    }
}

if (scene == "hero") {
    segments();
    panel();
    color(nut_col) translate([0, 0, flange_thickness() + 3]) nut();
    cables(below = 12, above = 16);
} else if (scene == "exploded") {
    segments(explode);
    color(nut_col) translate([0, 0, body_height() + 14]) nut();
} else if (scene == "body") {
    segments();
    cables(below = 10, above = 14);
} else if (scene == "segment") {
    color(pal[seg_pick % 8]) segment(seg_pick);
} else if (scene == "slide") {
    // two halves part way through sliding together: the keys show where they overlap
    color(pal[0]) segment(0);
    color(pal[1]) translate([0, 0, lift]) segment(1);
} else if (scene == "nut") {
    color(nut_col) nut();
} else if (scene == "plate") {
    s = print_spread();
    segments(s);
    color(nut_col) translate([flange_radius() + s + 6 + nut_across_flats() / 2 / cos(30), 0, 0]) nut();
}
