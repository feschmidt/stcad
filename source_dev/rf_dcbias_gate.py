#*** BROKEN

import numpy as np
import gdsCAD as cad
from CPW import *

class RFShuntGate():
    '''
    *** BROKEN
    *** Needs to be updated to the standard format of rf_dcbias.py
    Class for RF DC bias cavities with gate
    Initial values:
        - shuntgate = False
    '''
    def __init__(self, name, dict_dcbias, shuntgate=False, holemarker=True, shunttype=0):

        self.name = name
        self.dict_dcbias = dict_dcbias

        self.xmax = dict_dcbias['xmax'] # this is the maximum length without any wiggles
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
        resonator = self.gen_cavity(x0,y0,feedlength,self.hole,self.shuntgate)
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
        resonator = self.gen_cavity(x0,y0,feedlength,self.hole,self.shuntgate)
        rfcell.add(resonator)

        if loc == 'bottom':
            self.cell.add(rfcell)
        elif loc == 'top':
            self.cell.add(cad.core.CellReference(rfcell,origin=(0,0),x_reflection=True))
        else:
            raise ValueError("loc(ation) is invalid. Allowed values are bottom, top.")

        return self.cell
        
    def gen_cavity(self, x0, y0, feedlength, hole, shuntgate):
        """
        Generate baselayer with shunted gate (optional)
        """

        self.bias_cell = cad.core.Cell('RF_DC_BIAS')
        
        # Create feed to shunt
        part1 = CPW([[x0,y0],[x0+feedlength,y0]], layer=self.layer_bottom, pin=self.centerwidth,gap=self.gapwidth)        
        
        # Create shunt
        x1 = x0+feedlength
        y1 = y0-self.centerwidth/2-self.gapwidth
        shunt = self.gen_shunt_full((x1,y1))

        # Connect shunt to end
        x2 = x1+self.shunt[0]+2*self.gapwidth
        y2 = y0

        ############ TODO
        """
                                                                                                                                                                                                                                                                                                                                    dddddddd                                                                                                                                                                                                                                                                    
               AAA                                          tttt                                                                              tttt            iiii                                        lllllll              CCCCCCCCCCCCCPPPPPPPPPPPPPPPPP   WWWWWWWW                           WWWWWWWW                 d::::::d                                       iiii                                                                                        iiii           tttt          hhhhhhh                                                                                             
              A:::A                                      ttt:::t                                                                           ttt:::t           i::::i                                       l:::::l           CCC::::::::::::CP::::::::::::::::P  W::::::W                           W::::::W                 d::::::d                                      i::::i                                                                                      i::::i       ttt:::t          h:::::h                                                                                             
             A:::::A                                     t:::::t                                                                           t:::::t            iiii                                        l:::::l         CC:::::::::::::::CP::::::PPPPPP:::::P W::::::W                           W::::::W                 d::::::d                                       iiii                                                                                        iiii        t:::::t          h:::::h                                                                                             
            A:::::::A                                    t:::::t                                                                           t:::::t                                                        l:::::l        C:::::CCCCCCCC::::CPP:::::P     P:::::PW::::::W                           W::::::W                 d:::::d                                                                                                                                                t:::::t          h:::::h                                                                                             
           A:::::::::A           uuuuuu    uuuuuu  ttttttt:::::ttttttt       ooooooooooo      mmmmmmm    mmmmmmm     aaaaaaaaaaaaa   ttttttt:::::ttttttt    iiiiiii     cccccccccccccccc  aaaaaaaaaaaaa    l::::l       C:::::C       CCCCCC  P::::P     P:::::P W:::::W           WWWWW           W:::::W          ddddddddd:::::d     eeeeeeeeeeee        ssssssssss   iiiiiii    ggggggggg   gggggnnnn  nnnnnnnn         wwwwwww           wwwww           wwwwwwwiiiiiii ttttttt:::::ttttttt     h::::h hhhhh              aaaaaaaaaaaaa   rrrrr   rrrrrrrrr       cccccccccccccccc    ssssssssss   
          A:::::A:::::A          u::::u    u::::u  t:::::::::::::::::t     oo:::::::::::oo  mm:::::::m  m:::::::mm   a::::::::::::a  t:::::::::::::::::t    i:::::i   cc:::::::::::::::c  a::::::::::::a   l::::l      C:::::C                P::::P     P:::::P  W:::::W         W:::::W         W:::::W         dd::::::::::::::d   ee::::::::::::ee    ss::::::::::s  i:::::i   g:::::::::ggg::::gn:::nn::::::::nn        w:::::w         w:::::w         w:::::w i:::::i t:::::::::::::::::t     h::::hh:::::hhh           a::::::::::::a  r::::rrr:::::::::r    cc:::::::::::::::c  ss::::::::::s  
         A:::::A A:::::A         u::::u    u::::u  t:::::::::::::::::t    o:::::::::::::::om::::::::::mm::::::::::m  aaaaaaaaa:::::a t:::::::::::::::::t     i::::i  c:::::::::::::::::c  aaaaaaaaa:::::a  l::::l      C:::::C                P::::PPPPPP:::::P    W:::::W       W:::::::W       W:::::W         d::::::::::::::::d  e::::::eeeee:::::eess:::::::::::::s  i::::i  g:::::::::::::::::gn::::::::::::::nn        w:::::w       w:::::::w       w:::::w   i::::i t:::::::::::::::::t     h::::::::::::::hh         aaaaaaaaa:::::a r:::::::::::::::::r  c:::::::::::::::::css:::::::::::::s 
        A:::::A   A:::::A        u::::u    u::::u  tttttt:::::::tttttt    o:::::ooooo:::::om::::::::::::::::::::::m           a::::a tttttt:::::::tttttt     i::::i c:::::::cccccc:::::c           a::::a  l::::l      C:::::C                P:::::::::::::PP      W:::::W     W:::::::::W     W:::::W         d:::::::ddddd:::::d e::::::e     e:::::es::::::ssss:::::s i::::i g::::::ggggg::::::ggnn:::::::::::::::n        w:::::w     w:::::::::w     w:::::w    i::::i tttttt:::::::tttttt     h:::::::hhh::::::h                 a::::a rr::::::rrrrr::::::rc:::::::cccccc:::::cs::::::ssss:::::s
       A:::::A     A:::::A       u::::u    u::::u        t:::::t          o::::o     o::::om:::::mmm::::::mmm:::::m    aaaaaaa:::::a       t:::::t           i::::i c::::::c     ccccccc    aaaaaaa:::::a  l::::l      C:::::C                P::::PPPPPPPPP         W:::::W   W:::::W:::::W   W:::::W          d::::::d    d:::::d e:::::::eeeee::::::e s:::::s  ssssss  i::::i g:::::g     g:::::g   n:::::nnnn:::::n         w:::::w   w:::::w:::::w   w:::::w     i::::i       t:::::t           h::::::h   h::::::h         aaaaaaa:::::a  r:::::r     r:::::rc::::::c     ccccccc s:::::s  ssssss 
      A:::::AAAAAAAAA:::::A      u::::u    u::::u        t:::::t          o::::o     o::::om::::m   m::::m   m::::m  aa::::::::::::a       t:::::t           i::::i c:::::c               aa::::::::::::a  l::::l      C:::::C                P::::P                  W:::::W W:::::W W:::::W W:::::W           d:::::d     d:::::d e:::::::::::::::::e    s::::::s       i::::i g:::::g     g:::::g   n::::n    n::::n          w:::::w w:::::w w:::::w w:::::w      i::::i       t:::::t           h:::::h     h:::::h       aa::::::::::::a  r:::::r     rrrrrrrc:::::c                s::::::s      
     A:::::::::::::::::::::A     u::::u    u::::u        t:::::t          o::::o     o::::om::::m   m::::m   m::::m a::::aaaa::::::a       t:::::t           i::::i c:::::c              a::::aaaa::::::a  l::::l      C:::::C                P::::P                   W:::::W:::::W   W:::::W:::::W            d:::::d     d:::::d e::::::eeeeeeeeeee        s::::::s    i::::i g:::::g     g:::::g   n::::n    n::::n           w:::::w:::::w   w:::::w:::::w       i::::i       t:::::t           h:::::h     h:::::h      a::::aaaa::::::a  r:::::r            c:::::c                   s::::::s   
    A:::::AAAAAAAAAAAAA:::::A    u:::::uuuu:::::u        t:::::t    tttttto::::o     o::::om::::m   m::::m   m::::ma::::a    a:::::a       t:::::t    tttttt i::::i c::::::c     ccccccca::::a    a:::::a  l::::l       C:::::C       CCCCCC  P::::P                    W:::::::::W     W:::::::::W             d:::::d     d:::::d e:::::::e           ssssss   s:::::s  i::::i g::::::g    g:::::g   n::::n    n::::n            w:::::::::w     w:::::::::w        i::::i       t:::::t    tttttt h:::::h     h:::::h     a::::a    a:::::a  r:::::r            c::::::c     cccccccssssss   s:::::s 
   A:::::A             A:::::A   u:::::::::::::::uu      t::::::tttt:::::to:::::ooooo:::::om::::m   m::::m   m::::ma::::a    a:::::a       t::::::tttt:::::ti::::::ic:::::::cccccc:::::ca::::a    a:::::a l::::::l       C:::::CCCCCCCC::::CPP::::::PP                   W:::::::W       W:::::::W              d::::::ddddd::::::dde::::::::e          s:::::ssss::::::si::::::ig:::::::ggggg:::::g   n::::n    n::::n             w:::::::w       w:::::::w        i::::::i      t::::::tttt:::::t h:::::h     h:::::h     a::::a    a:::::a  r:::::r            c:::::::cccccc:::::cs:::::ssss::::::s
  A:::::A               A:::::A   u:::::::::::::::u      tt::::::::::::::to:::::::::::::::om::::m   m::::m   m::::ma:::::aaaa::::::a       tt::::::::::::::ti::::::i c:::::::::::::::::ca:::::aaaa::::::a l::::::l        CC:::::::::::::::CP::::::::P                    W:::::W         W:::::W                d:::::::::::::::::d e::::::::eeeeeeee  s::::::::::::::s i::::::i g::::::::::::::::g   n::::n    n::::n              w:::::w         w:::::w         i::::::i      tt::::::::::::::t h:::::h     h:::::h     a:::::aaaa::::::a  r:::::r             c:::::::::::::::::cs::::::::::::::s 
 A:::::A                 A:::::A   uu::::::::uu:::u        tt:::::::::::tt oo:::::::::::oo m::::m   m::::m   m::::m a::::::::::aa:::a        tt:::::::::::tti::::::i  cc:::::::::::::::c a::::::::::aa:::al::::::l          CCC::::::::::::CP::::::::P                     W:::W           W:::W                  d:::::::::ddd::::d  ee:::::::::::::e   s:::::::::::ss  i::::::i  gg::::::::::::::g   n::::n    n::::n               w:::w           w:::w          i::::::i        tt:::::::::::tt h:::::h     h:::::h      a::::::::::aa:::a r:::::r              cc:::::::::::::::c s:::::::::::ss  
AAAAAAA                   AAAAAAA    uuuuuuuu  uuuu          ttttttttttt     ooooooooooo   mmmmmm   mmmmmm   mmmmmm  aaaaaaaaaa  aaaa          ttttttttttt  iiiiiiii    cccccccccccccccc  aaaaaaaaaa  aaaallllllll             CCCCCCCCCCCCCPPPPPPPPPP                      WWW             WWW                    ddddddddd   ddddd    eeeeeeeeeeeeee    sssssssssss    iiiiiiii    gggggggg::::::g   nnnnnn    nnnnnn                www             www           iiiiiiii          ttttttttttt   hhhhhhh     hhhhhhh       aaaaaaaaaa  aaaa rrrrrrr                cccccccccccccccc  sssssssssss    

        """
        mlength = 800
        mwidth = 300
        endlength = 1400
        endx = x2+3*self.feedlength+3*mwidth+endlength

        part2 = CPW([[x2,y2],[x2+3*self.feedlength,y2],[x2+3*self.feedlength,y2-mlength],[x2+3*self.feedlength+mwidth,y2-mlength],
            [x2+3*self.feedlength+mwidth,y2],[x2+3*self.feedlength+2*mwidth,y2],[x2+3*self.feedlength+2*mwidth,y2-mlength],
            [x2+3*self.feedlength+3*mwidth,y2-mlength],[x2+3*self.feedlength+3*mwidth,y2],[endx,y2]],
            layer=self.layer_bottom,pin=self.centerwidth,gap=self.gapwidth,turn_radius = mwidth/2.)
        
        # Create hole at the end
        holex0 = endx
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
    
    def route_CPW(self,coords,pin,gap,turnradius=150,layer=self.layer_bottom): # TODO
        """
        Routes a CPW from (coords[0],coords[1]) to (coords[2],coords[3])
        """

        CPWcell = cad.core.Cell('CPW')

        return CPWcell

    def fit_CPW(self,x0,y0,length,xspace=6000,yspace=800,pin=12.5,gap=5,turnradius=150,layer=self.layer_bottom,orientation='hor',minrad=50): # TODO
        """
        Calculates the required number of arcs to fit the CPW into the available space

        """

        CPWcell = cad.core.Cell('CPW')

        if length < xspace:
            cpw = CPW([[x0,y0],[x0+length,y0]],pin=pin,gap=gap,layer=layer)
        else:


        mlength = 800
        mwidth = 300
        endlength = 1400
        endx = x2+3*self.feedlength+3*mwidth+endlength

        part2 = CPW([[x2,y2],[x2+3*self.feedlength,y2],[x2+3*self.feedlength,y2-mlength],[x2+3*self.feedlength+mwidth,y2-mlength],
            [x2+3*self.feedlength+mwidth,y2],[x2+3*self.feedlength+2*mwidth,y2],[x2+3*self.feedlength+2*mwidth,y2-mlength],
            [x2+3*self.feedlength+3*mwidth,y2-mlength],[x2+3*self.feedlength+3*mwidth,y2],[endx,y2]],
            layer=self.layer_bottom,pin=self.centerwidth,gap=self.gapwidth,turn_radius = mwidth/2.)

        return CPWcell


    def gen_shunt_full(self,pos):
        """
        Creates a shunt capacitor from center conductor to ground
        """
        x0 = pos[0]
        y0 = pos[1]

        shuntcell = cad.core.Cell('SHUNT')
        shuntbase = self.gen_shunt_base((x0,y0))
        shunttop = self.gen_shunt_top((x0+self.gapwidth+self.shunt[0]/2-self.shunt[4]/2,y0+self.gapwidth+self.centerwidth/2-self.shunt[5]/2),shunttype=self.shunttype)
        shuntins = self.gen_shunt_ins((x0+self.gapwidth-(self.shunt[2]-self.shunt[0])/2,y0+self.gapwidth+self.centerwidth/2-self.shunt[3]/2))
        print 'x0',x0,'y0',y0
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
                    















