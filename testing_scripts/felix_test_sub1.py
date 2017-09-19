import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_ald_array import Junctionchip
from source_dev.squid_ald_array import SQUIDchip

### Define DC part
dict_pads = {'width': 200, 'length': 300, 'spacing': 100, 'triheight': 100}

dict_junctions = [{'width': 3, 'jjmin': 1, 'jjmax': 7, 'jjstep': 1, 'location': 'n'},
                {'width': 4, 'jjmin': 1, 'jjmax': 7, 'jjstep': 1, 'location': 'w'},
                {'width': 3, 'jjmin': 7, 'jjmax': 13, 'jjstep': 1, 'location': 'e'},
                {'width': 4, 'jjmin': 7, 'jjmax': 13, 'jjstep': 1, 'location': 's'}]

smallchip = 5e3
name_jj = 'JJ'
jjs = [Junctionchip(name_jj,dict_pads,x) for x in dict_junctions]
[x.gen_junctions() for x in jjs]
chipjj = [Base_Chip(name_jj,xdim=smallchip,ydim=smallchip,frame=False,label=False,labelloc=(-500,2250)) for i in range(2)]

name_squid = 'SQUID'
squids = [SQUIDchip(name_squid,dict_pads,x) for x in dict_junctions]
[x.gen_junctions(dim=(50,50)) for x in squids]
chipsquid = [Base_Chip(name_squid,xdim=smallchip,ydim=smallchip,frame=False,label=False,labelloc=(-500,2250)) for i in range(2)]


for i in range(2):
    for jj,squid in zip(jjs,squids):
        chipjj[i].add_component(jj.cell,(0,0))
        chipsquid[i].add_component(squid.cell,(0,0))
for chip in [chipjj[0],chipjj[1],chipsquid[0],chipsquid[1]]:
    chip.add_bond_testpads(pos=(-1.8e3,-1.8e3))
    chip.add_ebpg_marker((-2e3,-1.5e3))
    chip.add_photolitho_marker()
    chip.add_photolitho_vernier(pos=(-300,-400))
    

chippos = [(-2.5e3,2.5e3),(-2.5e3,-2.5e3),(2.5e3,2.5e3),(2.5e3,-2.5e3)]
chip_sub1 = Base_Chip('felix_test_sub1',xdim=10e3,ydim=10e3,labelloc=(-600,4500))
for chipi,pos in zip([chipjj[0], chipsquid[0], chipjj[1], chipsquid[1]], chippos):
    chip_sub1.add(chipi,(pos[0],pos[1]))
chip_sub1.add_photolitho_marker()
chip_sub1.add_photolitho_vernier(pos=(-300,-400))
chip_sub1.save_to_gds(show = False, save = True)
