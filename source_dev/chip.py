import numpy as np
import gdsCAD as cad

class Base_Chip():
	
	"""
	This object represent a single chip and can be considered as the parentobject.
	
	"""

	def __init__(self,name,dict_layers = None):

		if dict_layers is None:

			self.dict_layers = {'Pads':1,
								'Leads:':2,
								'Junctions':3,
								'Markers': 4}


		else:
			self.dict_layers = dict_layers


		self.base_point = {}

		self.cell = cad.core.Cell(name)




