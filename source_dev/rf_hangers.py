import numpy as np
import gdsCAD as cad
import utilities as utils

class RFHangers():
    """
    Class for RF hangers
    Initial values:
        - coupling='capacitive'
        - couplinglength = 610
        - couplinggap = 10
        - centerwidth = 4
        - gapwidth = 20
        - radius = 100
        - squid = False, i.e. no squid at the end. Can be set to true
        - number=4
    """

    def __init__(self, name, dict_hangers, squid = False):

        self.name = name
        self.dict_hangers = dict_hangers
        self.length = self.dict_hangers['length']
        self.pos = self.dict_hangers['position']
        self.coupling = self.dict_hangers['coupling']   # either capacitive or inductive
        self.couplinglength = self.dict_hangers['couplinglength']
        self.couplinggap = self.dict_hangers['couplinggap']
        self.centerwidth = self.dict_hangers['centerwidth']
        self.gapwidth = self.dict_hangers['gapwidth']
        self.orientation = self.dict_hangers['orientation']

        self.layer_bottom = 1
        self.layer_top = 2

        # Option to add squid at the end
        self.squid = squid
        if squid==True:
            self.squiddrain = self.dict_hangers['squiddrain']
            self.squidx = self.dict_hangers['squidx']
            self.squidy = self.dict_hangers['squidy']
            self.squidjj = self.dict_hangers['squidjj']
            self.squidlead = self.dict_hangers['squidlead']
        elif squid=='Default':
	        self.squiddrain = 25
	        self.squidx = 40/2
	        self.squidy = 2*self.squidx
	        self.squidjj = 1
	        self.squidlead = 3

        # hard coded values
        self.radius = 100

        self.cell = cad.core.Cell('RF CELL')

    def gen_full(self,hangval=4,spacing=1800):
        """
        Generate <hangval=4> RF hangers coupled to transmission line with lengths
        [length-400*i for i in range(number)] spaced <spacing=1800> apart
	Alternatively, input an array of hanger lengths in hangval
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        length = self.length

        # Hard coded values
	if type(hangval)==int:
        	lengthvals = [length-400*i for i in range(hangval)]
	elif type(hangval)==list:
		lengthvals = hangval
	else:
		raise ValueError("hangval has to be of type int or list") 

        for xx, value in enumerate(lengthvals):
            hanger = self.gen_hanger(value,(x0+xx*spacing,y0),self.squid)
        
            if self.orientation == 'left':
                rot_cell = cad.core.CellReference(hanger,rotation = -90)
                self.cell.add(rot_cell)
            elif self.orientation == 'right':
                rot_cell = cad.core.CellReference(hanger,rotation = 90)
                self.cell.add(rot_cell)
            elif self.orientation == 'down':
                rot_cell = cad.core.CellReference(hanger,rotation = 180)
                self.cell.add(rot_cell)
            else:
                self.cell.add(hanger)

        return self.cell


    def gen_hanger(self, length, pos, squid):
        """
        Generate hanger of length=length at pos=(x0,y1)
        Initial values:
        - coupling='capacitive'
        - couplinglength = 610
        - couplinggap = 10
        - centerwidth = 4
        - gapwidth = 20
        - radius = 100
        """

        coupling = self.coupling
        couplinglength = self.couplinglength
        couplinggap = self.couplinggap
        centerwidth = self.centerwidth
        gapwidth = self.gapwidth
        radius = self.radius

        print 'Generating hanger of length ' + str(length) + ' with '+coupling+' coupling'

        self.hanger_cell = cad.core.Cell('RF_HANGER')
        
        x0 = pos[0]
        y0 = pos[1] - couplinggap
        radius_hanger = radius - gapwidth - centerwidth/2
        restlength = length - couplinglength - 2*np.pi*radius_hanger/4
        
        if coupling == 'inductive':
            hangerpoints_1 = [(x0,y0),
                            (x0 + couplinglength,y0),
                            (x0 + couplinglength,y0-gapwidth),
                            (x0, y0-gapwidth)]
            hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                            (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength),
                            (x0+couplinglength+radius-gapwidth,y0-radius-restlength),
                            (x0+couplinglength+radius-gapwidth,y0-radius)]
                            
        if coupling == 'capacitive':
            hangerpoints_1 = [(x0 - gapwidth,y0),
                            (x0 + couplinglength,y0),
                            (x0 + couplinglength,y0-gapwidth),
                            (x0 + gapwidth, y0-gapwidth),
                            (x0 + gapwidth, y0-gapwidth-centerwidth/2),
                            (x0 - gapwidth, y0-gapwidth-centerwidth/2)]
            if squid==False:
                hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                                (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                                (x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth),
                                (x0+couplinglength+radius-gapwidth,y0-radius)]
            else:
                print 'Adding SQUID'
		squiddrain=self.squiddrain
		squidx = self.squidx
		squidy = self.squidy
		squidjj = self.squidjj
		squidlead = self.squidlead
                hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                            (x0+couplinglength+radius, y0-radius-restlength),
                            (x0+couplinglength+radius+50, y0-radius-restlength),
                            (x0+couplinglength+radius+50, y0-radius-restlength-gapwidth-100),
                            (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth-100),
                            (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-2*gapwidth-2*centerwidth),
                            (x0+couplinglength+radius-gapwidth+25,y0-radius-restlength-2*gapwidth-2*centerwidth),
                            (x0+couplinglength+radius-gapwidth+25,y0-radius-restlength-2*gapwidth-centerwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius-restlength-2*gapwidth-centerwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius)]
                hangerpoints_squid_top = [(x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth-100-100),
(x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-2*gapwidth-2*centerwidth-squidy),
(x0+couplinglength+radius-gapwidth-centerwidth/2+squidx,y0-radius-restlength-2*gapwidth-2*centerwidth-squidy),
(x0+couplinglength+radius-gapwidth-centerwidth/2+squidx,y0-radius-restlength-2*gapwidth-2*centerwidth+squidjj),
(x0+couplinglength+radius-gapwidth-centerwidth/2+squidx+squidlead,y0-radius-restlength-2*gapwidth-2*centerwidth+squidjj),
(x0+couplinglength+radius-gapwidth-centerwidth/2+squidx+squidlead,y0-radius-restlength-2*gapwidth-2*centerwidth-squidy-squidlead),
(x0+couplinglength+radius-gapwidth,y0-radius-restlength-2*gapwidth-2*centerwidth-squidy-squidlead),
(x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth-100),
(x0+couplinglength+radius+50,y0-radius-restlength-gapwidth-100),
(x0+couplinglength+radius+50,y0-radius-restlength-gapwidth-100-100)]
                hanger_squid_top1 = cad.core.Boundary(hangerpoints_squid_top,layer=self.layer_top)
                hanger_squid_top2 = cad.utils.reflect(hanger_squid_top1,'y',origin=(x0+couplinglength+radius-gapwidth-centerwidth/2,0))

        hanger1 = cad.core.Boundary(hangerpoints_1)
        hanger2 = cad.core.Boundary(hangerpoints_2)
        hanger3 = cad.utils.reflect(hanger1,'x',origin=(0,y0-gapwidth-centerwidth/2))
        hanger4 = cad.utils.reflect(hanger2,'y',origin=(x0+couplinglength+radius-gapwidth-centerwidth/2,0))
        
        radius1 = radius                
        curve1 = cad.shapes.Disk((x0+couplinglength,y0-radius1), radius=radius, inner_radius=radius1-gapwidth, initial_angle=90,final_angle=0)
        
        radius2 = radius-gapwidth-centerwidth
        curve2 = cad.shapes.Disk((x0+couplinglength,y0-gapwidth-centerwidth-radius2), radius=radius2, inner_radius=radius2-gapwidth, initial_angle=90,final_angle=0)
        
        if squid==False:
            addto = [hanger1,hanger2,hanger3,hanger4,curve1,curve2]
        else:
            addto = [hanger1,hanger2,hanger3,hanger4,curve1,curve2,hanger_squid_top1,hanger_squid_top2]    
        for toadd in addto:
            self.hanger_cell.add(toadd)

        return self.hanger_cell

