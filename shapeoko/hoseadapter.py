import cadquery as cq

od1 = 31 # dust shoe hole ID
od2 = 25.7 # hose ID
len1 = 30
len2 = 30
id = 23

res = (cq.Workplane("XY")
       .circle(od1/2)
       .extrude(len1)
       .faces(">Z")
       .fillet(3)
       .faces(">Z")
       .circle(od2/2)
       .extrude(len2)
       .faces(">Z")
       .fillet(1)
       .circle(id/2)
       .cutThruAll()
      )

show_object(res)
