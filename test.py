from gdsCAD import *
from shapely.geometry import Polygon
# Create a Cell and add the box
cell1=core.Cell('first')
cell2=core.Cell('second')
top = core.Cell('TOP')
# Create three boxes on layer 2 of different sizes centered at
# the origin and add them to the cell.
l=3
height = 40
top_width = 5
fork_height = height+ 20
fork_depth = 2
base_width = 20
top_width = 10


box=shapes.Rectangle((-l,-l), (l,l), layer=2)
trapezoid = core.Boundary( [(-0.5*base_width,0),
										(0.5*base_width,0),
										(0.5*top_width,height),
										(-0.5*top_width,height),
										(-0.5*base_width,0)],layer=1)
fork = core.Boundary([(-0.5*top_width,0),
							(0.5*top_width,0),
							(0.5*top_width,fork_height),
							(0.5*top_width - top_width/3.,fork_height),
							(0.5*top_width - top_width/3.,fork_height-fork_depth),
							(0.5*top_width - 2*top_width/3.,fork_height-fork_depth),
							(0.5*top_width - 2*top_width/3.,fork_height),
							(-0.5*top_width ,fork_height),
							(-0.5*top_width,0)],layer=2)
print fork.points
box2 = utils.translate(box,(10,0))
box2.layer=3

cell1.add(trapezoid)
cell2.add(fork)
top.add(cell1)
top.add(cell2,origin = (0,height))
# ref1 = core.CellReference(cell1)
# top.add(ref1)
# top.add(cell1)
polygon = Polygon([(0, 0), (1, 1), (1, 0)])
print polygon.exterior.coords.xy

# # Create a layout and add the cell
layout = core.Layout('LIBRARY')
layout.add(top)

# # Save the layout and then display it on screen
# layout.save('output.gds')
layout.show()
