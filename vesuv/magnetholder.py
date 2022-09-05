import cadquery as cq

res = (cq.Workplane("XY")
       .box(28, 175, 5, centered=(True, True, False))
       .edges("|Z")
       .fillet(1)
       .rarray(1, 65, 1, 3)
       .circle(15.55/2)
       .cutBlind(3.5)
        )

show_object(res)

