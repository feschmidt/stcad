import numpy as np
from source_dev.chip import Base_Chip
import source_dev.rf_feedlines as feedline

dict_feedline = {'length': 7000,
                'feedwidth': 50,
                'gapwidth': 30,
                'curved': False,
                'orientation': 'up',
                'layer':1}


name = 'Feedlines'
rffeedline = feedline.Feedline(name, dict_feedline)
rf_feed_hor = rffeedline.gen_feedline()

rffeedline.curved = True
rffeedline.orientation = 'down'
ref_feed_curved_down =  rffeedline.gen_feedline()

rffeedline.orientation = 'up'
ref_feed_curved_up =  rffeedline.gen_feedline()


chipsize = 9e3
chip = Base_Chip(name, chipsize, chipsize)
chip.add_component(rf_feed_hor, (0,0))
chip.add_component(ref_feed_curved_down,(0,-3e3))
chip.add_component(ref_feed_curved_up,(0,3e3))


chip.add_ebpg_marker((-3.3e3, -1.5e3))
# chip.add_TUlogo()
chip.save_to_gds(show=True, save=False)
