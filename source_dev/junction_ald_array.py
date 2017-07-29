import numpy as np
import gdsCAD as cad
import dc_24pin

class Junctionchip():

    def __init__(self, name, dict_pads, dict_junctions, x0 = -100, y0 = -1700, 
        tlength = None):
        '''
        Class for ALD JJs. These are vertical tunnel barriers with a two-step process.
        '''
 
        self.name = name
        self.dict_pads = dict_pads
        self.dict_junctions = dict_junctions
        self.x0 = x0
        self.y0 = y0
        self.tlength = tlength

        self.layer_bottom = 1
        self.layer_top = 2

    def gen_junctions(self):
        '''
        Consists of a centerline that spreads out to 6 individual junctions
        First creates bottom row of JJs, finally uses dc_24pin to generate the full 4x4 array
        '''
        
        padwidth = self.dict_pads['width']
        padlength = self.dict_pads['length']
        padspace = self.dict_pads['spacing']
        triheight = self.dict_pads['triheight']
        tripeak = self.y0 + padlength + triheight

        jjwidth = self.dict_junctions['width']
        jjmin = self.dict_junctions['jjmin']
        jjmax = self.dict_junctions['jjmax']
        jjstep = self.dict_junctions['jjstep']
        jjlength = np.arange(jjmin,jjmax+1,jjstep)
        amount = len(jjlength)
        
        if self.tlength==None:
            self.tlength = (padwidth+padspace)*(amount)/2-padwidth/2

        cwidth = 20
        source = 200
        centerpoints = [(0, tripeak - cwidth / 2),
                        (0, tripeak + source + cwidth / 2),
                        (self.tlength, tripeak + source + cwidth / 2),
                        (- self.tlength, tripeak + source + cwidth / 2)]
        centerline = cad.core.Path(centerpoints, cwidth, layer = self.layer_bottom)

        self.padgroup = [cad.core.Cell('padgroup')] * 2
        self.padgroup[0].add(centerline)

        for k,i in zip(jjlength,range(-amount/2+1,amount/2+2)):
            if i>=0:
                k=k-1
            xs = (padwidth + padspace) * i
            junctionpoints = [(xs, tripeak - jjwidth / 2),
                            (xs, tripeak + source),
                            (xs, tripeak + source + k)]
            junction = cad.core.Path(junctionpoints, jjwidth, layer = self.layer_top)
            junction_label = cad.shapes.LineLabel(k,200,(xs-padwidth/2,-2e3), layer=self.layer_top)

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
                self.padgroup[ll-1].add(junction_label)

        # Create full array by inputting bottom junction row into dc_24pin method gen_full_array
        self.cell = dc_24pin.gen_full_array(padgroup = self.padgroup)



