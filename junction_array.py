import numpy as np
import gdsCAD as cad
import transmon
import time

class Junctiontest():

	def __init__(self, name, dict_pads, dict_junctions, nrows, ncols, w_junc_start,
				dw_junc, dx, dy,block, block_spacing):

		self.name = name
		self.dict_pads = dict_pads
		self.dict_junctions = dict_junctions
		self.ncols = ncols
		self.nrows = nrows
		self.w_junc_start = w_junc_start
		self.dw_junc = dw_junc

		offset_x = self.dict_pads['width']

		offset_y = 2*(self.dict_pads['height'] + self.dict_pads['lead_height'] )+\
							2*self.dict_junctions['bjunction_height'] + 2*self.dict_junctions['junction_height']+\
							self.dict_junctions['appr_overlap']

		

		self.dx = dx + offset_x 
		self.dy = dy + offset_y
		self.block = block
		self.block_spacing = block_spacing

		self.layer_label = 3
		self.layer_ref = 4
		self.layer_box = 5
	def gen_junction_array(self):

		test_junction = transmon.Singlejuction_transmon('test',self.dict_pads,
											self.dict_junctions,short = False)
		grid = cad.core.Cell('GRID')
		ref_cell = cad.core.Cell('REF_CELL')
		self.grid_chip = cad.core.Cell('GRID_CHIP')
		# label_grid = cad.shapes.LineLabel(' Block'  ,30, (pos_endx/2.,pos_endy+50),layer=3)
		for j in range(0,self.nrows):
			
			for i in range(0,self.ncols):

				junc_width = self.w_junc_start + (j*self.nrows + i)*self.dw_junc
				self.dict_junctions['junction_width'] = junc_width
				name = 'testjj_' + str(junc_width)
				test_junction.name = name
				test_junction.gen_pattern()

				grid.add(test_junction.cell,origin = (i*self.dx,j*self.dy))

		
		max_x = grid.bounding_box[1][0] + self.block_spacing[0]
		max_y = grid.bounding_box[1][1] + self.block_spacing[1]

		# This is a reference shape
		ref_points = [(0,0),(200,0),(200,40),
					  (40,40),(40,200),(0,200)]
		ref_shape = cad.core.Boundary(ref_points,layer = self.layer_ref)
		ref_cell.add(ref_shape)
		grid.add(ref_cell, origin=(grid.bounding_box[0][0]-100,-100))

		new_cell = cad.core.CellArray(grid, self.block[0],
									self.block[1] ,(max_x,max_y),(0,0))
		self.grid_chip.add(new_cell)
	
		pos_endx = self.grid_chip.bounding_box[1][0]
		pos_endy = self.grid_chip.bounding_box[1][1]

		# Making calibration junctions
		posx_cal_jj = pos_endx+self.block_spacing[0]
		for n in range(0,5):
			name = 'testcalibrationjj_' + str()
			test_junction.name = name
			test_junction.short = True
			test_junction.gen_pattern()

			# We have 5 calibration junctions spaced 50 um apart
			self.grid_chip.add(test_junction.cell,origin= (posx_cal_jj+n*self.dx,pos_endy/2.))



		date = time.strftime("%d/%m/%Y")
		#The label is added 100 um on top of the main cell
		label_grid_chip = cad.shapes.LineLabel('JunctionTest..' + 'width='+ str(self.w_junc_start)+\
										'.....'+ str(junc_width) +' um ' + \
										 date,40, (pos_endx/3.,pos_endy+100),layer=self.layer_label)
		

		self.grid_chip.add(label_grid_chip)
		
		# Now adding a box around design
		final_dim = self.grid_chip.bounding_box
		box=cad.shapes.Box(final_dim[0] - 30,final_dim[1] + 30 , width=0.2, layer =self.layer_box)

		self.grid_chip.add(box)

	def save_to_gds(self, save = True, show = True):

		layout = cad.core.Layout('CHIP')
		layout.add(self.grid_chip)


		if save:
			layout.save(self.name + '.gds')

		if show:
			layout.show()

