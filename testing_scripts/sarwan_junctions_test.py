import numpy as np
from source_dev.chip import Base_Chip
import source_dev.junction_array as junction_array
"""
For junctiontest layer 14,20,21 reserved
"""
dict_pads = {'width': 60,
             'height': 60,
             'lead_width': 20,
             'lead_height': 30,
             'rounded_edges': True,
             'layer': 1}


# adding 0.1 at the end of the equation makes sure that we have some extra room

# Note that overlap cannot be negative!!!!!
w_dolan_bridge = 0.2
appr_overlap = (2 * (320 - 35) * np.tan(35 * np.pi / 180) -
                w_dolan_bridge * 1e3) / 1e3 + 0.1
dict_junctions = {'bjunction_width': 2,
                  'bjunction_height': 20,
                  'junction_width': 0.1,
                  'junction_height': 1,
                  'w_dolan_bridge': w_dolan_bridge,
                  'appr_overlap': appr_overlap,
                  'overl_junc_lead': 2.1,
                  'layer': 2}

njuncx = 2
njuncy = 5
w_juncs_start = 0.01
dw_junc = 0.01
dx = 100
dy = 100
blocks = [2, 1]
block_spacing = [1000, 1000]
name = 'JunctionTest..' + 'width=' + str(w_juncs_start) +\
    '.....' + str(njuncx * njuncy * dw_junc +
                  dw_junc) + ' um '

testf = junction_array.Junctiontest('Junctiontest', dict_pads, dict_junctions,
                                    njuncx, njuncy, w_juncs_start,
                                    dw_junc, dx, dy, blocks, block_spacing)


testf.gen_junction_array()

njuncx = 5
njuncy = 10
w_juncs_start = 0.12
dw_junc = 0.02
dx = 100
dy = 100
blocks = [2, 1]
block_spacing = [1000, 1000]
name = 'JunctionTest..' + 'width=' + str(w_juncs_start) +\
    '.....' + str(njuncx * njuncy * dw_junc +
                  dw_junc) + ' um '

testf2 = junction_array.Junctiontest('Junctiontest', dict_pads, dict_junctions,
                                    njuncx, njuncy, w_juncs_start,
                                    dw_junc, dx, dy, blocks, block_spacing)

testf2.gen_junction_array()
chip = Base_Chip(name, 8000, 8000)
chip.add_component(testf.cell, (-2000, -2500))
chip.add_component(testf2.cell, (-2000, -200))
chip.save_to_gds(show=True, save=True)
