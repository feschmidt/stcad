import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.utilities import *
import shapely
import gdsCAD as cad


chipsize = 200
chip = Base_Chip('test', chipsize, chipsize,label=False)

layer_sacrificial_holes = 2
width = 150
chip.add(Hexagon(width = width,layer = 1))
margin = 10
n_width_holes = 7
hole_diameter = 4
if n_width_holes%2==0:
    raise ValueError("the width should contain an odd number of holes") 
half_height = np.sqrt(width**2/4.-width**2/16.)-margin
pitch = (width-2*margin)/(n_width_holes)
pitch_vertical = half_height/float((n_width_holes+1)/2-1)

for i in range((n_width_holes+1)/2):
	x_array = np.linspace(-(((n_width_holes+1)/2-1)*pitch-i*pitch/2.),((n_width_holes+1)/2-1)*pitch-i*pitch/2.,n_width_holes-i)
	y = i*pitch_vertical
	for x in x_array:
		chip.add(cad.shapes.Disk((x,y), hole_diameter,layer =layer_sacrificial_holes))
for i in range(1,(n_width_holes+1)/2):
	x_array = np.linspace(-(((n_width_holes+1)/2-1)*pitch-i*pitch/2.),((n_width_holes+1)/2-1)*pitch-i*pitch/2.,n_width_holes-i)
	y = -i*pitch_vertical
	for x in x_array:
		chip.add(cad.shapes.Disk((x,y), hole_diameter,layer =layer_sacrificial_holes))


chip.save_to_gds(show=True, save=False,loc='')