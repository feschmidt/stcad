import numpy as np
from source_dev.chip import Base_Chip
import source_dev.rf_feedlines as feedline
import source_dev.rf_hangers as hangers

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
rfhangers2 = hangers.RFHangers('Hangers', dict_hangers2)
rf_hangers2 = rfhangers2.gen_full()

chipsize = 10e3
chip = Base_Chip('RF HANGERS', chipsize, chipsize)
chip.add_component(rf_feed_hor, (0,3.5e3))
chip.add_component(rf_feed_hor, (0,-3.5e3))
chip.add_component(rf_hangers, (0,0))
chip.add_component(rf_hangers2, (0,0))


chip.add_ebpg_marker((-3.3e3, -1.5e3))
chip.chip_not()
# chip.add_TUlogo()
chip.save_to_gds(show=True, save=False)
