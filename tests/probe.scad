// Geometry probes used by run_tests.py. Each probe renders something that
// should be empty (no collision / no material) or non-empty, depending on the
// test. Model parameters are overridden with -D on the command line.
use <../cable_gland.scad>

probe = "pair";
seg_a = 0; seg_b = 1;
dx = 0; dy = 0; dz = 0;
nut_z = 4; nut_rot = 0;
ring_z = 3; ring_d = 4;

if (probe == "pair")                 // two segments overlap?
    intersection() { segment(seg_a); segment(seg_b); }
else if (probe == "pair_moved")      // overlap after moving segment b
    intersection() { segment(seg_a); translate([dx, dy, dz]) segment(seg_b); }
else if (probe == "key_outside_wedge")   // anything of the segment outside its own wedge (= key tab)
    difference() { segment(seg_a); wedge(seg_a0(seg_a), seg_a1(seg_a)); }
else if (probe == "nut_on_body")     // nut thread vs body thread
    intersection() { body_whole(); translate([0, 0, nut_z]) rotate([0, 0, nut_rot]) nut(); }
else if (probe == "hole_ring")       // body material inside a disc of ring_d at ring_z
    intersection() { body_whole(); translate([0, 0, ring_z]) cylinder(h = 0.2, d = ring_d, $fn = 96); }
else if (probe == "thread_ring")     // body material outside ring_d at ring_z
    intersection() {
        body_whole();
        translate([0, 0, ring_z]) difference() {
            cylinder(h = 0.2, d = 100);
            translate([0, 0, -1]) cylinder(h = 2, d = ring_d, $fn = 192);
        }
    }

// Generic box probe: body material inside [bx..bx+sx] x [by..by+sy] x [bz..bz+sz]
bx = 0; by = 0; bz = 0; sx = 1; sy = 1; sz = 1;
// Simulated elephant's foot: bottom 0.2 mm of segment b grown outward by `foot`
foot = 0.15;

if (probe == "box")
    intersection() { body_whole(); translate([bx, by, bz]) cube([sx, sy, sz]); }
else if (probe == "foot_pair")
    intersection() {
        segment(seg_a);
        union() {
            segment(seg_b);
            linear_extrude(height = 0.2) offset(delta = foot)
                projection(cut = true) translate([0, 0, -0.1]) segment(seg_b);
        }
    }
else if (probe == "key_box")         // parts of segment a outside its wedge (key tabs) inside the box
    intersection() {
        difference() { segment(seg_a); wedge(seg_a0(seg_a), seg_a1(seg_a)); }
        translate([bx, by, bz]) cube([sx, sy, sz]);
    }

// Plastic of all segments (keys and slots included) in the ring ring_d..ring_d2 at ring_z
ring_d2 = 6;
if (probe == "wall_ring")
    intersection() {
        union() for (k = [0:n_segments() - 1]) segment(k);
        translate([0, 0, ring_z]) difference() {
            cylinder(h = 0.2, d = ring_d2, $fn = 192);
            translate([0, 0, -1]) cylinder(h = 2, d = ring_d, $fn = 192);
        }
    }
