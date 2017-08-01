import numpy as np
from source_dev.chip import Base_Chip
from source_dev.junction_graphene_array import Junctionchip

              

name_jj = 'gJJ test'
jjs = Junctionchip(name_jj)
jjs.gen_junctions()
chipjj = Base_Chip(name_jj,xdim=10e3,ydim=10e3,frame=True)
chipjj.add_component(jjs.cell,(-5e3,-5e3))
chipjj.add_ebpg_marker(size = 10, pos = (-1800,-1700))
chipjj.add_ebpg_marker(size = 20, pos = (-3000,-1700))
chipjj.save_to_gds(show = False, save = True)
