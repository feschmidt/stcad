import numpy as np
import gdsCAD as cad
from . import dc_24pin

class Junctionchip():

    def __init__(self,name):
        '''
        Class for Graphene JJs with bottom gate.
        '''

        self.layer_base = 1
        self.layer_gateins = 2
        self.layer_protect = 3
        self.layer_etch = 4
        
        self.cell = cad.core.Cell('GRAPHENE_JJs')

    def gen_junctions(self):
        '''
        Consists of a centerline that spreads out to 6 individual junctions
        First creates bottom row of JJs, finally uses dc_24pin to generate the full 4x4 array
        '''
        
        self.padwidth = 200.
        self.padlength = self.padwidth
        self.padspace = 10.
        self.gaplength = 100.
        self.gapheight = 6.2
        self.gatelength = 60.
        self.holelength = 95.
        self.holeheight = 10.+2*self.gapheight 
        self.gatelead = 15.
        self.sourcelead = 40.

        jjwidth = np.arange(0.5,5.5,0.5)    # width in um
        bilayer = np.arange(0.05, 0.5, 0.05)    # lead spacing in um
        HSQ_1 = bilayer + 2*0.05        # 50nm overlap on each side
        gatewidth = HSQ_1 + 2*0.05
        HSQ_0 = gatewidth + 2*0.1       # 100nm overlap for gate insulation
        dist_gate = 0.2
        dist_ins = 0.3
        dist_protect = 0.05
        dist_etch = 0.05
        
        xspace = 800
        yspace = 800
        xshift = 1800
        yshift = 1500
        
        
        for k,gate in enumerate(gatewidth):
            for l,jj in enumerate(jjwidth):
                element = cad.core.Cell('ELEMENT')      # Only a cell_obj can be moved around when added to another cell. Clearing necessary
                gatepattern = self.gen_gate(gate,jj,dist_gate)
                element.add(gatepattern)
                pads = self.gen_bondpads()
                element.add(pads[0])
                element.add(pads[1])
                gateins = self.gen_gateins(gate,jj,dist_ins)
                element.add(gateins)
                protect = self.gen_gprotect(gate,jj,dist_protect)
                element.add(protect)
                etch = self.gen_jjetch(gate,jj,dist_etch,dist_protect)
                element.add(etch[0])
                element.add(etch[1])
                label = self.gen_label(str(gate)+' x '+str(jj))
                element.add(label)
                self.cell.add(element,origin=(k*xspace + xshift,l*yspace + yshift))
    
    def gen_gate(self,gate,jj,dist_gate):
        '''
        Create bottom gate with close metal leads
        '''
        gatepoints = [(self.holelength, 0), (self.holelength, self.gapheight),
                            (self.holelength - self.gatelength, self.gapheight),
                            (self.holelength - self.gatelength, self.gapheight + gate),
                            (self.holelength - 40, self.gapheight + gate),
                            (self.holelength - self.gatelead, self.holeheight - self.gapheight),
                            (self.holelength, self.holeheight - self.gapheight),
                            (self.holelength, self.holeheight),
                            (0, self.holeheight),
                            (0, self.holeheight - self.gapheight),
                            (self.sourcelead + jj, self.holeheight - self.gapheight),
                            (self.sourcelead + jj, self.gapheight + gate + dist_gate),
                            (self.sourcelead, self.gapheight + gate + dist_gate),
                            (self.sourcelead, self.gapheight + 5.0),
                            (self.sourcelead - 20.0, self.gapheight + 5.0),
                            (0, self.gapheight),
                            (0,0),
                            (self.sourcelead, 0),
                            (self.sourcelead, self.gapheight - dist_gate),
                            (self.sourcelead + jj, self.gapheight - dist_gate),
                            (self.sourcelead + jj, 0)]
        gatespace = cad.core.Boundary(gatepoints, layer = self.layer_base)
        return gatespace

    def gen_gateins(self,gate,jj,dist_ins):
        inspoints = [(self.sourcelead - 1, self.gapheight - dist_ins),
                    (self.sourcelead + jj + 1, self.gapheight + gate + dist_ins)]
        insspace = cad.shapes.Rectangle(inspoints[0], inspoints[1], layer = self.layer_gateins)
        return insspace
    
    def gen_gprotect(self,gate,jj,dist_protect):
        gpoints = [(self.sourcelead, self.gapheight + dist_protect),
                    (self.sourcelead + jj, self.gapheight + gate - dist_protect)]
        gspace = cad.shapes.Rectangle(gpoints[0],gpoints[1], layer = self.layer_protect)
        return gspace
        
    def gen_jjetch(self,gate,jj,dist_etch,dist_protect):
        jjpart1 = [(self.sourcelead, 0),
                    (self.sourcelead + jj, self.gapheight + dist_etch + dist_protect)]
        jjpart2 = [(0, self.holeheight - self.gapheight),
                    (self.sourcelead + jj, self.holeheight - self.gapheight),
                    (self.sourcelead + jj, self.gapheight + gate - dist_etch - dist_protect),
                    (self.sourcelead, self.gapheight + gate - dist_etch - dist_protect),
                    (self.sourcelead, self.gapheight + 5.0),
                    (self.sourcelead - 20.0, self.gapheight + 5.0),
                    (0, self.gapheight)]
        jj1 = cad.shapes.Rectangle(jjpart1[0],jjpart1[1],layer=self.layer_etch)
        jj2 = cad.core.Boundary(jjpart2, layer=self.layer_etch)
        return (jj1, jj2)
    
    def gen_bondpads(self):
        pad1points = [(6.2,0),(6.2,-100),(-200,-100),(-200,100),(6.2,100),(6.2,self.holeheight),
                    (0, self.holeheight),(0,100-6.2),(-200+6.2,100-6.2),(-200+6.2,-100+6.2),
                    (0,-100+6.2),(0,0)]
        pad2points = [(self.sourcelead+10,0), (self.sourcelead + 10, -6.2), (self.sourcelead+10+200, -6.2),
                    (self.sourcelead+10+200,-200), (self.sourcelead-5,-200), (self.sourcelead-5,0),
                    (self.sourcelead-5-6.2,0), (self.sourcelead-5-6.2,-200-6.2),
                    (self.sourcelead+10+200+6.2,-200-6.2), (self.sourcelead+10+200+6.2,0)]
        pad1 = cad.core.Boundary(pad1points, layer = self.layer_base)
        pad2 = cad.core.Boundary(pad2points, layer = self.layer_base)
        return (pad1, pad2)
        
    def gen_label(self,label):
        label_element = cad.shapes.LineLabel(label,30, (100,-150), layer=self.layer_base)
        return label_element



