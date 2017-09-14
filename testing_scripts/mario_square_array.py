import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.utilities import xor_polygons,shapely_to_poly,poly_to_shapely,join_polygons
import shapely
import gdsCAD as cad


chipsize = 25e3
square_size = 250
dx = 2.5e3
dy = dx
x_i = -11.5e3
y_i = x_i
N = 10
chip = Base_Chip('squares', chipsize, chipsize,label=False)


for i in range(N):
  for j in range(N):
    x = x_i+i*dx
    y = y_i+j*dy
    points=[(x,y), (x+square_size,y), (x+square_size,y+square_size), (x,y+square_size)]
    chip.add(cad.core.Boundary(points))

chip.save_to_gds(show=True, save=True,loc='')