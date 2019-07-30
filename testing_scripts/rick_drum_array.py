import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad


from stcad.source_dev.drums import *

chipsize = 10000
chip = Base_Chip('TEST', chipsize, chipsize,label=False)


# --------------------------------------------- Array -----------------------------------

start_pos = [[-4000,4000],[100,4000],[-4000,0],[100,0]]
# start_pos = [[-4000,4000]]
array_separation = 200

array_indicators = ["A","B","C","D"]

for i in range(len(start_pos)):
	drum_sizes=[5,10,20,40]
	drum_gaps=[2,3,5,10,15]
	tether_widths=[.5,.8,1,2]

	# Array = simple_drum_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths, separation=100)
	# for i in range(len(Array.get_dependencies())):
	# 	chip.add(Array.get_dependencies()[i]._objects)

	position = start_pos[i]

	Array1 = simple_drum_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array1.translate(position=position)
	# Array1.add_labl()
	print(Array1._bounding_box)
	Array1.add_to_chip(Base_Chip=chip)
	position = [Array1._bounding_box[1,0]+array_separation,start_pos[i][1]]


	Array2 = rounded_base_drum4_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array2.translate(position=position)
	# Array2.add_labl(text = "RBD")
	Array2.add_to_chip(Base_Chip=chip)
	position = [Array2._bounding_box[1,0]+array_separation,start_pos[i][1]]


	Array4 = simple_drum3_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array4.translate(position=position)
	Array4.add_to_chip(Base_Chip=chip)
	position = [Array4._bounding_box[1,0]+array_separation,start_pos[i][1]]


	Array3 = simple_drum2_Array(drum_sizes = drum_sizes, drum_length = 30, drum_gaps = drum_gaps, tether_widths = tether_widths, tether_length=5,array_indicator=array_indicators[i])
	Array3.translate(position=position)
	Array3.add_to_chip(Base_Chip=chip)
	position = [Array3._bounding_box[1,0]+array_separation,start_pos[i][1]]


	Array5 = circular_drum2_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array5.translate(position=position)
	Array5.add_to_chip(Base_Chip=chip)
	position = [Array5._bounding_box[1,0]+array_separation,start_pos[i][1]]

	Array7 = rounded_base_drum5_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array7.translate(position=position)
	# Array2.add_labl(text = "RBD")
	Array7.add_to_chip(Base_Chip=chip)
	position = [Array7._bounding_box[1,0]+array_separation,start_pos[i][1]]

	drum_sizes=[20,30,50,100]
	drum_gaps=[1,2,3,5]
	tether_widths=[.5,.8,1,1.5]
	Array6 = rounded_base_drum3_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array6.translate(position=position)
	# Array2.add_labl(text = "RBD")
	Array6.add_to_chip(Base_Chip=chip)
	position = [Array6._bounding_box[1,0]+array_separation,start_pos[i][1]]

# ------------------------------------------- Array End ----------------------------------

# # ------------------------------------------- Single drums -------------------------------
# # Choose a drum type from the available classes in source_dev.drums
# drum = circ_gap_drum(drum_size=5, tether_width=0.5, number_of_tethers=8)
# array_indicators = ["A","B","C","D"]
# drum_sizes=[2,5,8,10]
# numbers_of_tethers=[4,5,6,7,8]
# tether_widths=[.5,.8,1,1.5]
# Array6 = circ_gap_drum_Array(drum_sizes=drum_sizes,tether_widths=tether_widths, numbers_of_tethers= numbers_of_tethers, array_indicator="A")
# # Array6.translate(position=position)
# # Array2.add_labl(text = "RBD")
# #Array6.add_to_chip(Base_Chip=chip)
# # position = [Array6._bounding_box[1,0]+array_separation,start_pos[i][1]]

# print(drum.bounding_box())
# print(drum.elements)
# print(drum._objects[1])
# print(len(drum.elements))
# print(drum.name)
# drum.add_to_chip(Base_Chip = chip)
# Array6.add_to_chip(Base_Chip = chip)
# # for i in range(len(drum.elements)):
# # 	chip.add(drum._objects[i])
# # chip.add(drum._objects)


chip.save_to_gds(show=True, save=True,loc='')