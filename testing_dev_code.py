import numpy as np
import Transmon 

dict_pads = {'width': 30,
			'height': 30,
			'rounded_edges':True,
			'layer':1}
dict_leads = {'base_width':7,
			'top_width':2,
			'base_height':5,
			'fork_height': 3,
			'fork_depth': 0.5,
			'layer':2}

# adding 0.1 at the end of the equation makes sure that we have some extra room
w_dolan_bridge = 0.12
appr_overlap = (2*(700 - 45)*np.tan(35*np.pi/180) - w_dolan_bridge*1e3)/1e3 + 0.1
dict_junctions = {'bjunction_width':1.3,
				'bjunction_height':2,
				'junction_width':0.5,
				'junction_height':1,
				'w_dolan_bridge':0.12,
				'appr_overlap':0.2,
				'layer':3}
first_qubit = Transmon.singlejuction_transmon('test',dict_pads,
											dict_leads,dict_junctions,short = False)
