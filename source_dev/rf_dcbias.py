import numpy as np
import gdsCAD as cad
import utilities as utils

class RFShunt():
    """
    Class for RF DC bias cavities
    Initial values:
        - termination = "open". Other good values are "short" (to GND) or "squid"
    """

    def __init__(self, name, dict_dcbias, termination = "open"):

        self.name = name
        self.dict_dcbias = dict_dcbias
        self.length = self.dict_dcbias['length']
        self.pos = self.dict_dcbias['position']    # (x0,y0)
        self.feedlength = self.dict_dcbias['feedlength']
        self.shunt = self.dict_dcbias['shunt']     # (basex,basey,insoverlap,topx,topy)
        self.termination = termination
        if termination=='squid':
            self.squid = self.dict_dcbias['squid']     # (loopx,loopy,jwidth,loopwidth)

        self.centerwidth = self.dict_dcbias['centerwidth']
        self.gapwidth = self.dict_dcbias['gapwidth']

        self.layer_bottom = 1
        self.layer_top = 2
        self.layer_ins = 3
        

        # hard coded values
        self.radius = 1000

        self.cell = cad.core.Cell('RF CELL')

    def gen_full(self):
        """
        Generate four DC bias cavities with option to have squids at the end
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        feedlength = self.feedlength
        length = self.length

        # Generate first cavity
        rfcell = cad.core.Cell('RESONATOR')
        resonator = self.gen_cavity(x0,y0,feedlength,self.squid)
        rfcell.add(resonator)

        self.cell.add(rfcell)

        # Add the other three as copies of the first one
        self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))
        self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),rotation = 180))
        self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),rotation=180,x_reflection=True))

        return self.cell


    def gen_partial(self, loc):
        """
        Generate one DC bias cavity with specified loc(ation)
        values for loc: sw, se, ne, nw
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        feedlength = self.feedlength
        length = self.length

        # Generate first cavity
        rfcell = cad.core.Cell('RESONATOR')
        resonator = self.gen_cavity(x0,y0,feedlength,self.squid)
        rfcell.add(resonator)

        if loc == 'sw':
            self.cell.add(rfcell)
        elif loc == 'nw':
            self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))
        elif loc == 'ne':
            self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),rotation = 180))
        elif loc == 'se':
            self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),rotation=180,x_reflection=True))
        else:
            raise ValueError("loc(ation) is invalid. Allowed values are sw, nw, ne, se.")

        return self.cell


    def gen_cavity(self, x0, y0, feedlength, squid):
        """
        Generate baselayer with SQUID (optional)
        """

        self.bias_cell = cad.core.Cell('RF_DC_BIAS')
        
        # Create feed to shunt
        part1points = [(x0, y0),
                    (x0+feedlength, y0),
                    (x0+feedlength, y0+self.gapwidth),
                    (x0, y0+self.gapwidth)]
        part1 = cad.core.Boundary(part1points, layer=self.layer_bottom)
        part11 = cad.utils.reflect(part1,'x',origin=(0,y0+self.gapwidth+self.centerwidth/2.))
        
        
        # Create shunt
        x1 = x0+feedlength
        y1 = y0
        shunt = self.gen_shunt_full((x1,y1))
        
        # Connect shunt to first turn
        x2 = x1+self.shunt[0]+2*self.gapwidth
        y2 = y0
        part2l = 2e3
        part2points = [(x2, y2),
                    (x2+part2l, y2),
                    (x2+part2l, y2+self.gapwidth),
                    (x2, y2+self.gapwidth)]
        part2 = cad.core.Boundary(part2points, layer=self.layer_bottom)
        part21 = cad.utils.reflect(part2,'x',origin=(0,y2+self.gapwidth+self.centerwidth/2.))
        
        # Create first turn
        x3 = x2+part2l
        y3 = y0
        radius1 = self.radius                
        curve1 = cad.shapes.Disk((x3,y3+self.gapwidth+self.centerwidth+radius1), radius=radius1, inner_radius=radius1-self.gapwidth, initial_angle=270,final_angle=360, layer=self.layer_bottom)
        
        radius11 = self.radius + self.gapwidth + self.centerwidth
        curve11 = cad.shapes.Disk((x3,y3+radius11), radius=radius11, inner_radius=radius11-self.gapwidth, initial_angle=270,final_angle=360, layer=self.layer_bottom)
        
        # Connect first turn to second turn
        x4 = x3+radius11
        y4 = y3+radius11
        part3l = 1e3
        part3points = [(x4, y4),
                    (x4, y4+part3l),
                    (x4-self.gapwidth, y4+part3l),
                    (x4-self.gapwidth, y4)]
        part3= cad.core.Boundary(part3points, layer=self.layer_bottom)
        part31 = cad.utils.reflect(part3,'y',origin=(x4-self.gapwidth-self.centerwidth/2.,0))

        # Create second turn by copying first turn
        x5 = x3
        y5 = y4 + part3l/2
        curve2 = cad.utils.reflect(curve1,'x',origin=(0,y5))
        curve21 = cad.utils.reflect(curve11,'x',origin=(0,y5))

        # Add final length
        x6 = x3
        y6 = y5 + radius11 + part3l/2 - 2*self.gapwidth - self.centerwidth
        
        radius_cav = radius1 + self.gapwidth + self.centerwidth/2
        part4l = self.length - part2l - np.pi*radius_cav - part3l
        if part4l<0:
            raise ValueError("Cavity length is too short! Partial cavity length already exceeds desired value.")

        part4points = [(x6, y6),
                    (x6-part4l, y6),
                    (x6-part4l, y6+self.gapwidth),
                    (x6, y6+self.gapwidth)]
        part4 = cad.core.Boundary(part4points, layer=self.layer_bottom)
        part41 = cad.utils.reflect(part4,'x',origin=(0,y6+self.gapwidth+self.centerwidth/2.))
        

        # Add all elements to cell
        for toadd in [part1, part11,
                    shunt,
                    part2, part21, curve1, curve11,
                    part3, part31, curve2, curve21,
                    part4, part41]:
            self.bias_cell.add(toadd)

        # Add Box (optional) or SQUID (optional) at the end
        if self.termination == "short":
            print "Termination: Short to ground"
        elif self.termination == "open":
            x7 = x6-part4l
            y7 = y6+self.gapwidth+self.centerwidth/2
            boxx = 100
            boxy = 40
            endboxpoints = [(x7, y7),
                    (x7, y7-boxy),
                    (x7-boxx, y7-boxy),
                    (x7-boxx, y7+boxy),
                    (x7,y7+boxy)]
            endbox = cad.core.Boundary(endboxpoints, layer= self.layer_bottom)
            self.bias_cell.add(endbox)
            print "Termination: Open to ground"
        elif self.termination == "squid":
            squid1 = self.gen_squid_base((x6-part4l,y6+self.gapwidth),(100,40))
            squid2 = self.gen_squid_top((x6-part4l,y6+self.gapwidth+self.centerwidth/2.),(100,40))
            self.bias_cell.add(squid1)
            self.bias_cell.add(squid2)
            print "Termination: SQUID "+str(self.squid[2])+" "+str(self.squid[0])+'x'+str(self.squid[1])+" to ground"
        else:
            raise ValueError("Wrong termination specified. Good values are short (default), open, squid.")



        return self.bias_cell

    def gen_shunt_full(self,pos):
        """
        Creates a shunt capacitor from center conductor to ground
        """
        x0 = pos[0]
        y0 = pos[1]

        shuntcell = cad.core.Cell('SHUNT')
        shuntbase = self.gen_shunt_base((x0,y0))
        shunttop = self.gen_shunt_top((x0+self.gapwidth+self.shunt[0]/2-self.shunt[3]/2,y0+self.gapwidth+self.centerwidth/2-self.shunt[4]/2))
        shuntins = self.gen_shunt_ins((x0+self.gapwidth+self.shunt[0]/2-self.shunt[3]/2,y0+self.gapwidth+self.centerwidth/2-self.shunt[4]/2))
        [shuntcell.add(toadd) for toadd in [shuntbase, shuntins, shunttop]]
        return shuntcell

    def gen_shunt_base(self,pos):
        """
        Base layer for shunt
        """
        x0 = pos[0]
        y0 = pos[1]

        shuntbase = cad.core.Cell('shuntbase')
        shuntpoints = [(x0, y0+self.gapwidth),
                     (x0, y0-self.shunt[1]/2.),
                     (x0+self.shunt[0]+2*self.gapwidth, y0-self.shunt[1]/2.),
                     (x0+self.shunt[0]+2*self.gapwidth, y0+self.gapwidth),
                     (x0+self.shunt[0]+self.gapwidth, y0+self.gapwidth),
                     (x0+self.shunt[0]+self.gapwidth, y0+self.gapwidth-self.shunt[1]/2.),
                     (x0+self.gapwidth, y0+self.gapwidth-self.shunt[1]/2.),
                     (x0+self.gapwidth, y0+self.gapwidth)]
        shunt1 = cad.core.Boundary(shuntpoints, layer=self.layer_bottom)
        shunt11 = cad.utils.reflect(shunt1,'x',origin=(0,y0+self.gapwidth+self.centerwidth/2.))
        shuntbase.add(shunt1)
        shuntbase.add(shunt11)
        return shuntbase
      

    def gen_shunt_ins(self,pos):
        """
        Returns insulating slab for shunt capacitors
        """
        x0 = pos[0]
        y0 = pos[1]

        shuntins = cad.core.Cell('shuntins')
        shuntpoints = [(x0-self.shunt[2],y0-self.shunt[2]),
                    (x0+self.shunt[3]+self.shunt[2],y0+self.shunt[4]+self.shunt[2])]
        shunt = cad.shapes.Rectangle(shuntpoints[0], shuntpoints[1], layer=self.layer_ins)
        shuntins.add(shunt)
        return shuntins


    def gen_shunt_top(self,pos):
        """
        Returns top plate for shunt capacitors
        """
        x0 = pos[0]
        y0 = pos[1]

        shunttop = cad.core.Cell('shunttop')
        shuntpoints = [(x0,y0),
                    (x0+self.shunt[3],y0+self.shunt[4])]
        shunt = cad.shapes.Rectangle(shuntpoints[0], shuntpoints[1], layer=self.layer_top)
        shunttop.add(shunt)
        return shunttop


    def gen_squid_base(self,pos,boxdim):
        """
        Method to add SQUID at the end of the resonator. Uses all input variables specified in dict_dcbias
        pos: x0, y0
        """

        x0 = pos[0]
        y0 = pos[1]
        boxx = boxdim[0]
        boxy = boxdim[1]

        squidcell = cad.core.Cell('SQUIDBASE')
        squidpoints = [(x0, y0),
                    (x0-2*self.squid[0], y0),
                    (x0-2*self.squid[0], y0-0.6*self.squid[1]),
                    (x0-2*self.squid[0]-2*self.squid[3], y0-0.6*self.squid[1]),
                    (x0-2*self.squid[0]-2*self.squid[3], y0+self.centerwidth/2.),
                    (x0-boxx, y0+self.centerwidth/2.),
                    (x0-boxx, y0+self.centerwidth/2.-boxy),
                    (x0, y0+self.centerwidth/2.-boxy)]
        squidbase1 = cad.core.Boundary(squidpoints, layer=self.layer_bottom)
        squidbase11 = cad.utils.reflect(squidbase1,'x',origin=(0,y0+self.centerwidth/2.))
        squidcell.add(squidbase1)
        squidcell.add(squidbase11)
        return squidcell


    def gen_squid_top(self,pos,boxdim):
        """
        Top layer of SQUID at resonator end
        """

        x0 = pos[0]-2*self.squid[0]-2*self.squid[3]
        y0 = pos[1]
        boxx = boxdim[0]-2*self.squid[0]-2*self.squid[3]
        boxy = boxdim[1]
        overlap = 40

        squidcell = cad.core.Cell('SQUIDTOP')
        squidpoints = [(x0+self.squid[2],y0-self.squid[1]/2.),
                    (x0+self.squid[2], y0-self.squid[1]/2.-self.squid[3]),
                    (x0-self.squid[0]-self.squid[3], y0-self.squid[1]/2.-self.squid[3]),
                    (x0-self.squid[0]-self.squid[3], y0-self.squid[3]/2.),
                    (x0-boxx, y0-self.squid[3]/2.),
                    (x0-boxx, y0-overlap),
                    (x0-boxx-2*overlap, y0-overlap),
                    (x0-boxx-2*overlap, y0),
                    (x0-self.squid[0], y0),
                    (x0-self.squid[0], y0-self.squid[1]/2.)]
        squidtop1 = cad.core.Boundary(squidpoints, layer=self.layer_top)
        squidtop11 = cad.utils.reflect(squidtop1,'x',origin=(0,y0))
        squidcell.add(squidtop1)
        squidcell.add(squidtop11)
        return squidcell


    def gen_label(self,pos):
        """
        Generate label with termination type
        if squid: squid wJJ x wlead \n wSQUID x lSQUID \n cavlength
        """
        labelcell = cad.core.Cell('DEV_LABEL')
        if self.termination=='squid':
            label = cad.shapes.LineLabel(self.termination+' '+str(self.squid[2])+'x'+str(self.squid[3])+\
                                            '\n'+str(self.squid[0])+'x'+str(self.squid[1])+\
                                            '\n'+str(self.length),100,
                                         (pos[0],pos[1]),line_width=5,layer=self.layer_bottom)
        labelcell.add(label)
        return labelcell




