import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.objects import SpiralInductor
import gdsCAD as cad
from numpy import tan, pi, sqrt
from scipy.constants import e,h,hbar,epsilon_0

chipsize = 200
chip = Base_Chip('inductor', chipsize, chipsize,label=False)
inductor = SpiralInductor(exterior = 50,coil_number = 45)
d = np.array([5,6,7,8,9,10,11,12])*1.e-6
R = d/2.
gap = 50e-9
C = epsilon_0*pi*R**2/gap
gap = 250e-9
C2 = epsilon_0*pi*R**2/gap
inductor.inductance()
for c in C2:
	inductor.resonance(c)
for c in C:
	inductor.resonance(c)
# chip.add_component(inductor, (0,0))
# chip.save_to_gds(show=False, save=False,loc='')