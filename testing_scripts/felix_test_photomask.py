import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_ald_array import Junctionchip
from source_dev.squid_ald_array import SQUIDchip
from source_dev.rfcavities_dcbias import ShuntCavity
import source_dev.rf_feedlines as feedline
import source_dev.rf_hangers as hangers

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
name_jj = ['JJ test 1...7um', 'JJ test 8...15um']
jjs = [Junctionchip(name_jj[0],dict_pads,dict_junctions[0]), Junctionchip(name_jj[1],dict_pads,dict_junctions[1])]
[jjs[i].gen_junctions() for i in range(2)]
chipjj = [Base_Chip(name_jj[0],xdim=smallchip,ydim=smallchip,frame=True), Base_Chip(name_jj[1],xdim=smallchip,ydim=smallchip,frame=True)]

name_squid = ['JJ test 1...7um', 'JJ test 8...15um']
squids = [SQUIDchip(name_squid[0],dict_pads,dict_squids[0]), SQUIDchip(name_squid[1],dict_pads,dict_squids[1])]
[squids[i].gen_junctions() for i in range(2)]
chipsquid = [Base_Chip(name_squid[0],xdim=smallchip,ydim=smallchip,frame=True), Base_Chip(name_squid[1],xdim=smallchip,ydim=smallchip,frame=True)]

for i in range(2):
	for chipi,group in zip([chipjj[i],chipsquid[i]],[jjs[i],squids[i]]):
		chipi.add_component(group.cell,(0,0))
		chipi.add_bond_testpads(pos=(-1.8e3,-1.8e3))
		chipi.add_ebpg_marker((-2e3,-1.5e3))	
		chipi.add_photolitho_marker()
		chipi.add_photolitho_vernier()
		
		
### Define shunt cavity part                
dict_cavity = {'length': 6900,
            'centerwidth': 10,
            'gapwidth': 6.2,
            'shunts': 2,            # either 1 or 2. For future: extend to gap capacitors
            'leadlauncher': 100,    # should remain default like this
            'lead1': 1000,          # should remain default like this
            'holedim': (80,100),
            'holemarker': True}

name_cav = 'Shunt cavity'
cav = ShuntCavity(name_cav,dict_cavity)
cav.gen_full()
chipcav = Base_Chip(name_cav,xdim=10e3,ydim=10e3,frame=True)
chipcav.add_component(cav.cell,(-5e3,-5e3))
chipcav.add_ebpg_marker((-3.3e3,-1.5e3))
chipcav.add_photolitho_marker()
chipcav.add_photolitho_vernier()


######### Initialize chip with launchers and feedline
dict_feedline = {'length': 8000,
                'feedwidth': 50,
                'gapwidth': 30,
                'curved': False,
                'orientation': 'up',
                'layer':1}


name = 'Feedlines'
rffeedline = feedline.Feedline(name, dict_feedline)
rf_feed_hor = rffeedline.gen_feedline()


####### Add RF hangers
dict_hangers = {'length': 4000,
            'couplinglength': 600,
            'couplinggap': 10,
            'centerwidth': 4,
            'gapwidth': 20,
            'coupling': 'inductive',
            'orientation': 'up',
            'position': [-3.3e3,3440]}
dict_hangers2 = dict_hangers.copy()
dict_hangers2['orientation'] = 'down'
dict_hangers2['coupling'] = 'capacitive'

rfhangers = hangers.RFHangers('Hangers', dict_hangers)
rf_hangers = rfhangers.gen_full()
rfhangers2 = hangers.RFHangers('Hangers', dict_hangers2, squid=True)
rf_hangers2 = rfhangers2.gen_full()

chipsize = 10e3
chiphang = Base_Chip('RF HANGERS', chipsize, chipsize)
chiphang.add_component(rf_feed_hor, (0,3.5e3))
chiphang.add_component(rf_feed_hor, (0,-3.5e3))
chiphang.add_component(rf_hangers, (0,0))
chiphang.add_component(rf_hangers2, (0,0))
chiphang.add_ebpg_marker((-3.3e3, -1.5e3))
chiphang.add_photolitho_marker()
chiphang.add_photolitho_vernier()



### Add individual designs to big chip
chip = Base_Chip('25mm_mask',xdim=25000,ydim=25000,wafer=False)
for chipi,pos in zip([chipjj[0], chipsquid[0], chiphang],[(-7.5e3,7.5e3),(-7.5e3,2.5e3),(5e3,5e3)]):
    chip.add_component(chipi.cell,(pos[0]+0,pos[1]))
for chipi,pos in zip([chipjj[1], chipsquid[1], chipcav],[(-2.5e3,7.5e3),(-2.5e3,2.5e3),(-5e3,-5e3)]):
    chip.add_component(chipi.cell,(pos[0]+0,pos[1]))

# Dicing marker for RF
for pos in [(0,-10e3),(0,0),(0,10e3)]:
    chip.add_dicing_marker(pos=pos,vert=False)
for pos in [(-10e3,0),(0,0),(10e3,0)]:
    chip.add_dicing_marker(pos=pos,hor=False)

# Dicing marker for DC
chip.add_dicing_marker(pos=(-5e3,5e3),span=[(-10e3,10e3),(-10e3,10e3)])

chip.add_TUlogo(pos=(5000,-5000))
chip.save_to_gds(show = False, save = True)
