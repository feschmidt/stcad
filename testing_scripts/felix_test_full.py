import numpy as np
import gdsCAD as cad
from source_dev.chip import Base_Chip



### Add individual designs to big chip
chip = Base_Chip('full_mask',xdim=25000,ydim=25000,wafer=False)
chip.add_component(chip_sub1,(-5000,5000))
chip.add_component(chip_sub2,(5000,5000))
chip.add_component(chip_sub3,(-5000,-5000))

### Add dicing markers for RF
for pos in [(0,-10e3),(0,0),(0,10e3)]:
    chip.add_dicing_marker(pos=pos,vert=False)
for pos in [(-10e3,0),(0,0),(10e3,0)]:
    chip.add_dicing_marker(pos=pos,hor=False)

### Add dicing markers for DC
chip.add_dicing_marker(pos=(-5e3,5e3),span=[(-10e3,10e3),(-10e3,10e3)])

# chip.add_TUlogo()
chip.save_to_gds(show = False, save = True)
