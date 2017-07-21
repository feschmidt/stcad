import numpy as np
import gdsCAD as cad

class Leads():

	def __init(self,name,dict_leads)


		base_width = self.dict_leads.get('base_width',  10)
		top_width = self.dict_leads.get('top_width', 6)
		base_height = self.dict_leads.get('base_height', 20)
		fork_height = base_height + self.dict_leads.get('fork_height',10)
		fork_depth = self.dict_leads.get('fork_depth', 1)
		rounded_edges = self.dict_leads.get('rounded_edges', False)
		layer = self.dict_leads['layer']

		leads = cad.core.Cell("LEADS")


	def draw(self):

		fork_points = [(-0.5*base_width,0),
						(0.5*base_width,0),
						(0.5*top_width,base_height),
						(0.5*top_width,fork_height),
						(0.5*top_width - top_width/3.,fork_height),
						(0.5*top_width - top_width/3.,fork_height-fork_depth),
						(0.5*top_width - 2*top_width/3.,fork_height-fork_depth),
						(0.5*top_width - 2*top_width/3.,fork_height),
						(-0.5*top_width ,fork_height),
						(-0.5*top_width,base_height)]

		fork = cad.core.Boundary(fork_points,
								layer = layer)

		if rounded_edges is True:
			corners = collections.OrderedDict()
			corners['TR2'] = 2
			corners['TL3'] = 3
			corners['BR4O'] = 4
			corners['BL5O'] = 5
			corners['TR6'] = 6
			corners['TL7'] = 7
			fork_lower = utilities.make_rounded_edges(fork, 
											radius=0.3,
											dict_corners=corners)




		else:
			fork_lower = fork

			
		
		leads.add(fork_lower)

		return leads		
	

