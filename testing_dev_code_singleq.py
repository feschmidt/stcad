import numpy as np
import transmon 

dict_pads = {'width': 30,
			'height': 30,
			'lead_width': 3,
			'lead_height':5,
			'fork_depth': 0,
			'rounded_edges':True,
			'layer':1}



# adding 0.1 at the end of the equation makes sure that we have some extra room

# Note that overlap cannot be negative!!!!!
w_dolan_bridge = 0.12
appr_overlap = (2*(700 - 45)*np.tan(35*np.pi/180) - w_dolan_bridge*1e3)/1e3 + 0.1
dict_junctions = {'bjunction_width':2,
				'bjunction_height':4,
				'junction_width':0.1,
				'junction_height':1,
				'w_dolan_bridge':w_dolan_bridge,
				'appr_overlap':appr_overlap,
				'layer':3}


first_qubit = transmon.Singlejuction_transmon('test',dict_pads,
											dict_junctions,short = False)
first_qubit.gen_pattern()
first_qubit.save_to_gds()

