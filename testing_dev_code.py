import numpy as np
import Transmon 

dict_pads = {'width': 250,
			'height': 600,
			'lead_width': 3,
			'lead_height':20,
			'fork_depth': 1,
			'rounded_edges':True,
			'layer':1}



# dict_leads = {'base_width':7,
# 			'top_width':2,
# 			'base_height':5,
# 			'fork_height': 3,
# 			'fork_depth': 0.5,
# 			'layer':2}

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

dict_squidloop = {'squid_thickness':3,
				'squid_width': 30,
				'squid_height': 10}
# first_qubit = Transmon.singlejuction_transmon('test',dict_pads,
# 											dict_junctions,short = False)


first_qubit = Transmon.squidjunction_transmon('test',dict_pads,dict_squidloop,
											dict_junctions)