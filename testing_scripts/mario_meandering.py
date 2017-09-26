import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad
import os, inspect
current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

chipsize = 250
chip = Base_Chip('line', chipsize, chipsize,label=False)
cp = MeanderingLine()
chip.add_component(cp, (0,0))
chip.save_to_gds(show=True, save=False,loc='')