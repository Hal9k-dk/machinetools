import cadquery as cq

tool_side = 21.5
depth = 40
height = 20
bracket_th = 4
tool_cc = 35
nof_square_tools = 1
w = (nof_square_tools + 0.5)*tool_cc

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
          .transformed(offset=(tool_cc*0, -4, 0))
          #.rarray(tool_cc, 1, nof_square_tools, 1)
          .rect(tool_side, tool_side).cutThruAll()
          # mounting holes
          .workplaneFromTagged("bottom")
          .transformed(offset=(0, 0, -height/2), rotate=(90, 0, 0))
          .rarray(tool_cc, 1, 2, 1)
          .circle(2)
          .cutThruAll()
)

show_object(result)

