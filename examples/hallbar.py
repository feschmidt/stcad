from gdsCAD import *
from gdsCAD.shapes import Rectangle
from gdsCAD.core import Path, Cell

hbar = Cell('HALL_BAR')

# Build the channel
hbar.add(Rectangle((-50, -10), (50,10)))
#hbar.add(Rectangle((-50, -10), (-48, 10), layer=2))
#hbar.add(Rectangle((50, -10), (48, 10), layer=2))

# Build a pad
pad = Cell('PAD')
pad.add(Rectangle((-5,-5), (5,5)))
#pad.add(Rectangle((-2,-2), (2,2), layer=2))

# Copy the pads
for i in range(-2,3):
    x = -10 * i
    ys = 20 + 12 * (i%2)

    for y in (ys, -ys):
        # Add a connecting trace
        hbar.add(Path(((x,y), (x,0)), width=2))
        # Add a pad
        hbar.add(pad, (x,y))

hbar.show()