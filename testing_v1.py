import numpy as np
import funcs.jjarray as jjarray
import funcs.squidarray as squidarray

dict_pads = {'width': 200,
            'length': 300,
            'spacing': 300,
            'triheight': 100}

dict_junctions = {'width': 20,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}

dict_squids = {'width': 20,
                'jjmin': 1,
                'jjmax': 7,
                'jjstep': 1}

#testf = jjarray.Junctionchip('testjunctions',dict_pads,dict_squids, x0 = -100,
#        y0 = -2200, tlength = 1600, chipsize = 6000)
#testf.gen_junctions(marker = False, vernier = False, testpads = True)

testf = squidarray.Junctionchip('testsquids',dict_pads,dict_squids, x0 = -100,
        y0 = -2200, tlength = 1600, chipsize = 6000)
testf.gen_squids(lsquid = 50, hsquid = 50, marker = False, vernier = False,
        testpads = True)
testf.save_to_gds(save=False)