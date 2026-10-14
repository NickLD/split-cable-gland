# Customizable Split Cable Gland
[![Open in OpenSCAD Customizer](https://img.shields.io/badge/Open%20in-OpenSCAD%20Customizer-f9d72c)](https://openscad.app/#/gh/NickLD/split-cable-gland/cable_gland.scad)

A split, threaded cable gland you can size for your own cables. Close the body around one or more cables, push it through a hole in your panel, and screw the nut down. The split body clamps the cables and the nut locks the whole thing in place.

Remix of [Locking Threaded 4mm Cable Pass Through Grommet](https://www.printables.com/model/1151107-locking-threaded-4mm-cable-pass-through-grommet) by **zuberio** (CC BY 4.0), redesigned from scratch in OpenSCAD so every dimension can be changed.

## Features

- **1 to 8 cables**, each with its own diameter
- **Radial or inline** hole layouts, spaced automatically (or set the spacing yourself)
- **Your dimensions, or auto-fit:** set the thread, flange and nut sizes yourself, or leave them at 0 and they are sized to fit the cables
- **Arc keys** run the full height of the threaded body and lock the segments together
- **Prints flat with no supports.** The thread uses 45 degree flanks with flats at the crest and root, so nothing overhangs more than 45 degrees
- **Drill size on the nut:** the panel hole is engraved on top in mm, with the nearest imperial drill
- Warnings in the preview if a setting won't work (walls too thin, keys that don't fit, nut too small to cover the hole, and so on)

## Using the Customizer

1. Set **cable_count** and each **cable_N_d** (the outer diameter of each cable, in mm).
2. Pick **cable_layout**: radial (around the centre) or inline (in a row).
3. Leave **thread_d**, **flange_d** and **nut_af** at **0** to auto-size, or enter your own.
4. Set **thread_length** to about your panel thickness + nut height + 2 mm.
5. Check the preview for red warning text, then set **show_notes = false** before you export. The notes are real geometry and would print otherwise.

Useful extras:
- **hole_clearance:** extra hole diameter over the cable (default 0.3 mm)
- **hole_taper:** optional taper that grips the cable tighter near the flange (off by default; it can stop the halves closing on stiff cable)
- **key_clearance** (0.1 mm) and **nut_clearance** (0.15 mm): loosen these in 0.05 mm steps if your printer fits tight
- **bottom_chamfer:** 0 by default so thin parts stick to the bed. Raise it to 0.2-0.4 mm if elephant's foot stops the halves closing

## Ready-made STLs

Each STL is a full print plate (split body + nut), sized automatically. The file name tells you the thread size and the panel drill:

`cable_gland_<cables>_M<thread>_drill<hole>mm.stl`

1 cable: 3, 4, 5, 6, 8, 10 mm · 2 cables: 4, 5, 6 mm · 3 cables: 4, 5 mm · 4 cables: 4 mm

For other sizes, open the .scad in OpenSCAD (free) and use its Customizer panel.

## Printing

- PLA, PETG or ASA all work. PETG or ASA for outdoor use.
- 0.2 mm layers, 3+ walls, 15-25% infill. No supports, no brim needed.
- Print as laid out: every part sits flat on the bed.
- Turn on your slicer's elephant foot compensation (or raise bottom_chamfer) if the halves are hard to close.

## Assembly

1. Drill the panel to the size engraved on the nut.
2. Put the segments around the cables and slide them together along the cables. The arc keys only go together that way.
3. Push the body through the panel from one side and screw the nut on from the other.

## License

CC BY 4.0. Based on the design by zuberio. Credit both if you remix it.

## Customize it in your browser

[![Open in OpenSCAD Customizer](https://img.shields.io/badge/Open%20in-OpenSCAD%20Customizer-f9d72c)](https://openscad.app/#/gh/NickLD/split-cable-gland)
