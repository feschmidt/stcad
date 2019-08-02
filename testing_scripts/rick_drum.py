import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad


from stcad.source_dev.drums import *

chip = Base_Chip('drum_selection', 1200, 300,label=False)


position = [0,0]
array_separation = 50
drum1 = circ_gap_drum(drum_size=30,tether_width=4,number_of_tethers=10,
        release_holes_diameter = 1, release_holes_pitch = 20,release_holes_area_radius = 100)
drum1.translate(position=position)
drum1.add_to_chip(Base_Chip=chip)

position = [drum1._bounding_box[1,0]+array_separation,0]
drum2 = circular_drum2(tether_width=0.5, drum_gap=2, drum_size=5)
drum2.translate(position=position)
drum2.add_to_chip(Base_Chip=chip)

position = [drum2._bounding_box[1,0]+array_separation,0]
drum3 = rounded_base_drum3(tether_width=0.5, drum_gap=1, drum_size=20, corner_rad = 0.5, nr_of_points = 20)
drum3.translate(position=position)
drum3.add_to_chip(Base_Chip=chip)

position = [drum3._bounding_box[1,0]+array_separation,0]
drum4 = rounded_base_drum4(tether_width=0.5, drum_gap=2, drum_size=5,corner_rad = 1, nr_of_points = 20)
drum4.translate(position=position)
drum4.add_to_chip(Base_Chip=chip)

position = [drum4._bounding_box[1,0]+array_separation,0]
drum5 = rounded_base_drum5(tether_width=0.5, drum_gap=2, drum_size=5,corner_rad = 1, nr_of_points = 20)
drum5.translate(position=position)
drum5.add_to_chip(Base_Chip=chip)

position = [drum5._bounding_box[1,0]+array_separation,0]
drum6 = rounded_base_drum4(tether_width=1, drum_gap=5, drum_size=10,corner_rad = 1, nr_of_points = 20)
drum6.translate(position=position)
drum6.add_to_chip(Base_Chip=chip)

position = [drum6._bounding_box[1,0]+array_separation,0]
drum7 = rounded_base_drum5(tether_width=2, drum_gap=15, drum_size=40,corner_rad = 1, nr_of_points = 20)
drum7.translate(position=position)
drum7.add_to_chip(Base_Chip=chip)

position = [drum7._bounding_box[1,0]+array_separation,0]
drum8 = circ_gap_drum(drum_size=20,tether_width=4,number_of_tethers=7)
drum8.translate(position=position)
drum8.add_to_chip(Base_Chip=chip)

# ------------------------------------------- Array End ----------------------------------

chip.save_to_gds(show=False, save=True,loc='')