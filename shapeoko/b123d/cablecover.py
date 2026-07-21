from build123d import *
from ocp_vscode import *
from epilogue import *

w = 30
h = 25
case_th = 3.2
flange_th = 2
flange_w = 2
total_th = case_th + 2*flange_th
motor_cd = 3.5
limit_w, limit_h = 2, 3.5
rod_d1 = 1.8
rod_d2 = 1.5

bottom = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as p:
    # inner flange
    with BuildSketch():
        RectangleRounded(w + 2*flange_w, h + 2*flange_w, flange_th)
    extrude(amount=flange_th)
    # middle part
    with BuildSketch(p.faces().sort_by(Axis.Z).last):
        RectangleRounded(w, h, 2)
    extrude(amount=case_th)
    # outer flange
    with BuildSketch(p.faces().sort_by(Axis.Z).last):
        RectangleRounded(w + 2*flange_w, h + 2*flange_w, flange_th)
    extrude(amount=flange_th)
    filletsz(p, 0, 1.5)
    # holes, stepper
    with BuildSketch():
        with Locations((0, 2.5)):
            with GridLocations(w/2, 7.5, 2, 2):
                Circle(radius=motor_cd/2)
    extrude(amount=total_th, mode=Mode.SUBTRACT)
    # holes, limit/probe
    with BuildSketch():
        with Locations((0, -8)):
            with GridLocations(5.25, 1, 4, 1):
                RectangleRounded(limit_w, limit_h, .99)
    extrude(amount=total_th, mode=Mode.SUBTRACT)
    # rods
    with BuildSketch(Plane.XZ.offset(-h/2)):
        with Locations((0, total_th/2)):
            with GridLocations(w-7.5, 1, 2, 1):
                Circle(radius=rod_d1/2)
    extrude(amount=h-5, mode=Mode.SUBTRACT)
    with BuildSketch(Plane.XZ.offset(h/2)):
        with Locations((0, total_th/2)):
            with GridLocations(w-7.5, 1, 2, 1):
                Circle(radius=rod_d2/2)
    extrude(amount=-5, mode=Mode.SUBTRACT)
    
    
    split(bisect_by=Plane.XZ.offset(-(h/2+flange_w)+8.25), keep=Keep.BOTH)
    split(bisect_by=Plane.XZ.offset(-(h/2+flange_w)+8.25+7.5), keep=Keep.BOTH)
    split(bisect_by=Plane.XZ.offset(-(h/2+flange_w)+8.25+7.5+6), keep=Keep.BOTH)
    
epilogue(p)
