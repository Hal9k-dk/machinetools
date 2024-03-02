import cadquery as cq

w = 80
depth = 20
height = 10
bracket_th = 4
d1 = 11.5
d2 = 15
factor = 0.7

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
          # tool holes
          .workplaneFromTagged("bottom")
          .transformed(offset=(-w/3, -depth/6, 0))
          .slot2D(d1, 6).cutBlind(25)
          .workplaneFromTagged("bottom")
          .transformed(offset=(w/3, -depth/6, 0))
          .slot2D(d2, 6).cutThruAll()
          .workplaneFromTagged("bottom")
          .transformed(offset=(-w/3, -8, 0))
          .rect(d1*factor, 7).cutThruAll()
          .workplaneFromTagged("bottom")
          .transformed(offset=(w/3, -8, 0))
          .rect(d2*factor, 7).cutThruAll()
          .workplaneFromTagged("bottom")
          .transformed(offset=(0, 0, -height/2), rotate=(90, 0, 0))
          .rarray(w*0.5, 1, 2, 1)
          .circle(2)
          .cutThruAll()
)

show_object(result)

