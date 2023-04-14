import cadquery as cq

w = 15
depth = 10
height = 3
d2 = depth
bracket_th = 3
bracket_h = 5

result = (cq.Workplane("XY")
          .box(w, depth, height, centered=(True, True, False))
          .circle(3.5/2)
          .cutThruAll()
          .faces("<Y").workplane(centerOption="CenterOfMass").tag("side")
          .workplaneFromTagged("side")
          .transformed(offset=(-w/2, -bracket_th/2, -depth))
          .vLine(bracket_th)
          #.hLine(bracket_h)
          .threePointArc((-d2/2, bracket_th+d2/2), (0, d2+bracket_th))
          .hLine(bracket_h)
          .vLine(bracket_th)
          .hLine(-bracket_h)
          .threePointArc((-d2/2-bracket_th, bracket_th+d2/2), (0, 0))
          .close()
          .extrude(depth)
          .faces(">Y or <Y or >X")
          .fillet(.95)
)

show_object(result)

