import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.objects import SpiralInductor
import gdsCAD as cad
from numpy import tan, pi, sqrt
from scipy.constants import e,h,hbar,epsilon_0

chipsize = 200
chip = Base_Chip('inductor', chipsize, chipsize,label=False)
inductor = SpiralInductor(exterior = 50,coil_number = 45)

chip.add_component(inductor, (0,0))
chip.save_to_gds(show=False, save=False,loc='')