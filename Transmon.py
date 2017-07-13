import gdsCAD as cad
from junctions import JJunctions
import utilities
import collections


class Transmon():

	def __init__(self, name, dict_pads, dict_junctions, **kw):
		self.name = name
		self.dict_pads = dict_pads
		self.dict_squidloop = kw.pop('dict_squidloop', None)
		self.dict_junctions = dict_junctions




class Singlejuction_transmon(Transmon):
	"""
	This class returns a single junction Yale Transmon
	"""

	def __init__(self, name, dict_pads, dict_junctions, short = False):

		Transmon.__init__(self,name, dict_pads, dict_junctions)

		self.short = short

		self.overl_junc_lead  = self.dict_junctions['overl_junc_lead']
		
		self.position_offs_junc = self.dict_pads['height'] + self.dict_pads['lead_height'] +\
								 - self.overl_junc_lead
						



		self.pad_spacing = 2*self.position_offs_junc + 2*(self.dict_junctions['bjunction_height'] +\
									self.dict_junctions['junction_height']) + dict_junctions['w_dolan_bridge'] +\
									self.dict_junctions['appr_overlap'] 


		

		

	def gen_pattern(self):
		
		self.cell = cad.core.Cell(self.name)

		if self.short:
			self.dict_pads['fork_depth'] = 0
			self.pad_spacing = 2*(self.dict_pads['height'] + self.dict_pads['lead_height'] )
			
			self.dict_pads['rounded_edges'] = False

		else:
			self.draw_junctions()

		self.draw_pads()
		
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

		junctions = JJunctions('junctions',self.dict_junctions)
		
		self.cell.add(junctions.draw_junctions(),origin=(0,self.position_offs_junc))


	def save_to_gds(self, show = True):

		layout = cad.core.Layout('CHIP')
		layout.add(self.cell)
		layout.save(self.name + '.gds')

		if show:
			layout.show()




class Squidjunction_transmon(Transmon):
	"""
	This class returns a squid junction Yale Transmon
	"""

	def __init__(self, name, dict_pads, dict_squidloop, dict_junctions):

		Transmon.__init__(self,name, dict_pads, dict_junctions)

		self.name = name
		self.dict_pads = dict_pads
		self.dict_squidloop = dict_squidloop
		self.dict_junctions = dict_junctions

		self.overl_junc_lead  = self.dict_junctions['overl_junc_lead']
		
		self.position_offs_junc_y = self.dict_pads['height'] + self.dict_pads['lead_height'] +\
								 self.dict_squidloop['squid_height'] + self.dict_squidloop['squid_thickness'] +\
								 - self.overl_junc_lead

		self.position_offs_junc_x = 0.5*self.dict_squidloop['squid_width'] + 0.5*self.dict_squidloop['squid_thickness'] 
		
		
		self.pad_spacing = 2*self.position_offs_junc_y + 2*(self.dict_junctions['bjunction_height'] +\
									self.dict_junctions['junction_height']) + dict_junctions['w_dolan_bridge'] +\
									self.dict_junctions['appr_overlap'] 



		self.draw_pads()					

		self.draw_junctions()
		


	def draw_pads(self):

		width = self.dict_pads.get('width', 250)
		height = self.dict_pads.get('height', 600)
		lead_width = self.dict_pads.get('lead_width',10)
		lead_height = height +  self.dict_pads.get('lead_height',20)
		fork_depth = self.dict_pads.get('fork_depth', 1)
		rounded_edges = self.dict_pads.get('rounded_edges', False)
		layer = self.dict_pads['layer']

		squid_thickness =  2* self.dict_squidloop.get('squid_thickness',3)
		squid_width = self.dict_squidloop.get('squid_width', 10)
		squid_height = self.dict_squidloop.get('squid_height', 10)
	
		

		squid_width_wrap = squid_thickness + squid_width
		squid_height_wrap = 0.5*squid_thickness+ lead_height + squid_height
		
		# Now make 2 cells for the upper pad and lower pad
		# We also divide thcikness by 2, that's the reason for 6 in the
		# denominator
		pads = cad.core.Cell("PADS")
		lower_pad_points = [(-0.5*width,0),
							(0.5*width,0),
							(0.5*width,height),
							(0.5*lead_width,height),
							(0.5*lead_width,lead_height),
							(0.5*squid_width_wrap,lead_height),
							(0.5*squid_width_wrap, squid_height_wrap),
							(0.5*squid_width_wrap - (1/6.)*squid_thickness,squid_height_wrap),
							(0.5*squid_width_wrap - (1/6.)*squid_thickness,squid_height_wrap-fork_depth),
							(0.5*squid_width_wrap - (2/6.)*squid_thickness,squid_height_wrap-fork_depth),
							(0.5*squid_width_wrap - (2/6.)*squid_thickness,squid_height_wrap),
							(0.5*squid_width, squid_height_wrap),
							(0.5*squid_width, squid_height_wrap - squid_height),
							(-0.5*squid_width, squid_height_wrap - squid_height),
							(-0.5*squid_width, squid_height_wrap),
							(-0.5*squid_width - (1/6.)*squid_thickness,squid_height_wrap),
							(-0.5*squid_width - (1/6.)*squid_thickness,squid_height_wrap-fork_depth),
							(-0.5*squid_width - (2/6.)*squid_thickness,squid_height_wrap-fork_depth),
							(-0.5*squid_width - (2/6.)*squid_thickness,squid_height_wrap),
							(-0.5*squid_width_wrap,squid_height_wrap),
							(-0.5*squid_width_wrap,lead_height),
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
			corners['TL4O'] = 4
			corners['BR5'] = 5
			corners['TR6'] = 6
			corners['TL7'] = 7
			corners['BR8O'] = 8
			corners['BL9O'] = 9
			corners['TR10'] = 10
			corners['TL11'] = 11
			corners['BR12O'] = 12
			corners['BL13O'] = 13
			corners['TR14'] = 14
			corners['TL15'] = 15
			corners['BR16O'] = 16
			corners['BL17O'] = 17
			corners['TR18'] = 18
			corners['TL19'] = 19
			corners['BL20'] = 20
			corners['TR21O'] = 21
			corners['BR22O'] = 22
			corners['TL23'] = 23

			
			rad_corner = 0.3
			lower_pad = utilities.make_rounded_edges(lower_pad,
													rad_corner, 
													corners)

			
		upper_pad = cad.utils.translate(cad.utils.reflect(lower_pad,'x'),(0,self.pad_spacing))
		pad_list = cad.core.Elements([lower_pad,upper_pad])
		pads.add(pad_list)
		

		self.cell.add(pads)


	def draw_junctions(self):


		junctions = JJunctions('junctions_L',self.dict_junctions)
		self.cell.add(junctions.draw_junctions(),origin=(self.position_offs_junc_x,self.position_offs_junc_y))
		junctions.name = 'junctions_R'
		self.cell.add(junctions.draw_junctions(),origin=(-self.position_offs_junc_x,self.position_offs_junc_y))

	def save_to_gds(self, show = True):

		layout = cad.core.Layout('CHIP')
		layout.add(self.cell)
		layout.save(self.name + '.gds')

		if show:
			layout.show()