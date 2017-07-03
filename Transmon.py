import gdsCAD as cad
from chip import Base_Chip
from junctions import JJunctions
import utilities
import collections


class transmon(Base_Chip):

	def __init__(self, name, dict_pads, dict_leads, dict_junctions, **kw):
		self.dict_pads = dict_pads
		self.dict_leads = dict_leads
		self.dict_squidloop = kw.pop('dict_squidloop', None)
		self.dict_junctions = dict_junctions

		Base_Chip.__init__(self,name=name)





class singlejuction_transmon(transmon):
	"""
	This class returns a single junction Yale Transmon
	"""

	def __init__(self, name, dict_pads, dict_leads, dict_junctions, short = False):

		transmon.__init__(self,name, dict_pads, dict_leads, dict_junctions)

		overl_junc_lead = 1
		overl_lead_pad = 1
		self.position_offs_junc = self.dict_pads['height'] + self.dict_leads['base_height'] + \
							self.dict_leads['fork_height'] - overl_lead_pad - overl_junc_lead

		# 1 um is the overlap between  big pads and small leads
		self.position_offs_leads = self.dict_pads['height'] - overl_lead_pad

		self.pad_spacing = self.position_offs_junc + 2*(self.dict_junctions['bjunction_height'] +\
									self.dict_junctions['junction_height']) + dict_junctions['w_dolan_bridge'] +\
									self.dict_junctions['appr_overlap'] +\
									self.dict_leads['base_height'] + self.dict_leads['fork_height'] - overl_junc_lead - \
									overl_lead_pad

		self.lead_spacing = 2*(self.dict_leads['base_height'] + self.dict_leads['fork_height'] +\
							self.dict_junctions['bjunction_height'] + self.dict_junctions['junction_height']) +\
							dict_junctions['w_dolan_bridge'] +self.dict_junctions['appr_overlap'] - 2*overl_junc_lead

		

		if short:
			self.dict_leads['fork_depth'] = 0
			self.pad_spacing = self.dict_pads['height'] + 2*(self.dict_leads['base_height'] + self.dict_leads['fork_height']) - \
								2*overl_lead_pad
			self.lead_spacing = 2*(self.dict_leads['base_height'] + self.dict_leads['fork_height'])
		
		else:
			self.draw_junctions()

		self.draw_pads()
		self.draw_leads()
		
		layout = cad.core.Layout('LIBRARY')
		layout.add(self.cell)
		layout.save('output.gds')
		layout.show()

	def draw_pads(self):

		width = self.dict_pads.get('width', 250)
		height = self.dict_pads.get('height', 600)
		rounded_edges = self.dict_pads.get('rounded_edges', False)
		layer = self.dict_pads['layer']

		# Now make 2 cells for the upper pad and lower pad
		pads = cad.core.Cell("PADS")
		lower_pad_points = [(-0.5*width,0),(0.5*width,height)]
		if rounded_edges is False:
			lower_pad = cad.shapes.Rectangle(lower_pad_points[0],lower_pad_points[1],
											layer = layer)
		


		else:
		
			corners = collections.OrderedDict()
			corners['BL0'] = 0
			corners['BR1'] = 3
			corners['TR2'] = 2
			corners['TL3'] = 1
			
			rad_corner = 0.3
			lower_pad = utilities.make_rounded_edges(cad.shapes.Rectangle(lower_pad_points[0],
													lower_pad_points[1],
													layer = layer),
													rad_corner, 
													corners)

			
		upper_pad = cad.utils.translate(lower_pad,(0,self.pad_spacing))
		pad_list = cad.core.Elements([lower_pad,upper_pad])
		pads.add(pad_list)
		

		self.cell.add(pads)



	def draw_leads(self):

		base_width = self.dict_leads.get('base_width',  10)
		top_width = self.dict_leads.get('top_width', 6)
		base_height = self.dict_leads.get('base_height', 20)
		fork_height = base_height + self.dict_leads.get('fork_height',10)
		fork_depth = self.dict_leads.get('fork_depth', 1)
		rounded_edges = self.dict_leads.get('rounded_edges', False)
		layer = self.dict_leads['layer']

		leads = cad.core.Cell("LEADS")

		# trapz_points = [(-0.5*base_width,0),
		# 				(0.5*base_width,0),
		# 				(0.5*top_width,base_height),
	

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

			
		
		
		
		fork_upper = cad.utils.translate(cad.utils.reflect(fork_lower,'x'),(0,self.lead_spacing))
		lead_list = cad.core.Elements([fork_lower,fork_upper])
		leads.add(lead_list)
		

		
		self.cell.add(leads,origin=(0,self.position_offs_leads))



	def draw_junctions(self):

		junctions = JJunctions(self.dict_junctions)
		
		self.cell.add(junctions.draw_junctions(),origin=(0,self.position_offs_junc))


		

			





















class squidjunction_transmon(transmon):
	"""
	This class returns a squid junction Yale Transmon
	"""

	def __init__(self, dict_pads, dict_squidloop, dict_junction, name):

		super(singlejuction_Transmon, self).__init__()

		self.dict_pads = dict_pads
		self.dict_leads = dict_leads
		self.dict_squidloop = dict_squidloop
		self.dict_junction = dict_junction

		self.draw_pads()
		self.draw_squidloop();
		self.draw_leads()
		self.draw_junction()
		


