import cadquery as cq


res = (cq.Workplane("XY")
       .tag("bot")
       .box(120, 20, 15)
       .edges()
       .fillet(1)
       .workplaneFromTagged("bot")
       .transformed(offset=(-15 + 30, -5 + 8, 0))
       .rarray(80, 1, 2, 1)
       .circle(3/2)
       .cutThruAll()
       )

cutout = (cq.Workplane("XY")
         .tag("bot")
         .box(120, 20, 15)
         )

res = res - cutout.translate((5, 5, 10))
res = res - cutout.translate((5, 5, -10))

res = (res
       .workplaneFromTagged("bot")
       .transformed(offset=(-55, -5, 2.5))
       .circle(1)
       .cutBlind(5))
res = (res
       .workplaneFromTagged("bot")
       .transformed(offset=(-55, -5, -7.5))
       .circle(1)
       .cutBlind(5))

show_object(res)
