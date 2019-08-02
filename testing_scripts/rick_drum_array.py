import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad


from stcad.source_dev.drums import *

chipsize = 10000
chip = Base_Chip('TEST', chipsize, chipsize,label=False)


array_separation = 200


drum_sizes=[5,10]
drum_gaps=[5,15]
tether_widths=[.5,2]
start_pos = [-4000,4000]
position = [-4000,4000]

Array1 = simple_drum_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator="A")
Array1.translate(position=position)
# Array1.add_labl()
print(Array1._bounding_box)
Array1.add_to_chip(Base_Chip=chip)
position = [Array1._bounding_box[1,0]+array_separation,start_pos[1]]


Array2 = rounded_base_drum4_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator="A")
Array2.translate(position=position)
# Array2.add_labl(text = "RBD")
Array2.add_to_chip(Base_Chip=chip)
position = [Array2._bounding_box[1,0]+array_separation,start_pos[1]]


Array4 = simple_drum3_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator="A")
Array4.translate(position=position)
Array4.add_to_chip(Base_Chip=chip)
position = [Array4._bounding_box[1,0]+array_separation,start_pos[1]]


Array3 = simple_drum2_Array(drum_sizes = drum_sizes, drum_length = 30, drum_gaps = drum_gaps, tether_widths = tether_widths, tether_length=5,array_indicator="A")
Array3.translate(position=position)
Array3.add_to_chip(Base_Chip=chip)
position = [Array3._bounding_box[1,0]+array_separation,start_pos[1]]


Array5 = circular_drum2_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator="A")
Array5.translate(position=position)
Array5.add_to_chip(Base_Chip=chip)
position = [Array5._bounding_box[1,0]+array_separation,start_pos[1]]

Array7 = rounded_base_drum5_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator="A")
Array7.translate(position=position)
# Array2.add_labl(text = "RBD")
Array7.add_to_chip(Base_Chip=chip)
position = [Array7._bounding_box[1,0]+array_separation,start_pos[1]]

drum_sizes=[20,30,50,100]
drum_gaps=[1,2,3,5]
tether_widths=[.5,.8,1,1.5]
Array6 = rounded_base_drum3_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator="A")
Array6.translate(position=position)
# Array2.add_labl(text = "RBD")
Array6.add_to_chip(Base_Chip=chip)
position = [Array6._bounding_box[1,0]+array_separation,start_pos[1]]


chip.save_to_gds(show=False, save=True,loc='')