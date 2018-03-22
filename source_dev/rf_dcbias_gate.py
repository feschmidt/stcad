import numpy as np
import gdsCAD as cad
from CPW import *
from testing_fillet import fillet

class RFShuntGate():
    '''
    Class for RF DC bias cavities with gate
    Initial values:
        - shuntgate = False
    '''
    def __init__(self, name, dict_dcbias, shuntgate=False, holemarker=True, shunttype=0):

        self.name = name
        self.dict_dcbias = dict_dcbias

        self.xmax = dict_dcbias['xmax'] # this is the maximum length without any wiggles
        if 'ymax' in dict_dcbias.keys():
            self.ymax = dict_dcbias['ymax']
        else:
            self.ymax=1500.
        if 'nbends' in dict_dcbias.keys():
            self.nbends = dict_dcbias['nbends']
        else:
            self.nbends = 1
        self.length = dict_dcbias['length']
        self.pos = dict_dcbias['position']    # (x0,y0)
        self.feedlength = dict_dcbias['feedlength']
        self.shunt = dict_dcbias['shunt']     # (basex,basey,insoverlap,topx,topy)
        self.hole = dict_dcbias['holedim']       # (xdim, ydim)
        self.holemarker = holemarker
        self.shuntgate = shuntgate
        self.shunttype = shunttype
        
        self.centerwidth = self.dict_dcbias['centerwidth']
        self.gapwidth = self.dict_dcbias['gapwidth']

        self.layer_bottom = 1
        self.layer_top = 2
        self.layer_ins = 3
        
        self.cpwlist = []

        # hard coded values
        self.radius = 1000

        self.cell = cad.core.Cell('RF CELL')

    
    def gen_full(self):
        """
        Generate two DC bias cavities with gatelines on the other side. Option to have gate shunts at the end
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        feedlength = self.feedlength
        length = self.length

        # Generate first cavity
        rfcell = cad.core.Cell('RESONATOR')
        resonator = self.gen_cavity_new(x0,y0,feedlength,self.hole,self.shuntgate)
        rfcell.add(resonator)

        self.cell.add(rfcell)

        # Add the other one as copy of the first one
        self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))

        return self.cell
        
    
    def gen_partial(self, loc):
        """
        Generate one DC bias cavity with specified loc(ation)
        values for loc: bottom, top
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        feedlength = self.feedlength
        length = self.length

        # Generate first cavity
        rfcell = cad.core.Cell('RESONATOR')
        resonator = self.gen_cavity_new(x0,y0,feedlength,self.hole,self.shuntgate)
        rfcell.add(resonator)

        if loc == 'bottom':
            self.cell.add(rfcell)
        elif loc == 'top':
            self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))
        else:
            raise ValueError("loc(ation) is invalid. Allowed values are bottom, top.")

        return self.cell
    

    def gen_cavity_new(self, x0, y0, feedlength, hole, shuntgate):
        """
        Generate baselayer with shunted gate (optional)
        """

        self.bias_cell = cad.core.Cell('RF_DC_BIAS')
        
        # Create feed to shunt
        part1 = CPW([[x0,y0],[x0+feedlength,y0]], layer=self.layer_bottom, pin=self.centerwidth,gap=self.gapwidth)        
        
        # Create shunt
        x1 = x0+feedlength+self.gapwidth/2
        y1 = y0#-self.centerwidth/2-self.gapwidth
        shunt = self.gen_shunt_full((x1,y1))

        # Connect shunt to end
        x2 = x1+self.shunt[0]+self.gapwidth/2
        y2 = y0

        xspace = self.xmax
        part2 = self.fit_CPW(x2,y2,self.length,xspace=xspace,yspace=self.ymax,gap=self.gapwidth,pin=self.centerwidth,nbends=self.nbends)

        # Create hole at the end
        holex0 = self.cpwlist[-1][0]
        holey0 = y2
        holemarker = self.holemarker
        if self.gapwidth!=0:
            # Add hole for gJJ
            gJJ_box = cad.core.Cell('JJ BOX')
            gJJ_box.add(cad.shapes.Rectangle((holex0, holey0-hole[1]/2),(holex0+hole[0],holey0+hole[1]/2)))
            # Add marker for gJJ
            if holemarker == True:
                box1=cad.shapes.Rectangle((holex0+5,holey0+40),(holex0+10,holey0+45))
                box2=cad.shapes.Rectangle((holex0+10,holey0+35),(holex0+15,holey0+40))
                gJJ_box.add(box1)
                gJJ_box.add(box2)
                gJJ_box.add(cad.utils.reflect(box1,'x',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.reflect(box2,'x',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.reflect(box1,'y',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.reflect(box2,'y',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.rotate(box1,180,center=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.rotate(box2,180,center=(holex0+hole[0]/2,holey0)))
        endhole = holex0+hole[0]


        for toadd in [part1,shunt,part2,gJJ_box]:
            self.bias_cell.add(toadd)

        return self.bias_cell


    def resl1(self,x,n,r):
        # horizontal length
        return (x-4*n*r)/2.0


    def resl2(self,l,x,n,r):
        # vertical length
        return (l-2*self.resl1(x,n,r)-n*2*np.pi*r)/2./n


    def fit_CPW(self,x0,y0,length,xspace=6000,yspace=1500,pin=12.5,gap=5,turnradius=150,nbends=1,layer=1): # TODO
        """
        Calculates the required number of arcs to fit the CPW into the available space
        """

        CPWcell = cad.core.Cell('CPW')

        if length <= xspace:
            # first case: resonator fits into xspace
            if length < xspace:
                raise Warning('Distance between launchers smaller than resonator length. Maybe change launcher positions and try again.')
            cpw = CPW([[x0,y0],[x0+length,y0]],pin=pin,gap=gap,layer=layer)
            nbends = 0
        else:
            l1 = self.resl1(xspace,nbends,turnradius)
            l2 = self.resl2(length,xspace,nbends,turnradius)
            yy = 2*turnradius+l2
            while yy>yspace:
                nbends+=1
                l1 = self.resl1(xspace,nbends,turnradius)
                l2 = self.resl2(length,xspace,nbends,turnradius)
                yy = 2*turnradius+l2
                if l2<0:
                    raise ValueError('Minimum radius too small. Change launcher positions and try again.')
                if l1<0:
                    raise ValueError('Resonator does not fit into allocated space. Try increasing xspace or yspace.')
            cpwlist = [[x0,y0],[x0+l1+turnradius,y0]]
            for m in range(nbends):
                #cpwlist.append([cpwlist[-1][0]+turnradius,y0]) # workaround to prevent CPW() from making bends in straight segments
                cpwlist.append([cpwlist[-1][0],y0-l2-2*turnradius])
                cpwlist.append([cpwlist[-1][0]+2*turnradius,y0-l2-2*turnradius])
                cpwlist.append([cpwlist[-1][0],y0])
                if m<nbends-1:
                    cpwlist.append([cpwlist[-1][0]+2*turnradius,y0])
            cpwlist.append([cpwlist[-1][0]+l1+turnradius,y0])

            self.cpwlist = cpwlist
            cpw = CPW(self.cpwlist,pin=pin,gap=gap,turn_radius=turnradius,layer=layer)

        print 'Input length:', length
        print 'Available xspace:', xspace
        print 'Resonator length:', cpw.length
        print 'Number of bends:', nbends
        CPWcell.add(cpw)

        return CPWcell


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
        shuntpoints = [(x0,y0+self.centerwidth/2),(x0,y0+self.shunt[1]/2),
                    (x0+self.shunt[0],y0+self.shunt[1]/2),(x0+self.shunt[0],y0+self.centerwidth/2)]
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

    
    def gen_label(self,pos):
        """
        Generate label with resonator length
        """
        labelcell = cad.core.Cell('DEV_LABEL')
        if self.termination=='squid':
            label = cad.shapes.LineLabel(self.length, 100, (pos[0],pos[1]), line_width=5, layer=self.layer_bottom)
        labelcell.add(label)
        return labelcell