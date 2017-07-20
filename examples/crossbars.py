import numpy as np
from gdsCAD import *

length = 50
spacing = np.array([75, 75])

def xbar(w1, w2):
    cell = core.Cell('XBAR')
    xstrip = shapes.Rectangle((0,0), (length, w1))
    ystrip = shapes.Rectangle((0,0), (w2, length), layer=2)

    N = int(length/(2*w1))
    for i in range(N):
        d = (0, i*w1*2)
        cell.add(utils.translate(xstrip, d))

    N = int(length/(2*w2))
    for i in range(N):
        d = (i*w2*2, 0)
        cell.add(utils.translate(ystrip, d))

    return cell

grid = core.Cell('GRID')
w_vals = [1, 2, 3, 5]

for (i, bottom) in enumerate(w_vals):
    for (j, top) in enumerate(w_vals):
        grid.add(xbar(bottom, top), origin = np.array([i,j])*spacing)

grid.show()