# TODO: Below here is outdated and has to be removed                    
################################    
    def gen_cavities(self,gapwidth=0):
        '''
        Create the individual cavity. Gapwidth = 0: center conductor. Finite gapwidth: Gaps around
        '''

        length = self.length
        centerwidth = self.centerwidth + 2*gapwidth

        center = self.center

        # Create first launcher
        launcherwidth = self.launcherwidth
        llstart = self.llstart          
        llend = self.llend
        if gapwidth!=0:
            x1_launcher = 0#-500
            y1_launcher = 230
        else:
            x1_launcher = 700
            y1_launcher = 0  

        launcherpoints = [(x1_launcher, center+(launcherwidth+centerwidth)/2+y1_launcher),
                        (1900, center+(launcherwidth+centerwidth)/2+y1_launcher),
                        (llstart, center+centerwidth/2),
                        (llstart, center-centerwidth/2),
                        (1900, center-(launcherwidth+centerwidth)/2-y1_launcher),
                        (x1_launcher, center-(launcherwidth+centerwidth)/2-y1_launcher)]
        launcher = cad.core.Boundary(launcherpoints)

        # Create first shunt
        shunt1 = self.gen_shunt((llstart,self.llength),0,gap=gapwidth)

        # Cavity length starts here
        startx0 = shunt1[5]
        stopx0 = startx0 + self.dict_cavity['lead1']-gapwidth
        
        shunt1_cavity_points = [(startx0,center),(stopx0,center)]
        start_cavity = cad.core.Path(shunt1_cavity_points,centerwidth)

        r0 = self.r0
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = self.top_cv
        bot_cv = self.bot_cv
        
        # Calculate cavity length
        A = (stopx0-startx0) + 2*np.pi*r0 * 2 + (top_cv-bot_cv) * 4
        endx0 = stopx0+r0*8
        endx = length - (A - endx0) - gapwidth
        # without any curves: cav_straight = endx - startx0
        
        # Do the wiggles
        curve1 = cad.shapes.Disk((stopx0,top_cv),radius,inner_radius=inner_radius,initial_angle=90,
            final_angle=0)
        curve1_lead = cad.core.Path([(stopx0+r0, top_cv),(stopx0+r0,bot_cv)],centerwidth)
        curve2 = cad.shapes.Disk((stopx0+r0*2,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve2_lead = cad.core.Path([(stopx0+r0*3,bot_cv),(stopx0+r0*3,top_cv)],centerwidth)
        curve3 = cad.shapes.Disk((stopx0+r0*4,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=0)
        curve3_lead = cad.core.Path([(stopx0+r0*5,top_cv),(stopx0+r0*5,bot_cv)],centerwidth)
        curve4 = cad.shapes.Disk((stopx0+r0*6,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve4_lead = cad.core.Path([(stopx0+r0*7,bot_cv),(stopx0+r0*7,top_cv)],centerwidth)
        curve5 = cad.shapes.Disk((endx0,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=90)
        final_lead = cad.core.Path([(endx0,center),(endx,center)],centerwidth)

        # Create hole at the end
        holex0 = endx
        holedim = self.holedim
        holemarker = self.holemarker
        if gapwidth!=0:
            # Add hole for gJJ
            gJJ_box = cad.shapes.Rectangle((holex0, center-holedim[1]/2),(holex0+holedim[0],center+holedim[1]/2))
            # Add marker for gJJ
            if holemarker == True:
                gJJ_marker = cad.core.Cell('gJJ_marker')
                box1=cad.shapes.Rectangle((holex0+5,center+40),(holex0+10,center+45))
                box2=cad.shapes.Rectangle((holex0+10,center+35),(holex0+15,center+40))
                gJJ_marker.add(box1)
                gJJ_marker.add(box2)
                gJJ_marker.add(cad.utils.reflect(box1,'x',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.reflect(box2,'x',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.reflect(box1,'y',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.reflect(box2,'y',origin=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.rotate(box1,180,center=(holex0+holedim[0]/2,center)))
                gJJ_marker.add(cad.utils.rotate(box2,180,center=(holex0+holedim[0]/2,center)))
        endhole = holex0+holedim[0]

        # Create second shunt (optional)
        if shuntgate:
            leadout = 125
            shunt2 = self.gen_shunt((endhole,70),leadout,gap=gapwidth)
            self.endshunt = shunt2[5]
        else:
            self.endshunt = endhole
        
        # Create second launcher
        launcher2 = cad.utils.reflect(launcher,'y',origin=(5e3,5e3))
        holex0 = endx
        holedim = self.holedim
        launcher2 = cad.utils.translate(launcher2,(self.endshunt-(10e3-llstart),0))   
        # For future: fix second shunt. For length adjustments make meandering longer or shorter,
        # and center it. For now this is sufficient.
        
        # Create cavity
        cavity1 = [cad.core.Elements()] * 3
        # Add all elements with layer 1
        for toadd in [launcher, shunt1[0], shunt1[1], shunt1[4],
                    start_cavity, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead,
                    launcher2]:
            toadd.layer = self.layer_bottom
            cavity1[0].add(toadd)

        # Complete shunt
        if gapwidth == 0:    
            # Add all elements with layer 2
            for toadd in [shunt1[2]]:
                toadd.layer = self.layer_diel
                cavity1[1].add(toadd)

            # Add all elements with layer 3
            for toadd in [shunt1[3]]:
                toadd.layer = self.layer_top
                cavity1[2].add(toadd)

        # Add second shunt (optional)
        if shunts==2:
            for toadd in [shunt2[0], shunt2[1], shunt2[4]]:
                toadd.layer = self.layer_bottom
                cavity1[0].add(toadd)
            if gapwidth == 0:
                for toadd in [shunt2[2]]:
                    toadd.layer = self.layer_diel
                    cavity1[0].add(toadd)
                for toadd in [shunt2[3]]:
                    toadd.layer = self.layer_top
                    cavity1[0].add(toadd)

        # Add hole and marker for graphene
        if gapwidth != 0:
            cavity1[0].add(gJJ_box)
            if holemarker == True:
                for toadd in gJJ_marker:
                    gJJ_marker.layer = self.layer_bottom
                    cavity1[0].add(toadd)
                # gJJ marker are missing from cavity2 ??
        
        
        # Create second cavity as mirrored version of first one
        cavity2 = [cad.utils.reflect(cavity1[i],'x',origin=(5e3,5e3)) for i in range(len(cavity1))]
        
        return (cavity1, cavity2)
        

    def gen_shunt(self,leadin,leadout,gap=0):
        '''
        Create shunt capacitors
        leadin: tuple (x-coordinate, lendth)
        leadout: int length
        gap: gapwidth between center conductor and ground
        '''
        # Connect in to shunt
        startx_in = leadin[0]   # x-coordinate
        stopx_in = startx_in+leadin[1]-gap
        leadpoints_in = [(startx_in, self.center),(stopx_in,self.center)]
        lead_in = cad.core.Path(leadpoints_in,self.centerwidth+2*gap)

        # Create shunt
        shuntheight = self.shuntheight + 2*gap
        shuntlength = self.shuntlength + 2*gap
        shunt_x1 = stopx_in
        shunt_y1 = self.center - shuntheight/2
        shunt_x2 = shunt_x1 + shuntlength
        shunt_y2 = shunt_y1 + shuntheight
        shunt_points = [(shunt_x1, shunt_y1),(shunt_x2, shunt_y2)]

        top_dx = self.top_dx
        top_dy = self.top_dy
        shunt_top_points = [(shunt_x1-top_dx, shunt_y1-top_dy),
                            (shunt_x2+top_dx, shunt_y2+top_dy)]

        diel_dxy = self.diel_dxy
        shunt_diel_points = [(shunt_x1-top_dx-diel_dxy, shunt_y1-top_dy-diel_dxy),
                            (shunt_x2+top_dx+diel_dxy, shunt_y2+top_dy+diel_dxy)]
        
        shunt = cad.shapes.Rectangle(shunt_points[0],shunt_points[1])
        shunt_diel = cad.shapes.Rectangle(shunt_diel_points[0],shunt_diel_points[1])
        shunt_top = cad.shapes.Rectangle(shunt_top_points[0],shunt_top_points[1])

        # Connect shunt to out
        startx_out = shunt_x2
        stopx_out = startx_out + leadout
        leadpoints_out = [(startx_out, self.center),(stopx_out,self.center)]
        lead_out = cad.core.Path(leadpoints_out,self.centerwidth+2*gap)

        return (lead_in, shunt, shunt_diel, shunt_top, lead_out, stopx_out)



