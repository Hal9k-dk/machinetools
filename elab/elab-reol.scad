include <../box.scad>

th = 3;

box(width = 195, height = 350, depth = 170, thickness = th, open = true,
    dividers = [ 1, 0 ],
    assemble = false, labels = true, explode = 0);

