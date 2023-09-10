import cadquery as cq

SHAPEOKO = False
WOODMADS = True

w = 25
if SHAPEOKO:
    gs = 25.4*1.5  # grid spacing
elif WOODMADS:
    gs = 45
sd = 4 # depth of screw head hole
th = 19 # thickness
N = 3 # number of holes

def make_hole(o, x, y):
    return (o
            .workplaneFromTagged("bot")
            .transformed(offset=(w/2 + x*gs, w/2 + y*gs, 0))
            .tag("ref")
            .circle(6.2/2)
            .cutThruAll()
            .workplaneFromTagged("ref")
            .transformed(offset=(0, 0, th-sd))
            .circle(14/2)
            .cutBlind(sd)
            )

res = (cq.Workplane("XY")
       .tag("bot")
       .box((N - 1)*gs + w, w, th, centered=False)
       .edges(">Z or |Z")
       .fillet(2)
      )

for i in range(0, N):
    res = make_hole(res, i, 0)

show_object(res)
