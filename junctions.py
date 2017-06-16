
import numpy as np
import gdsCAD as cad
from chip import Base_Chip

class JJunctions(Base_Chip):

	def __init__(self, name, dict_junctions):
		self.dict_junctions = dict_junctions

		super(JJunctions,self).__init__(name)

		 bjunction_width = dict_junctions.get('bjunction_width',2)
		 bjunction_height = dict_junctions.get('bjunction_height',5)
		 junction_width = dict_junctions.get('junction_width',0.2)
		 w_dolan_bridge = dict_junctions.get('w_dolan_bridge', 0.120)
		 layer = self.dict_junctions['layer']

		 junct_lead_points = [(-0.5*junction_width,0),
		 					  (0.5*junction_width,junction_height)]
		 
		 junction_lead = cad.shapes.Rectangle(junct_lead_points,
		 									layer = layer )

		 junct_trapz_points = [(-0.5*junction_width,bjunction_height),
		 						(0.5*junction_width,bjunction_height),
		 						(0.5*(junction_width+0.1),1.5),
		 						(-0.5*(junction_width+0.1),1.5)]