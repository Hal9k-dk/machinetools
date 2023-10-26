include <../box.scad>

th = 3;

box(width = 189, height = 80.5, depth = 350-th-0.5, thickness = th, open = true,
    dividers = [ 2, 0 ],
    finger_cutout_radius = 15,
    finger_cutout_offset = 5,
    airgap_radius = 5,
    airgap_width = 50,
    spacing = 1,
    assemble = false, labels = true, explode = 0);

