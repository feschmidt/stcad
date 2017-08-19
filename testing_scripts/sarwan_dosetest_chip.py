import numpy as np
from source_dev.chip import Base_Chip
import source_dev.transmon as transmon


dict_pads = {'width': 60,
             'height': 60,
             'lead_width': 20,
             'lead_height': 30,
             'rounded_edges': True,
             'layer': 1}


w_dolan_bridge = 0.12
appr_overlap = (2 * (320 - 45) * np.tan(35 * np.pi / 180) -
                w_dolan_bridge * 1e3) / 1e3 + 0.1
dict_junctions = {'bjunction_width': 2,
                  'bjunction_height': 20,
                  'junction_width': 0.1,
                  'junction_height': 1,
                  'w_dolan_bridge': w_dolan_bridge,
                  'appr_overlap': appr_overlap,
                  'overl_junc_lead': 2.1,
                  'layer': 2}


first_qubit = transmon.Singlejunction_transmon('qubit_100nm', dict_pads,
                                               dict_junctions, short=False,
                                               junctiontest=True)
first_qubit.gen_pattern()
qubit_100nm = first_qubit.cell

first_qubit.name = 'qubit_910nm'
first_qubit.dict_junctions['junction_width'] = 0.91
first_qubit.gen_pattern()
qubit_910nm = first_qubit.cell


chip = Base_Chip('Dosetest Electra coating chip PMGI', 8000, 8000)
chip.add_component(qubit_100nm, (-100, 0))
chip.add_component(qubit_910nm, (300, 0))
chip.save_to_gds(show=True, save=True)
