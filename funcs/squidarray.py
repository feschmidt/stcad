import numpy as np
import gdsCAD as cad
import basechip

class Junctionchip():

    def __init__(self, name, dict_pads, dict_junctions, chipsize, x0 = -100, y0 = -2200, 
        tlength = 1600):

        self.base = basechip.BaseChip(l=chipsize)
        self.chip = self.base.base_chip()
    
        self.name = name
        self.dict_pads = dict_pads
        self.dict_junctions = dict_junctions
        self.x0 = x0
        self.y0 = y0
        self.tlength = tlength

        self.layer_bottom = 1
        self.layer_top = 2

    def gen_squids(self, lsquid, hsquid, marker = True, vernier = True, testpads = True,
                        save = True, show = True):
        
        padwidth = self.dict_pads['width']
        padlength = self.dict_pads['length']
        padspace = self.dict_pads['spacing']
        triheight = self.dict_pads['triheight']
        tripeak = self.y0 + padlength + triheight

        jjwidth = self.dict_junctions['width']
        jjmin = self.dict_junctions['jjmin']
        jjmax = self.dict_junctions['jjmax']
        jjstep = self.dict_junctions['jjstep']

        centerpoints = [(0, tripeak - jjwidth / 2),
                        (0, tripeak + 100 + jjwidth / 2 + hsquid),
                        (self.tlength, tripeak + 100 + jjwidth / 2 + hsquid),
                        (- self.tlength, tripeak + 100 + jjwidth / 2 + hsquid)]
        centerline = cad.core.Path(centerpoints, jjwidth, layer = self.layer_bottom)

        self.padgroup = [cad.core.Cell('bottom')] * 2
        self.padgroup[0].add(centerline)

        for k,i in enumerate(range(-3, 4)):
            xs = (padwidth + padspace) * i
            squid_left = cad.core.Path([[xs,tripeak-jjwidth/2],
                                    [xs,tripeak+hsquid],
                                    [xs-lsquid/2,tripeak+hsquid],
                                    [xs-lsquid/2,tripeak+2*hsquid+(k+1)*jjstep]],jjwidth, layer=self.layer_top)
            squid_right = cad.core.Path([[xs,tripeak-jjwidth/2],
                                    [xs,tripeak+hsquid],
                                    [xs+lsquid/2,tripeak+hsquid],
                                    [xs+lsquid/2,tripeak+2*hsquid+(k+1)*jjstep]],jjwidth, layer=self.layer_top)
            pad = cad.shapes.Rectangle((self.x0 + xs,self.y0),(self.x0 + padwidth + xs,self.y0 + padlength))
            tripoints = [[self.x0 + xs,self.y0 + padlength],
                        [self.x0 + padwidth / 2. + xs,tripeak],
                        [self.x0 + padwidth + xs, self.y0 + padlength]]
            tri = cad.core.Boundary(tripoints)

            if i==0:
                ll = self.layer_bottom
            else:
                ll = self.layer_top
                squid_hor = cad.core.Path([[xs-lsquid*2/3,tripeak+2*hsquid],
                                    [xs+lsquid*2/3,tripeak+2*hsquid]],jjwidth,layer=self.layer_bottom)
                squid_ver = cad.core.Path([[xs,tripeak+2*hsquid],
                                    [xs,tripeak+100+hsquid+jjwidth/2]],jjwidth,layer=self.layer_bottom)
            for toadd in [pad, tri, squid_ver, squid_hor]:
                if toadd==pad or toadd==tri:
                    toadd.layer = ll
                self.padgroup[ll-1].add(toadd)

            if i!=0:
                self.padgroup[ll-1].add(squid_left)
                self.padgroup[ll-1].add(squid_right)

        # Create full array by inputting bottom junction row into basechip method
        # gen_full_array
        self.layout = self.base.gen_full_array(padgroup = self.padgroup, marker = marker,
                                            vernier = vernier, testpads = testpads)

        # Save and show using base method save_to_gds
        #self.base.save_to_gds(chip = self.chip, layout = self.layout, name = 'testjunctions',
        #                    save = True, show = True)
        
        self.layout.save('test.gds')
## I routinely get a "TypeError: unhashable type: 'Layout'". Show works however??
    def save_to_gds(self, save = True, show = True):

        self.chip.add(self.layout)

        if save:    # doesn't work? unhashable type
            self.chip.save(self.name + '.gds')

        if show:
            #self.chip.save(self.name + '.png')
            self.chip.show()

