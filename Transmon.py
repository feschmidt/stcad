import gdsCAD as cad
from chip import Base_Chip


class Transmon(Base_Chip):

	def __init__(self, name, dict_pads, dict_leads, dict_junction, **kw):
		self.dict_pads = dict_pads
		self.dict_leads = dict_leads
		self.dict_squidloop = kw.pop('dict_squidloop', None)
		self.dict_junction = dict_junction

		super(Transmon, self).__init__(name=name)



	def draw_junction(self):
		pass





class singlejuction_Transmon(Transmon):
	"""
	This class returns a single junction Yale Transmon
	"""

	def __init__(self, name, dict_pads, dict_leads, dict_junction):

		super(singlejuction_Transmon, self).__init__(name, 
													 dict_pads, 
													 dict_leads,
													 dict_junction)


		self.draw_pads()
		self.draw_leads()
		self.draw_junction()

	def draw_pads(self):

		width = self.dict_pads.get('width', 250)
		height = self.dict_pads.get('height', 600)
		gap = self.dict_pads.get('gap', 100)
		rounded_edges = self.dict_pads.get('rounded_edges', False)
		layer = self.dict_pads['layer']

		# Now make 2 cells for the upper pad and lower pad
		pads = cad.core.Cell("PADS")
		lower_pad_points = [(0,0),(width,height)]
		if rounded_edges is False:
			lower_pad = cad.shapes.Rectangle(lower_pad_points,
											layer = layer)

			pads.add(lower_pad)


		else:

			dict_corners = ['BL','BR','TR','TL']
			rad_corner = 0.1
			lower_pad = make_rounded_edges(Rectangle(lower_pad_points,
													layer = layer),
								 					rad_corner, 
								 					dict_corners)

			self.cell.add(pads)



	def draw_leads(self):

		base_width = self.dict_leads.get('base_width',  10)
		top_width = self.dict_leads.get('top_width', 6)
		baseheight = self.dict_leads.get('base_height', 20)
		fork_height = self.dict_leads.get('fork_height',10)
		fork_depth = self.dict_leads.get('fork_depth', 1)
		layer = self.dict_leads['layer']

		trapz_points = [(-0.5*base_width,0),
						(0.5*base_width,0),
						(0.5*top_width,height),
						(-0.5top_width,height),
						(-0.5*base_width,0)]
		
		trapezoid_lower = cad.Core.Boundary( trapz_points,
											layer =layer)

		fork_points = [(-0.5*top_width,baseheight),
						(0.5*top_width,baseheight),
						(0.5*top_width,fork_height),
						(0.5*top_width - top_width/3.,fork_height),
						(0.5*top_width - top_width/3.,fork_height-fork_depth),
						(0.5*top_width - 2*top_width/3.,fork_height-fork_depth),
						(0.5*top_width - 2*top_width/3.,fork_height),
						(-0.5*top_width ,fork_height)]

		fork = cad.Core.Boundary(fork_points,
								layer = layer)

		if rounded_edges is True:
			corners['TR2'] = 2
			corners['TL3'] = 3
			corners['BR4O'] = 4
			corners['BL5O'] = 5
			corners['TR6'] = 6
			corners['TL7'] = 7
			fork_lower = make_rounded_edges(fork, 
											radius=0.3,
											dict_corners=corners)

		else:
			fork_lower = fork

			
		leads = cad.core.Cell("LEADS")

		leads.add(trapezoid_lower)
		leads.add(fork_lower)

		self.cell.add(leads,origin(0,self.dict_pads['height']-1))



	def draw_junctions(self):
		

			






















class squidjunction_Transmon(Transmon):
	"""
	This class returns a squid junction Yale Transmon
	"""

	def __init__(self, dict_pads, dict_squidloop, dict_junction, name)

		super(singlejuction_Transmon, self).__init__()

		self.dict_pads = dict_pads
		self.dict_leads = dict_leads
		self.dict_squidloop = dict_squidloop
		self.dict_junction = dict_junction

		self.draw_pads()
		self.draw_squidloop();
		self.draw_leads()
		self.draw_junction()
		


