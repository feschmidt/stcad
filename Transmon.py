import gdsCAD as cad
from chip import Base_Chip
from junctions import JJunctions
import utilities
import collections


class transmon(Base_Chip):

	def __init__(self, name, dict_pads, dict_junctions, **kw):
		self.dict_pads = dict_pads
		self.dict_squidloop = kw.pop('dict_squidloop', None)
		self.dict_junctions = dict_junctions

		Base_Chip.__init__(self,name=name)





class singlejuction_transmon(transmon):
	"""
	This class returns a single junction Yale Transmon
	"""

	def __init__(self, name, dict_pads, dict_junctions, short = False):

		transmon.__init__(self,name, dict_pads, dict_junctions)

		overl_junc_lead = 2
		
		self.position_offs_junc = self.dict_pads['height'] + self.dict_pads['lead_height'] +\
								 - overl_junc_lead
						



		self.pad_spacing = 2*self.position_offs_junc + 2*(self.dict_junctions['bjunction_height'] +\
									self.dict_junctions['junction_height']) + dict_junctions['w_dolan_bridge'] +\
									self.dict_junctions['appr_overlap'] 


		

		if short:
			self.dict_pads['fork_depth'] = 0
			self.pad_spacing = 2*(self.dict_pads['height'] + self.dict_pads['lead_height'] )
			
		
		else:
			self.draw_junctions()

		self.draw_pads()

		
		layout = cad.core.Layout('LIBRARY')
		layout.add(self.cell)
		layout.save('output.gds')
		layout.show()

	def draw_pads(self):

		width = self.dict_pads.get('width', 250)
		height = self.dict_pads.get('height', 600)
		lead_width = self.dict_pads.get('lead_width',10)
		lead_height = height +  self.dict_pads.get('lead_height',20)
		fork_depth = self.dict_pads.get('fork_depth', 1)
		rounded_edges = self.dict_pads.get('rounded_edges', False)
		layer = self.dict_pads['layer']

		# Now make 2 cells for the upper pad and lower pad
		pads = cad.core.Cell("PADS")
		lower_pad_points = [(-0.5*width,0),
							(0.5*width,0),
							(0.5*width,height),
							(0.5*lead_width,height),
							(0.5*lead_width,lead_height),
							(0.5*lead_width - (1/3.)*lead_width,lead_height),
							(0.5*lead_width - (1/3.)*lead_width,lead_height-fork_depth),
							(0.5*lead_width - (2/3.)*lead_width,lead_height-fork_depth),
							(0.5*lead_width - (2/3.)*lead_width,lead_height),
							(-0.5*lead_width,lead_height),
							(-0.5*lead_width, height),
							(-0.5*width,height)]
		
		lower_pad = cad.core.Boundary(lower_pad_points,
											layer = layer)
		


		if rounded_edges:
		
			corners = collections.OrderedDict()
			corners['BL0'] = 0
			corners['BR1'] = 1
			corners['TR2'] = 2
			corners['BL3O'] = 3
			corners['TR4'] = 4
			corners['TL5'] = 5
			corners['BR6O'] = 6
			corners['BL7O'] = 7
			corners['TR8'] = 8
			corners['TL9'] = 9
			corners['BR10O'] = 10
			corners['TL11'] = 11
			
			rad_corner = 0.3
			lower_pad = utilities.make_rounded_edges(lower_pad,
													rad_corner, 
													corners)

			
		upper_pad = cad.utils.translate(cad.utils.reflect(lower_pad,'x'),(0,self.pad_spacing))
		pad_list = cad.core.Elements([lower_pad,upper_pad])
		pads.add(pad_list)
		

		self.cell.add(pads)



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
		


