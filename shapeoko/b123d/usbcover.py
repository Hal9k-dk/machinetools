from build123d import *
from ocp_vscode import *
from epilogue import *

w = 15.5
h = 14
th = 3.5
flange_th = 2
flange_w = 2
plug_w = 12
plug_h = 6.5

bottom = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as p:
    # inner part
    with BuildSketch():
        RectangleRounded(w, h, 1)
    extrude(amount=th)
    # flange
    with BuildSketch(p.faces().sort_by(Axis.Z).last):
        RectangleRounded(w + 2*flange_w, h + 2*flange_w, 2)
    extrude(amount=flange_th)
    filletsz(p, -1, 1.5)
    # plug hole
    with BuildSketch():
        with Locations((-(w-plug_w)/2, (h-plug_h)/2)):
            RectangleRounded(plug_w, plug_h, plug_h*0.49)
    extrude(amount=10, mode=Mode.SUBTRACT)
    
epilogue(p)
