import numpy as np
import gdsCAD as cad
from .objects import CPW
from .objects import Shunt_Cap

class RFShuntGate():
    '''
    Class for RF DC bias cavities with gate
    Initial values:
        - shuntgate = False
    dict_cavity = {'length': 6900,
            'feedlength': 200,
            'centerwidth': feedwidth,
            'gapwidth': gapwidth,
            'shunt': (237.6,647.6,270,680,237.6,720),
            'holedim': (80,70),
            'position': (-launchdist/2.,3500),
            'nbends': 2,
            'xmax': 3000}
    '''
    def __init__(self, name, dict_dcbias, holemarker=True, shunttype=0, label=True):

        self.name = name
        self.cell = cad.core.Cell('RF CELL') 

        self.layer_bottom = 1
        self.layer_ins = 2
        self.layer_top = 3
        
        self.ymax = 1500
        self.nbends = 1
        self.turnradius = 150
        self.maskmargin = 5
        self.shuntmasksize = (260,740)
        self.shuntgate = False
        self.gatestub = 50 # length of gate stub

        for key,val in list(dict_dcbias.items()):
            setattr(self,key,val)
        
        self.holemarker = holemarker
        self.shunttype = shunttype

        self.cpwlist = []
        self.label = label

    
    def gen_full(self,mask=True):
        """
        Generate two DC bias cavities with gatelines on the other side. Option to have gate shunts at the end
        """

        x0 = self.position[0]
        y0 = self.position[1]
        feedlength = self.feedlength
        length = self.length

        # Generate first cavity
        rfcell = cad.core.Cell('RESONATOR')
        resonator = self.gen_cavity_new(x0,y0,feedlength,self.holedim,self.shuntgate)
        if mask:
            rfmask = self.gen_holey_ground_mask()
            rfcell.add(rfmask)
        rfcell.add(resonator)

        self.cell.add(rfcell)

        # Add the other one as copy of the first one
        self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))

        return self.cell
        
    
    def gen_partial(self, loc, gJJ=True, mask=True):
        """
        Generate one DC bias cavity with specified loc(ation)
        values for loc: bottom, top
        """

        x0 = self.position[0]
        y0 = self.position[1]
        feedlength = self.feedlength
        length = self.length

        # Generate first cavity
        rfcell = cad.core.Cell('RESONATOR')
        resonator = self.gen_cavity_new(x0,y0,feedlength,self.holedim,self.shuntgate,gJJ=gJJ)
        rfcell.add(resonator)
        if mask:
            rfmask = self.gen_holey_ground_mask()
            rfcell.add(rfmask)

        if loc == 'top':
            self.cell.add(rfcell)
        elif loc == 'bottom':
            self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))
        else:
            raise ValueError("loc(ation) is invalid. Allowed values are bottom, top.")

        return self.cell
    

    def gen_cavity_new(self, x0, y0, feedlength, hole, shuntgate, gJJ):
        """
        Generate baselayer with shunted gate (optional)
        """

        self.bias_cell = cad.core.Cell('RF_DC_BIAS')
        
        # Create feed to shunt
        self.feedlist = [[x0,y0],[x0+feedlength,y0]]
        part1 = CPW(self.feedlist, layer=self.layer_bottom, pin=self.centerwidth,gap=self.gapwidth)        
        
        # Create shunt
        x1 = x0+feedlength
        y1 = y0#-self.centerwidth/2-self.gapwidth
        self.shunt1 = Shunt_Cap(pos=(x1,y1),shunt=self.shunt)

        # Connect shunt to end
        x2 = x1+self.shunt[0]+self.gapwidth
        y2 = y0

        if not shuntgate:
            xspace = self.launchdist - self.feedlength - self.shunt[0] - self.holedim[0]
        else:
            xspace = self.launchdist - self.feedlength - self.shunt[0] - self.holedim[0] - self.gatestub - self.shunt[0] - 2*self.gatestub#self.feedlength
        part2 = self.fit_CPW(x2,y2,self.length,xspace=xspace,yspace=self.ymax,gap=self.gapwidth,pin=self.centerwidth,nbends=self.nbends,turnradius=self.turnradius)

        # Create hole at the end
        holex0 = self.cpwlist[-1][0]
        holey0 = y2
        holemarker = self.holemarker
        if self.gapwidth!=0:
            # Add hole for gJJ
            gJJ_box = cad.core.Cell('JJ BOX')
            self.jjboxpts = [(holex0, holey0-hole[1]/2),(holex0+hole[0],holey0+hole[1]/2)]
            gJJ_box.add(cad.shapes.Rectangle(self.jjboxpts[0],self.jjboxpts[1]))
            # Add marker for gJJ
            if holemarker == True:
                box1=cad.shapes.Rectangle((holex0+5,holey0+hole[1]/2+5),(holex0+10,holey0+hole[1]/2+10))
                box2=cad.shapes.Rectangle((holex0+10,holey0+hole[1]/2),(holex0+15,holey0+hole[1]/2+5))
                gJJ_box.add(box1)
                gJJ_box.add(box2)
                gJJ_box.add(cad.utils.reflect(box1,'x',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.reflect(box2,'x',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.reflect(box1,'y',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.reflect(box2,'y',origin=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.rotate(box1,180,center=(holex0+hole[0]/2,holey0)))
                gJJ_box.add(cad.utils.rotate(box2,180,center=(holex0+hole[0]/2,holey0)))
        endhole = holex0+hole[0]

        if shuntgate:
            # Connect hole to shunt
            self.gatecpwpts = [[endhole,y0],[endhole+self.gatestub,y0]]
            gatecpw = CPW(self.gatecpwpts,gap=self.gapwidth,pin=self.centerwidth,layer=1)
            
            # Create second shunt
            x1 = self.gatecpwpts[-1][0]
            y1 = y0
            self.shunt2 = Shunt_Cap(pos=(x1,y1),shunt=self.shunt)

            # Connect second shunt to end
            x2 = x1+self.shunt[0]+self.gapwidth
            y2 = y0
            self.endcpwpts = [[x2,y2],[-self.position[0],y2]]#[x2+self.feedlength,y2]]
            endcpw = CPW(self.endcpwpts,gap=self.gapwidth,pin=self.centerwidth,layer=1)


        for toadd in [part1,self.shunt1,part2]:
            self.bias_cell.add(toadd)
        if gJJ:
            self.bias_cell.add(gJJ_box)
        if shuntgate:
            self.bias_cell.add(self.shunt2)
            self.bias_cell.add(gatecpw)
            self.bias_cell.add(endcpw)


        return self.bias_cell


    def resl1(self,x,n,r):
        # horizontal length
        l1 = (x-4*n*r)/2.0
        if l1<0:
            raise ValueError('Resonator does not fit into allocated space. Try increasing xspace or yspace.')
        return l1


    def resl2(self,l,x,n,r):
        # vertical length
        l2 = (l-2*self.resl1(x,n,r)-n*2*np.pi*r)/2./n
        if l2<0:
            raise ValueError('Minimum radius too small or number of bends too high.')
        return l2


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

        print('Input length:', length)
        print('Available xspace:', xspace)
        print('Resonator length:', cpw.length)
        print('Number of bends:', nbends)

        CPWcell.add(cpw)

        return CPWcell


    def gen_holey_ground_mask(self):
        self.maskcell = cad.core.Cell('MASK')

        skirt = self.centerwidth+2*self.gapwidth+2*self.maskmargin
        self.maskcell.add(CPW(self.feedlist,pin=skirt,gap=0,turn_radius=self.turnradius,layer=91,writegaps=False))
        self.maskcell.add(CPW(self.cpwlist,pin=skirt,gap=0,turn_radius=self.turnradius,layer=91,writegaps=False))
        jjboxmask = cad.shapes.Rectangle((self.jjboxpts[0][0]-2*self.maskmargin,self.jjboxpts[0][1]-5*self.maskmargin),
            (self.jjboxpts[1][0]+2*self.maskmargin,self.jjboxpts[1][1]+5*self.maskmargin),layer=91)
        self.maskcell.add(jjboxmask)

        if self.shuntgate:
            self.maskcell.add(CPW(self.endcpwpts,pin=skirt,gap=0,turn_radius=self.turnradius,layer=91,writegaps=False))
            self.maskcell.add(CPW(self.gatecpwpts,pin=skirt,gap=0,turn_radius=self.turnradius,layer=91,writegaps=False))

        return self.maskcell

    
    def gen_label(self,pos):
        """
        Generate label with termination type
        if squid: squid wJJ x wlead \n wSQUID x lSQUID \n cavlength
        """
        labelcell = cad.core.Cell('DEV_LABEL')
        # if self.termination=='squid':
        #     lblstrng = self.termination+' '+str(self.squid[2])+'x'+str(self.squid[3])+\
        #                                     '\n'+str(self.squid[0])+'x'+str(self.squid[1])+\
        #                                     '\n'+str(self.cpwlength)
        # else:
        lblstrng = '{}\nl={:.0f} um\nAs={:.0f} um2'.format('gJJ',self.length,self.shunt[0]*self.shunt[1])
        label = cad.shapes.LineLabel(lblstrng,100,
                                     (pos[0],pos[1]),line_width=5,layer=self.layer_bottom)
        labelcell.add(label)

        return labelcell