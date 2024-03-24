import cadquery as cq
import math

depth = 12
vise_d = 30.5
vise_h = 20
total_d = 50
height = 3
d2 = 10.5
bracket_th = 3
bracket_h = 15
toein = 0.8

c = math.sin(math.pi/4)*total_d

result = (cq.Workplane("XY")
          .moveTo(vise_d, 0).hLine(total_d - vise_d)
          .threePointArc((c, c), (0, total_d))
          .vLine(-(total_d - vise_h))
          .hLine(vise_d)
          .close()
          .extrude(depth)
          .edges("|Z")
          .fillet(1)
          .faces("<Z")
          .transformed(rotate=(90, 90, 0), offset=(20, vise_h + 10, depth/2))
          .tag("o")
          .circle(8.5/2)
          .cutBlind(total_d)
          .workplaneFromTagged("o")
          .circle(4.5/2)
          .cutThruAll()
)

show_object(result)

