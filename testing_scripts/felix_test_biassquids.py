import numpy as np
from source_dev.chip import Base_Chip
import source_dev.rf_feedlines as feedline
import source_dev.rf_dcbias as dcbias

######### Initialize chip with launchers and feedline
launchdist = 7500
dict_feedline = {'length': launchdist,
                'feedwidth': 10,
                'gapwidth': 6.2,
                'curved': False,
                'orientation': 'up',
                'layer':1}


name = 'Launchers'
rffeedline = feedline.Feedline(name, dict_feedline,feedline=False)
rf_feed_hor = rffeedline.gen_feedline()


####### Add DC bias cavities
cavlength = 6900
dict_dcbias = []
dict_dcbias.append({'length': cavlength,
            'feedlength': 300,
            'centerwidth': 10,
            'gapwidth': 6.2,
            'position': (-launchdist/2,-3511-0.2),
            'shunt': (155,420,5,220,632),
            'squid': (10,10,1,3)})
for i in [(10,10,2,3),(20,20,1,3),(10,10,2,3)]:
    copy = dict_dcbias[0].copy()
    copy['squid'] = i
    dict_dcbias.append(copy)

chipsize = 10e3
chip_sub3 = Base_Chip('RF_DC_BIAS_'+str(cavlength/1e3)+'mm', chipsize, chipsize,labelloc=(-500,4500),labelwidth=5)
chip_sub3.add_component(rf_feed_hor, (0,3.5e3))
chip_sub3.add_component(rf_feed_hor, (0,-3.5e3))

for i,loc,pos in zip(range(4),('sw','se','ne','nw'),((-2400,-1400),(2000,-1400),(2000,1400),(-2400,1400))):
    dccavs = dcbias.RFShunt('Shunt cavities', dict_dcbias[i], termination='squid')
    rf_dcvacs = dccavs.gen_partial(loc=loc)
    rf_dcvacs_label = dccavs.gen_label(pos=pos)
    chip_sub3.add_component(rf_dcvacs, (0,0))
    chip_sub3.add_component(rf_dcvacs_label, (0,0))

chip_sub3.add_ebpg_marker((-3.3e3, -1.5e3))
chip_sub3.add_photolitho_marker(pos=(-300,0))
chip_sub3.add_photolitho_vernier(pos=(-100,-500))
chip_sub3.add_photolitho_marker(layer=(1,3),pos=(300,0))
chip_sub3.add_photolitho_vernier(layer=(1,3),pos=(-100,200))

chip_sub3.save_to_gds(show=False, save=True)
