import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.objects import WheelDrum
import gdsCAD as cad

chipsize = 50
chip = Base_Chip('wheel_drum', chipsize, chipsize,label=False)
d = WheelDrum(base_layer = 1,
					sacrificial_layer = 2 ,
					top_layer = 3,
					electrode_radius = 6,
					name = 'drum')
chip.add_component(d, (0,0))
chip.save_to_gds(show=False, save=True,loc='')