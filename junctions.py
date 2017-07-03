
import numpy as np
import gdsCAD as cad


class JJunctions():

	def __init__(self,  dict_junctions):
		
		self.dict_junctions = dict_junctions

		

		

	def draw_junctions(self):

		bjunction_width = self.dict_junctions.get('bjunction_width',2)
		bjunction_height = self.dict_junctions.get('bjunction_height',5)
		junction_width = self.dict_junctions.get('junction_width',0.2)
		junction_height = self.dict_junctions.get('junction_height',1.5)
		w_dolan_bridge = self.dict_junctions.get('w_dolan_bridge', 0.120)
		appr_overlap = self.dict_junctions.get('appr_overlap', 0.9 )
		layer = self.dict_junctions['layer']
		# estimate of the junction overlap at 35 double angle evaporation, with the first layer
		# of 45 nm thick Al. Resist used: MMA/PMMA


		if appr_overlap <= 0:
			raise ValueError('overlap cannot be <0')



		junct_lead_lower_points = [(-0.5*bjunction_width,0),
								(0.5*bjunction_width,0),
								(0.5*bjunction_width,bjunction_height),
								(0.5*(junction_width+0.1),bjunction_height+junction_height),
								(-0.5*(junction_width+0.1),bjunction_height+junction_height),
								(-0.5*bjunction_width,bjunction_height),
								(-0.5*bjunction_width,0)]





		junct_lead_upper_points = [(-0.5*bjunction_width,0),
								(0.5*bjunction_width,0),
								(0.5*bjunction_width,bjunction_height),
								(0.5*(junction_width),bjunction_height+junction_height),
								(0.5*(junction_width),bjunction_height+junction_height+appr_overlap),
								(-0.5*(junction_width),bjunction_height+junction_height+appr_overlap ),
								(-0.5*(junction_width),bjunction_height+junction_height),
								(-0.5*bjunction_width,bjunction_height),
								(-0.5*bjunction_width,0)]


		junct_lower = cad.core.Boundary(junct_lead_lower_points, layer = layer)

		junct_upper = cad.core.Boundary(junct_lead_upper_points, layer = layer)

		junct_upper = cad.utils.translate(cad.utils.reflect(junct_upper,'x'),
											(0,2*(bjunction_height+junction_height)+appr_overlap + w_dolan_bridge ))

		junc_list = cad.core.Elements([junct_lower,junct_upper])

		cell_junct = cad.core.Cell('JUNCTIONS')

		cell_junct.add(junc_list)



		return cell_junct

