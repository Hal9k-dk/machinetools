import cadquery as cq

w = 155
depth = 20
height = 10
bracket_th = 4
d1 = 11.5
d2 = 15
d3 = 7
factor = 0.8
mh_cc = 100
w_offset = -40
w1_offset = w_offset - 80/3
w2_offset = w_offset + 80/3
h1_offset = 80 + w2_offset
log(w1_offset)
log(w2_offset)
log(h1_offset)
h1_dia = 5
h1_dist = 10

result = (cq.Workplane("XY")
          .box(w, depth, height, centered=(True, True, False))
          .faces("<Z").workplane(centerOption="CenterOfMass", 
                             invert=True).tag("bottom")
          .workplaneFromTagged("bottom")
          # mount plate
          .workplaneFromTagged("bottom")
          .transformed(offset=(0, (depth-bracket_th)/2, -height))
          .box(w, bracket_th, height, centered=(True, True, False))
          # round edges
          .edges("|Y or <Y").fillet(1)
          # hex key
          .workplaneFromTagged("bottom")
          .transformed(offset=(h1_offset, depth/2 - bracket_th - h1_dist, 0))
          .circle(h1_dia/2).cutThruAll()
          # large wrench
          .workplaneFromTagged("bottom")
          .transformed(offset=(w1_offset, -depth/6, 0))
          .slot2D(d1, d3).cutThruAll()
          # small wrench
          .workplaneFromTagged("bottom")
          .transformed(offset=(w2_offset, -depth/6, 0))
          .slot2D(d2, d3).cutThruAll()
          # cut through
          .workplaneFromTagged("bottom")
          .transformed(offset=(w1_offset, -8, 0))
          .rect(d1*factor, 7).cutThruAll()
          .workplaneFromTagged("bottom")
          .transformed(offset=(w2_offset, -8, 0))
          .rect(d2*factor, 7).cutThruAll()
          # mounting holes
          .workplaneFromTagged("bottom")
          .transformed(offset=(0, 0, -height/2), rotate=(90, 0, 0))
          .rarray(mh_cc, 1, 2, 1)
          .circle(2)
          .cutThruAll()
)

show_object(result)

