import numpy as np
import gdsCAD as cad
import transmon

class Junctiontest():

	def __init__(self, name, dict_pads, dict_junctions, nrows, ncols, w_junc_start,
				dw_junc, dx, dy):

		self.name = name
		self.dict_pads = dict_pads
		self.dict_junctions = dict_junctions
		self.ncols = ncols
		self.nrows = nrows
		self.w_junc_start = w_junc_start
		self.dw_junc = dw_junc
		self.dx = dx
		self.dy = dy


	def gen_junction_array(self):

		test_junction = transmon.Singlejuction_transmon('test',self.dict_pads,
											self.dict_junctions,short = False)
		grid = cad.core.Cell('GRID')
		self.grid_chip = cad.core.Cell('GRID_CHIP')

		for j in range(0,self.nrows):
			
			for i in range(0,self.ncols):

				junc_width = self.w_junc_start + (j*self.nrows + i)*self.dw_junc
				self.dict_junctions['junction_width'] = junc_width
				name = 'testjj_' + str(junc_width)
				test_junction.name = name
				test_junction.gen_pattern()

				grid.add(test_junction.cell,origin = (i*self.dx,j*self.dy))


		
		max_x = grid.bounding_box[1][0] + 300
		max_y = grid.bounding_box[1][1] + 300


		new_cell = cad.core.CellArray(grid, 2,2,(max_x,max_y),(0,0))
		self.grid_chip.add(new_cell)

		pos_endx = self.grid_chip.bounding_box[1][0]
		pos_endy = self.grid_chip.bounding_box[1][1]

		# Making calibration junctions
		posx_cal_jj = pos_endx+300
		for n in range(0,5):
			name = 'testcalibrationjj_' + str()
			test_junction.name = name
			test_junction.short = True
			test_junction.gen_pattern()

			self.grid_chip.add(test_junction.cell,origin= (posx_cal_jj+n*100,pos_endy/2.))




		label = cad.shapes.LineLabel('JunctionTest..' + 'width='+ str(self.w_junc_start)+\
										'.....'+ str(junc_width),30, (pos_endx/2.,pos_endy/2.),layer=3)
		self.grid_chip.add(label)
	
		# grid_new.show()
	def save_to_gds(self, save = True, show = True):

		layout = cad.core.Layout('CHIP')
		layout.add(self.grid_chip)


		if save:
			layout.save(self.name + '.gds')

		if show:
			layout.show()

