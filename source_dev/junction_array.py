import numpy as np
import gdsCAD as cad
import transmon
import time


class Junctiontest():

    def __init__(self, name, dict_pads, dict_junctions, nrows, ncols, w_junc_start,
                 dw_junc, dx, dy, block, block_spacing,reference_shape = True):

        self.name = name
        self.reference_shape=reference_shape
        self.dict_pads = dict_pads
        self.dict_junctions = dict_junctions
        self.ncols = ncols
        self.nrows = nrows
        self.w_junc_start = w_junc_start
        self.dw_junc = dw_junc

        offset_x = self.dict_pads['width']

        offset_y = 2 * (self.dict_pads['height'] + self.dict_pads['lead_height'] ) +\
            2 * self.dict_junctions['bjunction_height'] + 2 * self.dict_junctions['junction_height'] +\
            self.dict_junctions['appr_overlap']

        self.dx = dx + offset_x
        self.dy = dy + offset_y
        self.block = block
        self.block_spacing = block_spacing

        self.layer_ref = 14

    def gen_junction_array(self):

        test_junction = transmon.Singlejunction_transmon('test', self.dict_pads,
                                                         self.dict_junctions, short=False,
                                                         junctiontest=True)
        grid = cad.core.Cell('GRID')
        ref_cell = cad.core.Cell('REF_CELL')
        self.cell = cad.core.Cell('GRID_CHIP')
        # label_grid = cad.shapes.LineLabel(' Block'  ,30, (pos_endx/2.,pos_endy+50),layer=3)
        for j in range(0, self.ncols):

            for i in range(0, self.nrows):

                junc_width = self.w_junc_start + \
                    (j * self.nrows + i) * self.dw_junc
                self.dict_junctions['junction_width'] = junc_width
                name = 'testjj_' + str(junc_width)
                print junc_width
                test_junction.name = name
                test_junction.gen_pattern()

                grid.add(test_junction.cell, origin=(i * self.dx, j * self.dy))

        max_x = grid.bounding_box[1][0] + self.block_spacing[0]
        max_y = grid.bounding_box[1][1] + self.block_spacing[1]

        # This is a reference shape
        if self.reference_shape:
            ref_points = [(0, 0), (200, 0), (200, 40),
                          (40, 40), (40, 200), (0, 200)]
            ref_shape = cad.core.Boundary(ref_points, layer=self.layer_ref)
            ref_cell.add(ref_shape)
        grid.add(ref_cell, origin=(grid.bounding_box[0][0] - 100, -100))

        new_cell = cad.core.CellArray(grid, self.block[0],
                                      self.block[1], (max_x, max_y), (0, 0))
        self.cell.add(new_cell)

        pos_endx = self.cell.bounding_box[1][0]
        pos_endy = self.cell.bounding_box[1][1]

        # # Making 10 standard calibration junctions
        # posx_cal_jj = pos_endx + self.block_spacing[0]
        # posy_cal_jj = pos_endy / 2.
        # for n in range(0, 2):
        #     for m in range(0, 5):
        #         name = 'testcalibrationjj_' + str()
        #         test_junction.name = name
        #         test_junction.short = True
        #         test_junction.gen_pattern()

        #         # We have 5 calibration junctions spaced 50 um apart
        #         self.cell.add(test_junction.cell,
        #                       origin=(posx_cal_jj + m * self.dx, posy_cal_jj + n * self.dy))
