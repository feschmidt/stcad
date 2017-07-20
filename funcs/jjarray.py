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

    def gen_junctions(self, marker = True, vernier = True, testpads = True,
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
                        (0, tripeak + 100 + jjwidth / 2),
                        (self.tlength, tripeak + 100 + jjwidth / 2),
                        (- self.tlength, tripeak + 100 + jjwidth / 2)]
        centerline = cad.core.Path(centerpoints, jjwidth, layer = self.layer_bottom)

        self.padgroup = [cad.core.Cell('bottom')] * 2
        self.padgroup[0].add(centerline)

        for k,i in enumerate(range(-3, 4)):
            xs = (padwidth + padspace) * i
            junctionpoints = [(xs, tripeak - jjwidth / 2),
                            (xs, tripeak + 100),
                            (xs, tripeak + 100 + (k + jjmin) * jjstep)]
            junction = cad.core.Path(junctionpoints, jjwidth, layer = self.layer_top)
            pad = cad.shapes.Rectangle((self.x0 + xs,self.y0),(self.x0 + padwidth + xs,self.y0 + padlength))
            tripoints = [[self.x0 + xs,self.y0 + padlength],
                        [self.x0 + padwidth / 2. + xs,tripeak],
                        [self.x0 + padwidth + xs, self.y0 + padlength]]
            tri = cad.core.Boundary(tripoints)

            if i==0:
                ll = self.layer_bottom
            else:
                ll = self.layer_top
            pad.layer = ll
            tri.layer = ll
            self.padgroup[ll-1].add(pad)
            self.padgroup[ll-1].add(tri)

            if i!=0:
                self.padgroup[ll-1].add(junction)

        # Create full array by inputting bottom junction row into basechip method
        # gen_full_array
        self.layout = self.base.gen_full_array(padgroup = self.padgroup, marker = marker,
                                            vernier = vernier, testpads = testpads)

        # Save and show using base method save_to_gds
        #self.base.save_to_gds(chip = self.chip, layout = self.layout, name = 'testjunctions',
        #                    save = True, show = True)

## I would like to move save_to_gds to basechip, but I routinely get a "TypeError: unhashable type: 'Layout'"
    def save_to_gds(self, save = True, show = True):

        self.chip.add(self.layout)

        if save:
            self.chip.save(self.name + '.gds')

        if show:
            self.chip.show()

