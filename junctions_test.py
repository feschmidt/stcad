import numpy as np
import junction_array

dict_pads = {'width': 60,
			'height': 60,
			'lead_width': 10,
			'lead_height':10,
			'fork_depth': 0.0,
			'rounded_edges':True,
			'layer':1}



# adding 0.1 at the end of the equation makes sure that we have some extra room

# Note that overlap cannot be negative!!!!!
w_dolan_bridge = 0.12
appr_overlap = (2*(700 - 60)*np.tan(11*np.pi/180) - w_dolan_bridge*1e3)/1e3 + 0.1
dict_junctions = {'bjunction_width':2,
				'bjunction_height':6,
				'junction_width':0.1,
				'junction_height':1,
				'w_dolan_bridge':w_dolan_bridge,
				'appr_overlap':appr_overlap,
				'overl_junc_lead':2.1,
				'layer':2}

njuncx = 9
njuncy = 10
w_juncs_start = 0.1
dw_junc = 0.01
dx = 70
dy = 70
blocks = [2,2]
block_spacing = [1000,1000]
testf = junction_array.Junctiontest('junctiontest', dict_pads,dict_junctions,
									njuncx,njuncy,w_juncs_start,
									dw_junc, dx, dy,blocks, block_spacing)

testf.gen_junction_array()
testf.save_to_gds(save = True)