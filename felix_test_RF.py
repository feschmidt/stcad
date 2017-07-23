import numpy as np
from source_dev.chip import Base_Chip
import source_dev.junction_ald_array as junction_array
import source_dev.squid_ald_array as squid_array
import source_dev.rfcavities_dcbias as cavities

dict_cavity = {'length': 6900,
            'centerwidth': 10,
            'gapwidth': 6.2,
            'shunts': 2,
            'startx0': 4400,
            'holedim': (80,100),
            'holemarker': True}

                

name = 'testcavities'
testf = cavities.ShuntCavity(name,dict_cavity)
testf.gen_cavities()
testf.gen_full()

chipsize = 10e3
chip = Base_Chip(name,chipsize,chipsize)
chip.add_component(testf.cell,(0,0))
chip.add_ebpg_marker((1690,6560))
#chip.add_TUlogo()
chip.save_to_gds(show = True, save = True)
