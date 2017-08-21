import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_ald_array import Junctionchip
from source_dev.squid_ald_array import SQUIDchip

### Define DC part
dict_pads = {'width': 200,
            'length': 300,
            'spacing': 100,
            'triheight': 100}

dict_junctions = [{'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1},
                {'width': 5,
                'jjmin': 7,
                'jjmax': 13,
                'jjstep': 1}]

dict_squids = [{'width': 5,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1},
                {'width': 5,
                'jjmin': 7,
                'jjmax': 13,
                'jjstep': 1}]

smallchip = 5e3
name_jj = 'JJ'
jjs = [Junctionchip(name_jj,dict_pads,dict_junctions[i]) for i in range(2)]
[jjs[i].gen_junctions() for i in range(2)]
chipjj = [Base_Chip(name_jj,xdim=smallchip,ydim=smallchip,frame=False,label=False,labelloc=(-500,2250)) for i in range(2)]

name_squid = 'SQUID'
squids = [SQUIDchip(name_squid,dict_pads,dict_squids[i]) for i in range(2)]
[squids[i].gen_junctions() for i in range(2)]
chipsquid = [Base_Chip(name_squid,xdim=smallchip,ydim=smallchip,frame=False,label=False,labelloc=(-500,2250)) for i in range(2)]

for i in range(2):
	for chipi,group in zip([chipjj[i],chipsquid[i]],[jjs[i],squids[i]]):
		chipi.add_component(group.cell,(0,0))
		chipi.add_bond_testpads(pos=(-1.8e3,-1.8e3))
		chipi.add_ebpg_marker((-2e3,-1.5e3))	
		chipi.add_photolitho_marker()
		chipi.add_photolitho_vernier()

chippos = [(-2.5e3,2.5e3),(-2.5e3,-2.5e3),(2.5e3,2.5e3),(2.5e3,-2.5e3)]
chip_sub1 = Base_Chip('felix_test_sub1',xdim=10e3,ydim=10e3,labelloc=(-600,4500))
for chipi,pos in zip([chipjj[0], chipsquid[0], chipjj[1], chipsquid[1]], chippos):
    chip.add_component(chipi.cell,(pos[0],pos[1]))

chip_sub1.save_to_gds(show = False, save = True)
