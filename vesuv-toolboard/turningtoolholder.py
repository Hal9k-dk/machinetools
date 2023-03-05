import cadquery as cq

tool_side = 16.5
tool_dia = 12.5
depth = 30
height = 30
bracket_th = 4
tool_cc = 35
nof_square_tools = 4
nof_round_tools = 1
w = (nof_square_tools + nof_round_tools)*tool_cc

result = (cq.Workplane("XY")
          .box(w, depth, height, centered=(True, True, False))
          .faces("<Z").workplane(centerOption="CenterOfMass", 
                             invert=True).tag("bottom")
          .workplaneFromTagged("bottom")
          # mount plate
          .workplaneFromTagged("bottom")
          .transformed(offset=(0, (depth-bracket_th)/2, -depth))
          .box(w, bracket_th, height, centered=(True, True, False))
          # round edges
          .edges("|Y or <Y").fillet(1)
          # tool holes
          .workplaneFromTagged("bottom")
          .transformed(offset=(tool_cc/2, -4, 0))
          .rarray(tool_cc, 1, nof_square_tools, 1)
          .rect(tool_side, tool_side).cutThruAll()
          .workplaneFromTagged("bottom")
          .transformed(offset=(-tool_cc*2, -depth/6, 0))
          .circle(tool_dia/2).cutThruAll()
          .workplaneFromTagged("bottom")
          # mounting holes
          .workplaneFromTagged("bottom")
          .transformed(offset=(0, 0, -height/2), rotate=(90, 0, 0))
          .rarray((nof_square_tools - 1)*tool_cc, 1, 2, 1)
          .circle(2)
          .cutThruAll()
)

show_object(result)

