import numpy as np
from gdsCAD import *

width = 2    # wire width
height = 40  # device width
width = 150  # device length (approx.)

def Heater(spacing):
    heater = core.Cell('HEATER')

    unit = np.array([[0,0], [0, height], [spacing/2., height], [spacing/2., 0]])

    N = int(np.floor(width/spacing))
    pts=unit
    for i in range(1,N):
        next_unit = unit + i * np.array([spacing, 0])
        pts = np.vstack((pts, next_unit))

    pts=np.vstack(([0,-10], pts, [spacing * N, 0], [spacing * N, height+10]))

    trace=core.Path(pts, width=2)
    heater.add(trace)

    pad = core.Cell('PAD')
    pad.add(shapes.Rectangle((-5,-5), (5,5)))
    pad.add(shapes.Rectangle((-2,-2), (2,2), layer=2))

    heater.add(pad, origin= (0, -10))
    heater.add(pad, origin=(spacing * N, height+10))

    return heater

top = core.Cell('TOP')
yPos = 0
for sp in [5, 10, 20, 30, 50]:
    htr = Heater(sp)
    bb = htr.bounding_box
    h = bb[1,1] - bb[0,1]
    top.add(htr, (0, yPos + h ))
    yPos += h

top.show()