import numpy as np
from source_dev.chip import Base_Chip
import funcs.junction_ald_array as junction_array
"""
For junctiontest layer 14,20,21 reserved
"""
dict_pads = {'width': 200,
            'length': 300,
            'spacing': 300,
            'triheight': 100}

dict_junctions = {'width': 20,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}

name = 'testjunctions'

testf = junction_array.Junctionchip(name,dict_pads,dict_junctions, x0 = -100,
        y0 = -2200, tlength = 1600, chipsize = 6000)
testf.gen_junctions(marker = False, vernier = False, testpads = True)

chip = Base_Chip(name,6000,6000)
chip.add_component(testf.cell,(3000,3000))
chip.add_photolitho_marker()
chip.add_photolitho_vernier()
chip.save_to_gds(show = True, save =False)

