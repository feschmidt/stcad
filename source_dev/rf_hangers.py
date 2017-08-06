import numpy as np
import gdsCAD as cad
import source_dev.utilities as utils

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
    """

    def __init__(self, name, dict_hangers):

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

        # hard coded values
        self.radius = 100

        self.cell = cad.core.Cell('RF CELL')

    def gen_full(self):
        """
        Generate four RF hangers coupled to transmission line with lengths
        length, length - 430, length - 830,length - 1.2e3
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        length = self.length

        # Hard coded values
        spacing = 1.8e3
        lengthvals = [length, length - 430, length - 830, length - 1.2e3]

        for xx, value in enumerate(lengthvals):
            hanger = self.gen_hanger(value,(x0+xx*spacing,y0))
        
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


    def gen_hanger(self, length, pos):
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
            hangerpoints_1 = [(x0,y0),
                            (x0 + couplinglength,y0),
                            (x0 + couplinglength,y0-gapwidth),
                            (x0 + gapwidth, y0-gapwidth),
                            (x0 + gapwidth, y0-gapwidth-centerwidth/2),
                            (x0, y0-gapwidth-centerwidth/2)]
            hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                            (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius)]
        hanger1 = cad.core.Boundary(hangerpoints_1)
        hanger2 = cad.core.Boundary(hangerpoints_2)
        hanger3 = cad.utils.reflect(hanger1,'x',origin=(0,y0-gapwidth-centerwidth/2))
        hanger4 = cad.utils.reflect(hanger2,'y',origin=(x0+couplinglength+radius-gapwidth-centerwidth/2,0))
        
        radius1 = radius                
        curve1 = cad.shapes.Disk((x0+couplinglength,y0-radius1), radius=radius, inner_radius=radius1-gapwidth, initial_angle=90,final_angle=0)
        
        radius2 = radius-gapwidth-centerwidth
        curve2 = cad.shapes.Disk((x0+couplinglength,y0-gapwidth-centerwidth-radius2), radius=radius2, inner_radius=radius2-gapwidth, initial_angle=90,final_angle=0)
            
        for toadd in [hanger1,hanger2,hanger3,hanger4,curve1,curve2]:
            self.hanger_cell.add(toadd)

        return self.hanger_cell

