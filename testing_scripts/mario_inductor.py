import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.objects import SpiralInductor
import gdsCAD as cad
from numpy import tan, pi, sqrt
from scipy.constants import e,h,hbar,epsilon_0

chipsize = 200
chip = Base_Chip('inductor', chipsize, chipsize,label=False)
inductor = SpiralInductor( 
        exterior = 70.,
        coil_number = 20,
        line_width = 0.5,
        spacing = 1,kinetic_inductance = 0.)

print(inductor.Lg*1e9+inductor.Lk*1e9)
print(inductor.C)
print(inductor.self_resonance/1e9)
print(inductor.length)
inductor.show()


# chip.add_component(inductor, (0,0))
# chip.save_to_gds(show=False, save=False,loc='')