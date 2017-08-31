from source_dev.chip import Base_Chip
import source_dev.rf_feedlines as feedline
import source_dev.jpa_shunt_ald as jpa_shunt


######### Initialize chip with launchers and feedline
dict_feedline = {'length': 8000,
                'feedwidth': 10,
                'gapwidth': 6,
                'curved': False,
                'orientation': 'up',
                'layer':1}


name = 'Feedlines'
rffeedline = feedline.Feedline(name, dict_feedline, feedline=False)
rf_feed_hor = rffeedline.gen_feedline()


####### Add RF hangers
feedlength = 400
dict_jpa = {'feedlength': feedlength,
            'position': (-4000,-3511),
            'shunt': (80,125),
            'squid': (10,10,1,3),
            'squidfeed': 15,
            'centerwidth': 10,
            'gapwidth': 6}

jpa = jpa_shunt.JPA('JPA', dict_jpa)
rf_jpa = jpa.gen_full()

dict_jpa2 = {'feedlength': feedlength,
            'position': (-4000,3489),
            'shunt': (80,125),
            'squid': (10,10,1,3),
            'squidfeed': 15,
            'centerwidth': 10,
            'gapwidth': 6}

jpa2 = jpa_shunt.JPA('JPA', dict_jpa2)
rf_jpa2 = jpa2.gen_full()

chipsize = 10e3
chip = Base_Chip('JPA TEST', chipsize, chipsize)
chip.add_component(rf_jpa, (0,0))
chip.add_component(rf_feed_hor, (0,-3500))
chip.add_component(rf_jpa2, (0,0))
chip.add_component(rf_feed_hor, (0,3500))
chip.add_ebpg_marker((-3300, -1500))
chip.add_ebpg_marker((feedlength-4150, -3750), spacing=500, duplicate=False)    # add extra markers for trimming
chip.add_photolitho_marker()
chip.add_photolitho_vernier()


# chip.add_TUlogo()
chip.save_to_gds(show = False, save = True)
