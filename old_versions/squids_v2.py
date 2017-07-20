import os.path
from gdsCAD import *
import numpy as np

# Create a Cell and add the box
maincell = core.Cell('MAIN')

cell=core.Cell('GUIDES')
# Layer 0: 6x6mm chip
l = 6000
box=shapes.Box((-l/2,-l/2), (l/2,l/2), width=20, layer=0)
cell.add(box)


padwidth = 200
padlength = 300
padspace = 300
x0 = -100
y0 = -2200
triheight = 100
tripeak = y0+padlength+triheight
w1=10
l1 = 100
hsquid = 50
lsquid = 50
tlength = 1500
jjstep = 1
padgroup = [core.Cell('bot')] * 2    #[0]: bottom, [1]: top
centerline = core.Path([[0,tripeak-10],[0,tripeak+l1+hsquid+w1/2],[tlength,tripeak+l1+hsquid+w1/2],[-tlength,tripeak+l1+hsquid+w1/2]],w1,layer=1,pathtype=0)
padgroup[0].add(centerline)

for k,i in enumerate(range(-3,4)):
    l=1
    xs = (padwidth + padspace) * i
    squid_left = core.Path([[xs,tripeak-10],[xs,tripeak+hsquid],[xs-lsquid/2,tripeak+hsquid],[xs-lsquid/2,tripeak+2*hsquid+(k+1)*jjstep]],w1)
    squid_right = core.Path([[xs,tripeak-10],[xs,tripeak+hsquid],[xs+lsquid/2,tripeak+hsquid],[xs+lsquid/2,tripeak+2*hsquid+(k+1)*jjstep]],w1)
    pad = shapes.Rectangle((x0+xs,y0),(x0+padwidth+xs,y0+padlength))
    tri = core.Boundary([[x0+xs,y0+padlength], [x0+padwidth/2.+xs,tripeak], [x0+padwidth+xs,y0+padlength]])
    if i==0:
        l=1
    else:
        l=2
        squid_hor = core.Path([[xs-lsquid*2/3,tripeak+2*hsquid],[xs+lsquid*2/3,tripeak+2*hsquid]],w1,layer=1)
    	squid_ver = core.Path([[xs,tripeak+2*hsquid],[xs,tripeak+l1+hsquid+w1/2]],w1,layer=1)
    pad.layer = l
    tri.layer = l
    squid_left.layer = l
    squid_right.layer = l
    for toadd in [pad,tri,squid_ver,squid_hor]:
    	padgroup[l-1].add(toadd)
    if i!=0:
        padgroup[l-1].add(squid_left)
        padgroup[l-1].add(squid_right)

# Merge objects into cells
bottom = [core.Cell('BOTTOM LAYER')] * 4
top = [core.Cell('TOP LAYER')] * 4
bottom[0].add(padgroup[0])
top[0].add(padgroup[1])
angle = [90,180,270]
for i in range(3):
	bottom[i+1] = core.CellReference(bottom[0], origin=(0,0),rotation=angle[i])
	top[i+1] = core.CellReference(top[0], origin=(0,0),rotation=angle[i])	

# Add alignment marks
marks = templates.AlignmentMarks(('A','C'),(1,2))
#marks = core.CellReference(amarks,magnification = 0.5)	# scale alignment marks
vernier0 = templates.Verniers(('A','B'),(1,2))
vernier = core.CellReference(vernier0).translate([-500,-500])

# Merge all cells
for toadd in [cell,bottom,top,marks,vernier]:
	maincell.add(toadd)

#block = templates.Block('ARRAY', maincell, (20000, 20000), spacing=None, edge_gap=0, prefix='')

# Create a layout and add the cell
layout = core.Layout('LIBRARY')
layout.add(maincell)
#layout.add(block)

# grid on 25x25mm chip
grid = core.Cell('GRID')
w_vals = [1, 2, 3]
spacing = 6000
'''
for (i, bottom) in enumerate(w_vals):
    for (j, top) in enumerate(w_vals):
        grid.add(maincell, origin = np.array([i,j])*spacing)
grid.show()
'''
# Save the layout and then display it on screen
#layout.save('squids_v2.gds')
layout.show()


