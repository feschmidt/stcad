import numpy as np
from source_dev.chip import Base_Chip
import source_dev.junction_ald_array as junction_array
import source_dev.squid_ald_array as squid_array
"""
For junctiontest layer 14,20,21 reserved
"""
dict_pads = {'width': 200,
            'length': 300,
            'spacing': 300,
            'triheight': 100}

dict_junctions = {'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}

dict_squids = {'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}
                

name = 'testjunctions'
testf = junction_array.Junctionchip(name,dict_pads,dict_junctions)
testf.gen_junctions()
'''
name = 'testsquids'
testf = squid_array.Junctionchip(name,dict_pads,dict_squids)
testf.gen_junctions(dim=(50,50))
'''

chip = Base_Chip(name,6000,6000)
chip.add_component(testf.cell,(3000,3000))
chip.add_photolitho_marker()
chip.add_photolitho_vernier()
chip.add_bond_testpads()
chip.add_ebpg_marker()
chip.add_dicing_marker(pos=(3000,3000))
#chip.add_TUlogo()
chip.save_to_gds(show = True, save = True)
