import numpy as np
import gdsCAD as cad
# from .utilities import utilities as utils
from .CPW import *
from .testing_fillet import fillet

class RFShunt():
    """
    Class for RF DC bias cavities
    Initial values:
        - termination = "open". Other good values are "short" (to GND) or "squid"
    """

    def __init__(self, name, dict_dcbias):

        self.name = name
        self.parts = (3000,3000,2000)
        self.turnradius = 1e3
        self.termination='open'
        self.boxdim = (100,40)
        self.maskmargin = 5

        self.layer_bottom = 1
        self.layer_ins = 2
        self.layer_top = 3

        self.shunttype = 0

        for key,val in list(dict_dcbias.items()):
            setattr(self,key,val)

        if self.termination=='squid':
            self.squid = self.dict_dcbias['squid']     # (loopx,loopy,jwidth,loopwidth)
        else:
            self.squid = False

        self.cell = cad.core.Cell('RF CELL')

    def gen_full(self,mask=True):
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
        if mask:
            rfmask = self.gen_holey_ground_mask()
            rfcell.add(rfmask)

        # Add the other three as copies of the first one
        rfcell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))
        rfcell.add(cad.core.CellReference(rfcell,origin=(0,0),rotation = 180))
        rfcell.add(cad.core.CellReference(rfcell,origin=(0,0),rotation=180,x_reflection=True))

        self.cell.add(rfcell)

        return self.cell


    def gen_partial(self, loc, mask=True):
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
        if mask:
            rfmask = self.gen_holey_ground_mask()
            rfcell.add(rfmask)

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
        self.feedlist = [[x0,y0],[x0+feedlength,y0]]
        feedpart = CPW(self.feedlist,pin=self.centerwidth,gap=self.gapwidth,layer=self.layer_bottom)
        
        # Create shunt
        x1 = x0+feedlength
        y1 = y0
        self.shunt1 = self.gen_shunt_full((x1,y1))
        
        CPWcell = cad.core.Cell('CPW')
        
        cpwlist = [(x1+self.shunt[0]+self.gapwidth,y0)]
        cpwlist.append((cpwlist[-1][0]+self.parts[0],cpwlist[-1][1]))
        cpwlist.append((cpwlist[-1][0],cpwlist[-1][1]+self.parts[1]))
        cpwlist.append((cpwlist[-1][0]-self.parts[2],cpwlist[-1][1]))
        
        self.cpwlist = cpwlist
        cpw = CPW(self.cpwlist,pin=self.centerwidth,gap=self.gapwidth,turn_radius=self.turnradius,layer=self.layer_bottom)
        self.cpwlength = cpw.length
        ### Not yet implemented:
        # print('Input length:', self.length)
        # print('Available xspace:', xspace)
        # print('Resonator length:', cpw.length)
        # print('Number of bends:', nbends)

        CPWcell.add(cpw)
        '''
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
        
        '''
        # Add all elements to cell
        for toadd in [feedpart, self.shunt1, CPWcell]:
            self.bias_cell.add(toadd)

        # Add Box (optional) or SQUID (optional) at the end
        x7 = self.cpwlist[-1][0]
        y7 = self.cpwlist[-1][1]
        
        if self.termination == "short":
            self.endboxpoints=[(x7,y7-self.boxdim[1]/2.),(x7,y7+self.boxdim[1]/2.)]
            print("Termination: Short to ground")
        elif self.termination == "open":
            self.endboxpoints=[(x7-self.boxdim[0],y7-self.boxdim[1]/2.),(x7,y7+self.boxdim[1]/2.)]
            endbox = cad.shapes.Rectangle(self.endboxpoints[0],self.endboxpoints[1])
            self.bias_cell.add(endbox)
            print("Termination: Open to ground")
        elif self.termination == "squid":
            squid1 = self.gen_squid_base((x6-part4l,y6+self.gapwidth),(100,40))
            squid2 = self.gen_squid_top((x6-part4l,y6+self.gapwidth+self.centerwidth/2.),(100,40))
            self.bias_cell.add(squid1)
            self.bias_cell.add(squid2)
            print("Termination: SQUID "+str(self.squid[2])+" "+str(self.squid[0])+'x'+str(self.squid[1])+" to ground")
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
        shunttop = self.gen_shunt_top((x0+self.gapwidth/2+self.shunt[0]/2-self.shunt[4]/2,y0-self.shunt[5]/2),shunttype=self.shunttype)
        shuntins = self.gen_shunt_ins((x0+self.gapwidth/2-(self.shunt[2]-self.shunt[0])/2,y0-self.shunt[3]/2))

        [shuntcell.add(toadd) for toadd in [shuntbase, shuntins, shunttop]]
        return shuntcell


    def gen_shunt_base(self,pos):
        """
        Base layer for shunt
        """
        x0 = pos[0]
        y0 = pos[1]

        shuntbase = cad.core.Cell('shuntbase')
        '''
        shuntpoints = [(x0, y0+self.gapwidth),
                     (x0, y0-self.shunt[1]/2.),
                     (x0+self.shunt[0]+2*self.gapwidth, y0-self.shunt[1]/2.),
                     (x0+self.shunt[0]+2*self.gapwidth, y0+self.gapwidth),
                     (x0+self.shunt[0]+self.gapwidth, y0+self.gapwidth),
                     (x0+self.shunt[0]+self.gapwidth, y0+self.gapwidth-self.shunt[1]/2.),
                     (x0+self.gapwidth, y0+self.gapwidth-self.shunt[1]/2.),
                     (x0+self.gapwidth, y0+self.gapwidth)]
        shunt1 = cad.core.Boundary(shuntpoints, layer=self.layer_bottom)
        '''
        shuntpoints = [(x0,y0+self.centerwidth/2.),(x0,y0+self.shunt[1]/2.+self.gapwidth/2.),
                    (x0+self.shunt[0]+self.gapwidth,y0+self.shunt[1]/2.+self.gapwidth/2.),(x0+self.shunt[0]+self.gapwidth,y0+self.centerwidth/2.)]
        shunt1 = cad.core.Path(shuntpoints,self.gapwidth)
        shunt11 = cad.utils.reflect(shunt1,'x',origin=(0,y0))#+self.gapwidth+self.centerwidth/2.))
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
        shuntpoints = [(x0,y0),
                    (x0+self.shunt[2],y0+self.shunt[3])]
        shunt = cad.shapes.Rectangle(shuntpoints[0], shuntpoints[1], layer=self.layer_ins)
        shuntins.add(shunt)
        return shuntins


    def gen_shunt_top(self,pos,shunttype):
        """
        Returns top plate for shunt capacitors
        """
        x0 = pos[0]
        y0 = pos[1]

        shunttop = cad.core.Cell('shunttop')
        if shunttype==0:
            shuntpoints = [(x0,y0),
                        (x0+self.shunt[4],y0+self.shunt[5])]
            shunt = cad.shapes.Rectangle(shuntpoints[0], shuntpoints[1], layer=self.layer_top)
            
            shunttop.add(shunt)

        elif shunttype==1:
            dy = self.centerwidth+self.gapwidth*1.4
            dx = 30
            shuntpoints = [(x0-dx,y0),(x0-dx,y0+self.shunt[5]/2-dy),(x0,y0+self.shunt[5]/2-dy),(x0,y0+self.shunt[5]/2),
                            (x0+self.shunt[4]/2,y0+self.shunt[5]/2),(x0+self.shunt[4]/2,y0)]
            shunt1 = cad.core.Boundary(shuntpoints, layer=self.layer_top)
            shunt2 = cad.utils.reflect(shunt1,'y',origin=(x0+self.shunt[4]/2,y0+self.shunt[5]/2))
            shunt3 = cad.utils.reflect(shunt1,'x',origin=(x0+self.shunt[4]/2,y0+self.shunt[5]/2))
            shunt4 = cad.utils.rotate(shunt1,180,center=(x0+self.shunt[4]/2,y0+self.shunt[5]/2))
            for toadd in [shunt1,shunt2,shunt3,shunt4]:
                shunttop.add(toadd)
        else:
            raise KeyError('shunttype has to be 0 or 1')
        
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


    def gen_holey_ground_mask(self):
        self.maskcell = cad.core.Cell('MASK')

        self.maskcell.add(CPW(self.feedlist,pin=0.,gap=self.centerwidth/2.+self.gapwidth+self.maskmargin,turn_radius=self.turnradius,layer=91))
        self.maskcell.add(CPW(self.cpwlist,pin=0.,gap=self.centerwidth/2.+self.gapwidth+self.maskmargin,turn_radius=self.turnradius,layer=91))
        bbx, bby = self.shunt1.bounding_box
        self.maskcell.add(cad.shapes.Rectangle((bbx[0]-self.maskmargin,bbx[1]-self.maskmargin),(bby[0]+self.maskmargin,bby[1]+self.maskmargin),layer=91))

        boxmask = cad.shapes.Rectangle((self.endboxpoints[0][0]-2*self.maskmargin,self.endboxpoints[0][1]-self.maskmargin),
            (self.endboxpoints[1][0]+2*self.maskmargin,self.endboxpoints[1][1]+self.maskmargin),layer=91)

        self.maskcell.add(boxmask)

        return self.maskcell

    def gen_label(self,pos):
        """
        Generate label with termination type
        if squid: squid wJJ x wlead \n wSQUID x lSQUID \n cavlength
        """
        labelcell = cad.core.Cell('DEV_LABEL')
        if self.termination=='squid':
            lblstrng = self.termination+' '+str(self.squid[2])+'x'+str(self.squid[3])+\
                                            '\n'+str(self.squid[0])+'x'+str(self.squid[1])+\
                                            '\n'+str(self.cpwlength)
        else:
            lblstrng = '{}\nl={:.0f} um\nAs={:.0f} um2'.format(self.termination,self.cpwlength,self.shunt[0]*self.shunt[1])
        label = cad.shapes.LineLabel(lblstrng,100,
                                     (pos[0],pos[1]),line_width=5,layer=self.layer_bottom)
        labelcell.add(label)
        return labelcell