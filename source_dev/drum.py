import numpy as np
import gdsCAD as cad
from stcad.source_dev.utilities import xor_polygons
import copy

class Drum(cad.core.Cell):
	"""docstring for Drum"""
	def __init__(self, base_layer = 1,
					sacrificial_layer = 2 ,
					top_layer = 3,
					outer_radius = 9,
					head_radius = 7,
					electrode_radius = 6,
					cable_width = 0.5,
					sacrificial_tail_width = 3,
					sacrificial_tail_length = 3,
					opening_width = 4,
					N_holes = 3,
					hole_angle = 45,
					hole_distance_to_center = 4.5,
					hole_distance_to_edge = 0.5,
					name = ''):
		super(Drum, self).__init__(name)
		hole_radius = (head_radius-hole_distance_to_edge-hole_distance_to_center)/2.
		opening_angle = np.arcsin(float(opening_width)/float(head_radius)/2.)*180/np.pi


		##################################
		# Head (holey section)
		##################################

		cad.core.default_layer=top_layer
		holy_section_of_head = cad.core.Elements()


		angle_start = 0
		angle_end = hole_angle
		section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
		  initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
		hole_2_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_end/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_end/180.*np.pi)]
		hole_2 = cad.shapes.Disk(hole_2_position, hole_radius,layer=top_layer)
		section=xor_polygons(section,hole_2)
		holy_section_of_head.add(section)


		for i in range(N_holes-1):
		  angle_start = hole_angle+i*(180-2*hole_angle)/(N_holes-1)
		  angle_end = hole_angle+(i+1)*(180-2*hole_angle)/(N_holes-1)
		  section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
		    initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
		  hole_1_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_start/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_start/180.*np.pi)]
		  hole_1 = cad.shapes.Disk(hole_1_position, hole_radius,layer=top_layer)
		  hole_2_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_end/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_end/180.*np.pi)]
		  hole_2 = cad.shapes.Disk(hole_2_position, hole_radius,layer=top_layer)
		  section=xor_polygons(section,hole_1)
		  section=xor_polygons(section,hole_2)
		  holy_section_of_head.add(section)


		angle_start = 180-hole_angle
		angle_end = 180
		section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
		  initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
		hole_1_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_start/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_start/180.*np.pi)]
		hole_1 = cad.shapes.Disk(hole_1_position, hole_radius,layer=top_layer)
		section=xor_polygons(section,hole_1)
		holy_section_of_head.add(section)

		##################################
		# Head (rest + supports)
		##################################

		drum_head_outer = cad.shapes.Disk((0,0), head_radius, inner_radius = hole_distance_to_center+2*hole_radius, layer=top_layer) 
		drum_head_inner = cad.shapes.Disk((0,0), hole_distance_to_center, layer=top_layer) 


		support_top = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
		  initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer)
		support_bottom = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
		  initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer).copy().reflect('x')



		##################################
		# Electrode
		##################################

		electrode = cad.shapes.Disk((0,0), electrode_radius, layer=base_layer) 
		electrode_tail = cad.core.Path([[-outer_radius,0],[outer_radius,0]], cable_width,layer = base_layer)



		##################################
		# Sacrificial layer
		##################################


		sacrificial_drum = cad.shapes.Disk((0,0), head_radius, layer=sacrificial_layer) 
		sacrificial_tail = cad.core.Path([[-head_radius-sacrificial_tail_length,0],[head_radius+sacrificial_tail_length,0]],\
		 sacrificial_tail_width,layer = sacrificial_layer)


		##################################
		# Add all components
		##################################

		self.add([holy_section_of_head,holy_section_of_head.copy().reflect('x'), drum_head_inner,drum_head_outer,support_bottom,support_top])
		self.add([electrode,electrode_tail])
		self.add([sacrificial_tail,sacrificial_drum])