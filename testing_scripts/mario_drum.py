import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.objects import Drum
import gdsCAD as cad

chipsize = 50
chip = Base_Chip('drum', chipsize, chipsize,label=False)
inductor = Drum(base_layer = 1,
					sacrificial_layer = 2 ,
					top_layer = 3,
					outer_radius = 9,
					head_radius = 7,
					electrode_radius = 6,
					cable_width = 0.5,
					sacrificial_tail_width = 3,
					sacrificial_tail_length = 3,
					opening_width = 4,
					N_holes = 3,
					hole_angle = 45,
					hole_distance_to_center = 4.5,
					hole_distance_to_edge = 0.5,
					name = '')
chip.add_component(inductor, (0,0))
chip.save_to_gds(show=False, save=True,loc='')