import numpy as np
import gdsCAD as cad
from . import dc_24pin

class SQUIDchip():

    def __init__(self, name, dict_pads, dict_junctions, x0 = -100, y0 = -1500, 
        tlength = None):
        '''
        Class for ALD SQUIDs. These are based on vertical tunnel barriers with a two-step process.
        dict_pads = {'padwidth': 200, 'padlength': 300, 'padspacing': 100, 'triheight': 100}
        dict_junctions = {'jjwidth': width, 'jjmin': jjmin, 'jjmax': jjmin+5*step, 'jjstep': step, 'location': 'n'}
        '''
 
        self.name = name
        for key,val in list(dict_pads.items()):
            setattr(self,key,val)
        for key,val in list(dict_junctions.items()):
            setattr(self,key,val)
        self.x0 = x0
        self.y0 = y0
        self.tlength = tlength

        self.layer_bottom = 1
        self.layer_top = 2

    def gen_junctions(self, dim = (50,50), doublepads=False, tbar_bot=True, jjleadwidth = 0):
        '''
        Consists of a centerline that spreads out to 6 individual SQUIDs
        First creates bottom row of JJs, finally uses dc_24pin to generate the full 4x4 array
        doublepads puts bondpads also on bottom layer everywhere
        '''
        
        tripeak = self.y0 + self.padlength + self.triheight

        if jjleadwidth!=0:
            jjleadwidth = jjleadwidth
        else:
            jjleadwidth = self.jjwidth
        jjlength = np.arange(self.jjmin,self.jjmax+self.jjstep,self.jjstep)
        amount = len(jjlength)

        if self.tlength==None:
            self.tlength = (self.padwidth+self.padspacing)*(amount)/2.-self.padwidth/2.
    
        cwidth = 20.
        drain = 100.
        source = 15.
        # Place drain strip (ground)
        if tbar_bot: #if using tbar geometry
            centerpoints = [(0, tripeak - cwidth / 2),
                            (0, tripeak + source + dim[1] + drain + cwidth / 2),
                            (self.tlength-5, tripeak + source + dim[1] + drain + cwidth / 2),
                            (- self.tlength, tripeak + source + dim[1] + drain + cwidth / 2)]
        else: # if just using a straight wire
            centerpoints = [(0, tripeak - cwidth / 2),
                        (0, tripeak + source + cwidth / 2),
                        (self.tlength, tripeak + source + cwidth / 2),
                        (- self.tlength, tripeak + source + cwidth / 2)]
        centerline = cad.core.Path(centerpoints, cwidth, layer = self.layer_bottom)

        self.padgroup = [cad.core.Cell('padgroup')] * 2
        self.padgroup[0].add(centerline)

        for k,i in zip(jjlength,list(range(-amount/2+1,amount/2+2))):
            if i>=0:
                k=k-self.jjstep
            xs = (self.padwidth + self.padspacing) * i
            # The actual squid
            if tbar_bot:
                extra = cwidth/2
            else:
                extra = 0
            squid_lead = cad.core.Path([[xs,tripeak-10*self.jjwidth], [xs,tripeak+source-dim[1]+extra]],jjleadwidth,layer=self.layer_top)
            squid_fork = cad.core.Path([[xs-dim[0]/2,tripeak+source+(k+.5)*self.jjstep+extra],
                                    [xs-dim[0]/2,tripeak+source-dim[1]+extra],
                                    [xs+dim[0]/2,tripeak+source-dim[1]+extra],
                                    [xs+dim[0]/2,tripeak+source+(k+.5)*self.jjstep+extra]],
                                    self.jjwidth, layer=self.layer_top)
            junction_label = cad.shapes.LineLabel(k,150,(xs-self.padwidth/2,self.y0-self.padlength), layer=self.layer_top)
            array_label = cad.shapes.LineLabel(self.jjwidth,150,(-100,self.y0-self.padlength), layer=self.layer_bottom)
            
            pad_bot = cad.shapes.Rectangle((self.x0 + xs,self.y0),(self.x0 + self.padwidth + xs,self.y0 + self.padlength), layer = self.layer_bottom)
            pad_top = cad.shapes.Rectangle((self.x0 + xs,self.y0),(self.x0 + self.padwidth + xs,self.y0 + self.padlength), layer = self.layer_top)
            tripoints = [[self.x0 + xs,self.y0 + self.padlength],
                        [self.x0 + self.padwidth / 2. + xs,tripeak],
                        [self.x0 + self.padwidth + xs, self.y0 + self.padlength]]
            tri = cad.core.Boundary(tripoints)

            if i==0:
                ll = self.layer_bottom
                if doublepads==False:
                    self.padgroup[ll-1].add(pad_bot)
            else:
                ll = self.layer_top
                # Horizontal and vertical tbar ground leads
                squid_hor = cad.core.Path([[xs-0.6*dim[0],tripeak+source+dim[1]+cwidth/2],
                                           [xs+0.6*dim[0],tripeak+source+dim[1]+cwidth/2]],
                                    cwidth,layer=self.layer_bottom)
                squid_ver = cad.core.Path([[xs,tripeak+source+dim[1]+cwidth/2],
                                           [xs,tripeak+source+dim[1]+cwidth/2+drain]],
                                    cwidth,layer=self.layer_bottom)
                if doublepads==False:
                    self.padgroup[ll-1].add(pad_top)
            if tbar_bot:
                for toadd in [squid_ver, squid_hor]:
                    self.padgroup[ll-1].add(toadd)
            tri.layer=ll
            self.padgroup[ll-1].add(tri)
            if doublepads==True:
                self.padgroup[ll-1].add(pad_bot)
                self.padgroup[ll-1].add(pad_top)

            if i!=0:
                self.padgroup[ll-1].add(squid_lead)
                self.padgroup[ll-1].add(squid_fork)
                self.padgroup[ll-1].add(junction_label)
        self.padgroup[0].add(array_label)
    
        # Create full array by inputting bottom junction row into dc_24pin method
        if self.location == 'all':
            self.cell = dc_24pin.gen_full_array(padgroup = self.padgroup)
        else:
            self.cell = dc_24pin.gen_partial(padgroup = self.padgroup, loc=self.location)




