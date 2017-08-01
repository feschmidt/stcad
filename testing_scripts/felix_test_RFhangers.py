import numpy as np
import gdsCAD as cad
from source_dev.chip import Base_Chip
import source_dev.junction_ald_array as junction_array
import source_dev.squid_ald_array as squid_array
import source_dev.rfcavities_hangers as cavities

dict_hangers = {'length': 4000,
            'couplinglength': 600,
            'centerwidth': 4,
            'gapwidth': 20}
                

name = 'hangers'
rfhangers = cavities.HangerCavity(name,dict_hangers)
rfhangers.gen_full()

chipsize = 10e3
chip = Base_Chip(name,chipsize,chipsize)
chip.add_component(rfhangers.cell,(0,0))
chip.add_ebpg_marker((-3.3e3,-1.5e3))
#chip.add_TUlogo()
chip.save_to_gds(show = True, save = True)

