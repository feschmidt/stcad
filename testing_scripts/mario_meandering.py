import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
from stcad.source_dev.drums import *

# chipsize = 700
# chip = Base_Chip('line_and_drum', chipsize, chipsize,label=False)
# drum = circ_gap_drum(drum_size=30,tether_width=4,number_of_tethers=10)
# mender_and_drum = MeanderAndSuspendedDrum(drum,
#         meander_layer = 1,
#         n_legs = 19, 
#         cond_spacing = 10., 
#         meander_length = 300.,
#         cable_width=1, 
#         bend_radius = 1.,
#         meander_to_ground = 200.,
#         label = "test",
#         drumhead_radius = 10,
#         name = "test")
# chip.add_component(mender_and_drum, (0,0))
# chip.save_to_gds(show=True, save=False,loc='')

chipsize = 700
chip = Base_Chip('line_and_drum', chipsize, chipsize,label=False)
drum = circ_gap_drum(drum_size=30,tether_width=4,number_of_tethers=10)
mender_and_drum = MeanderAndSuspendedDrum(drum,
        meander_layer = 1,
        n_legs = 20, 
        cond_spacing = 10., 
        meander_length = 300.,
        cable_width=1, 
        bend_radius = 1.,
        meander_to_ground = 200.,
        label = "test",
        drumhead_radius = 10,
        name = "test")
chip.add_component(mender_and_drum, (0,0))
chip.save_to_gds(show=True, save=False,loc='')

# chipsize = 250
# chip = Base_Chip('line', chipsize, chipsize,label=False)
# cp = MeanderingLine()
# chip.add_component(cp, (0,0))
# chip.save_to_gds(show=True, save=False,loc='')

