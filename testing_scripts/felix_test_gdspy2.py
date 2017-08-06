import gdspy
import gdsCAD as cad
coords8 = [[[-1.16635, -0.5    ], [-1.16635,  0.5    ], [-0.99945,  0.5    ], [-0.99945, -0.5    ]],
           [[-0.99945,  0.3331 ], [-0.99945,  0.5    ], [-0.50005,  0.5    ], [-0.50005, -0.5    ],
            [-0.99945, -0.5    ], [-0.99945, -0.3331 ], [-0.66695, -0.3331 ], [-0.66695, -0.08345],
            [-0.99945, -0.08345], [-0.99945,  0.08345], [-0.66695,  0.08345], [-0.66695,  0.3331 ]]]
coords6 = [[[ 0.50005, -0.5    ], [ 0.50005,  0.5    ], [ 1.16635,  0.5    ], [ 1.16635,  0.3331 ], [ 0.66695,  0.3331 ], [ 0.66695, -0.5    ]],
           [[ 0.66695, -0.5    ], [ 1.16635, -0.5    ], [ 1.16635,  0.08345], [ 0.66695,  0.08345], [ 0.66695, -0.08345], [ 0.99945, -0.08345], [ 0.99945, -0.3331 ], [ 0.66695, -0.3331 ]]]
poly8_layer1 = gdspy.PolygonSet(coords8, 1)
poly6_layer1 = gdspy.PolygonSet(coords6, 1)
poly8_layer2 = gdspy.PolygonSet(coords8, 2)
poly6_layer2 = gdspy.PolygonSet(coords6, 2)

cell1 = gdspy.Cell('CELL1')
cell2 = gdspy.Cell('CELL2')
cell1.add(poly8_layer1)
cell1.add(poly6_layer1)
cell2.add(poly8_layer2)
cell2.add(poly6_layer2)
cell_ref1 = gdspy.CellReference(cell1)
cell_ref2 = gdspy.CellReference(cell2)

box = cad.shapes.Rectangle((-1,-1), (0,0))
box_cell = gdspy.Cell('CELL3')
box_cell_ref = gdspy.CellReference(box_cell)
result = gdspy.fast_boolean(cell_ref1, box_cell_ref, 'not')
result_cell = gdspy.Cell('DIFF_CELL')
result_cell.add(result)

gdspy.write_gds('boolean_subtract_test_example.gds', cells=[cell1, result_cell])   # for gdspy 1.1.1
#gdspy.print_gds('boolean_subtract_test_example.gds', cells=[result_cell])               # for gdspy 1.0