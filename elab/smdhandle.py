import cadquery as cq

# wedge dimensions
wd = 1.5
ww1 = 5
ww2 = 6

# block dimensions
bd = 5
bw = 15
bh = 10

# handle
hd = 17.5
hh = 5

# extrude part with slot
y1 = bw/2 - ww1/2
y2 = bw/2 - ww2/2
result = (cq.Workplane("XY")
          .tag("base")
          .hLine(bd)
          .vLine(bw)
          .hLine(-bd)
          .vLine(-y1)
          .lineTo(wd, bw - y2)
          .lineTo(wd, y2)
          .lineTo(0, y1)
          .close()
          .extrude(bh)
          )

# handle
x1 = hd - bw/2
handle = (cq.Workplane("XY")
          #.transformed(offset=(bd, 0, 0))
          .hLine(x1)
          .threePointArc((hd, bw/2), (x1, bw))
          .hLine(-x1)
          .close()
          .extrude(hh)
          )

dip_r = 10
dip_d = 2
dip = (cq.Workplane("XY")
       .transformed(offset=(x1, bw/2, dip_r + hh - dip_d))
       .sphere(dip_r)
       )

handle = handle - dip

result = result + handle.translate((bd, 0, 0))

result = (result
          .faces(">X")
          .fillet(1)
         )

show_object(result)
