from gdsCAD import *
from gdsCAD.shapes import Rectangle
from gdsCAD.core import Path, Cell

# Create a Cell and add the box
maincell = core.Cell('MAIN')

cell=core.Cell('GUIDES')
# Layer 0: 6x6mm chip
l = 6000
box=shapes.Box((-l/2,-l/2), (l/2,l/2), width=20, layer=0)
cell.add(box)

hbar = Cell('HALL_BAR')

# Build the channel
hwidth = 200
hlength = 400
hbar.add(Rectangle((-hlength/2, -hwidth/2), (hlength/2,hwidth/2),layer=1))

# Build a pad
pad = Cell('PAD')
padwidth = 100
padlength = 100
pad.add(Rectangle((-padlength/2,-padwidth/2), (padlength/2,padwidth/2),layer=2))
hbar.add(Rectangle((-hlength/2-padlength,-padwidth/2),(-hlength/2,padwidth/2),layer=2))
hbar.add(Rectangle((hlength/2,-padwidth/2),(hlength/2+padlength,padwidth/2),layer=2))


# Copy the pads
for i in [-1,1]:
    x = -padlength*0.75 * i
    ys = hwidth/2+padwidth

    for y in (ys, -ys):
        # Add a connecting trace
        hbar.add(Path(((x,y), (x,0)), width=10))
        # Add a pad
        hbar.add(pad, (x,y))

#hbar.show()

maincell.add(cell)
maincell.add(hbar)
maincell.show()