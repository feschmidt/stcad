import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad
import os, inspect
current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

chipsize = 250
chip = Base_Chip('CPW', chipsize, chipsize,label=False)
cp = CPW([[-100,-50],[-50,-50],[-50,0],[50,0],[50,-50],[0,-50]],pin=3,gap=5)
print cp.length
cp.add_launcher('beginning')
cp.add_open('end')
chip.add_component(cp, (0,0))
chip.save_to_gds(show=True, save=True,loc='')