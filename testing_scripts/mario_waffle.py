import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
import shapely
import gdsCAD as cad



chipsize = 200
chip = Base_Chip('waffle', chipsize, chipsize,label=False)

base_width = 150
base_lead_length = 12
base_line_width = 2
ground_length = 5
n_holes = 13
base_hole_diameter = 3
sacrificial_width_overlap = 0.5
side_support = 4
release_hole_diameter = 1

waffle = WaffleCapacitor(base_width, 
        base_lead_length, 
        base_line_width, 
        ground_length, 
        n_holes, 
        base_hole_diameter, 
        sacrificial_width_overlap, 
        side_support, 
        release_hole_diameter, 
        base_layer =1, 
        base_hole_layer =4, 
        sacrificial_layer =2, 
        sacrificial_hole_layer =5, 
        top_layer =3, 
        top_hole_layer =6,
        ground = True)
print(waffle.capacitance(gap=50e-9))
chip.add(waffle)
chip.save_to_gds(show=False, save=True,loc='')