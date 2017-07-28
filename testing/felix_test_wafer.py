import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_ald_array import Junctionchip
from source_dev.squid_ald_array import SQUIDchip
from source_dev.rfcavities_dcbias import ShuntCavity

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
                
dict_cavity = {'length': 6900,
            'centerwidth': 10,
            'gapwidth': 6.2,
            'shunts': 2,            # either 1 or 2. For future: extend to gap capacitors
            'leadlauncher': 100,    # should remain default like this
            'lead1': 1000,          # should remain default like this
            'holedim': (80,100),
            'holemarker': True}
                

name_jj = 'JJ test'
jjs = Junctionchip(name_jj,dict_pads,dict_junctions)
jjs.gen_junctions()
chipjj = Base_Chip(name_jj,xdim=6e3,ydim=6e3,frame=False)

name_squid = 'SQUID test'
squids = SQUIDchip(name_squid,dict_pads,dict_squids)
squids.gen_junctions(dim=(50,50))
chipsquid = Base_Chip(name_squid,xdim=6e3,ydim=6e3,frame=False)

name_cav = 'Shunt cavity'
cav = ShuntCavity(name_cav,dict_cavity)
cav.gen_full()
chipcav = Base_Chip(name_cav,xdim=10e3,ydim=10e3,frame=False)

for chipi,group in zip([chipjj, chipsquid, chipcav],[jjs,squids,cav]):
    chipi.add_component(group.cell,(0,0))
    chipi.add_photolitho_marker()
    chipi.add_photolitho_vernier()
    chipi.add_bond_testpads()
    chipi.add_ebpg_marker()

chip = Base_Chip('full_wafer',xdim=25000,ydim=25000,wafer=2)
for chipi,pos in zip([chipjj, chipsquid, chipcav],[(8e3,4e3),(1e3,-4e3),(-10e3,2e3)]):
    chip.add_component(chipi.cell,pos)
chip.add_dicing_marker(pos=(0,0))
#chip.add_TUlogo()
chip.save_to_gds(show = True, save = True)
