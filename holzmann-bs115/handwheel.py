import cadquery as cq
import math

outer_dia = 90

# create path
path = (cq.Workplane("XY" )
        .circle(90/2)
        )

outer_h = 12
outer_th = 20

# The outer wheel
outer_ring = (cq.Workplane("XZ")
              .transformed(offset=(outer_dia/2, outer_h/2, 0))
              .slot2D(outer_th, outer_h, 0).sweep(path)
              )

inner_dia = 38

# The inner hub
inner = (cq.Workplane("XY")
         .tag("bot")
         .circle(inner_dia/2)
         .extrude(24)
         .workplaneFromTagged("bot")
         .transformed(offset=(0, 0, 6))
         .circle(22.5/2)
         .cutBlind(18)
         .circle(16/2)
         .cutThruAll()
         )

# Radial arm (x 3)
factor = 0.3
def arm(a):
    return (cq.Workplane("XZ")
       .transformed(rotate=(0, a, 0))
       .transformed(offset=(0, outer_h/2, inner_dia*factor))
       .rect(20, outer_h)
       .extrude(outer_dia/2 - inner_dia*factor - outer_th*factor)
       .edges()
       .fillet(2)
       )

oa = 60 # angular offset
res = outer_ring + inner + arm(oa + 120) + arm(oa - 120) + arm(oa)

# Screw hole in the side
res = (res
       .workplaneFromTagged("bot")
       .transformed(rotate=(90, 0, 0))
       .transformed(offset=(0, 6+9.5, -10))
       .circle(8/2)
       .cutBlind(30)
       )

# Hole for handle
res = (res
       .workplaneFromTagged("bot")
       .transformed(offset=(0, outer_dia/2, 0))
       .circle(8.5/2)
       .cutThruAll()
       .workplaneFromTagged("bot")
       .transformed(offset=(0, outer_dia/2, outer_h/2))
       .polygon(6, 13, circumscribed=True)
       .cutBlind(6.5)
       )

show_object(res)

