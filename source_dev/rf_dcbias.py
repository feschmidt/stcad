import numpy as np
import gdsCAD as cad
import source_dev.utilities as utils

class RFShunt():
    """
    Class for RF DC bias cavities
    Initial values:
        - radius = 100
        - squid = False, i.e. no squid at the end. Can be set to true
    """

    def __init__(self, name, dict_dcbias, squid = False):

        self.name = name
        self.dict_dcbias = dict_dcbias
        self.length = self.dict_dcbias['length']
        self.pos = self.dict_dcbias['position']    # (x0,y0)
        self.feedlength = self.dict_dcbias['feedlength']
        self.shunt = self.dict_dcbias['shunt']     # (xdim,ydim)
        self.squid = self.dict_dcbias['squid']     # (loopx,loopy,xdimj,xdimy)
        self.centerwidth = self.dict_dcbias['centerwidth']
        self.gapwidth = self.dict_dcbias['gapwidth']

        self.layer_bottom = 1
        self.layer_top = 2
        self.layer_ins = 3

        # Option to add squid at the end
        self.squid = squid

        # hard coded values
        self.radius = 100

        self.cell = cad.core.Cell('RF CELL')

    def gen_full(self):
        """
        Generate four DC bias cavities with option to have squids at the end
        """

        x0 = self.pos[0]
        y0 = self.pos[1]
        feedlength = self.feedlength
        length = self.length

        baselayer = self.gen_baselayer(x0,y0,feedlength,self.squid)
        baselayer2 = cad.core.CellReference(baselayer,origin=(0,0),x_reflection=True)
        baselayer3 = cad.core.CellReference(baselayer,origin=(0,0),rotation = 180)
        baselayer4 = cad.core.CellReference(baselayer,origin=(0,0),rotation=180,x_reflection=True)
        #shuntins = self.gen_shuntinsulation(x0,y0,feedlength)
        #toplayer = self.gen_toplayer(x0,y0,feedlength,self.squid)
        
        self.cell.add(baselayer)
        self.cell.add(baselayer2)
        self.cell.add(baselayer3)
        self.cell.add(baselayer4)
        #self.cell.add(shuntins)
        #self.cell.add(toplayer)

        return self.cell


    def gen_baselayer(self, x0, y0, feedlength, squid):
        """
        Generate baselayer with SQUID (optional)
        """

        self.bias_cell = cad.core.Cell('RF_DC_BIAS')
        
        radius_cav = self.radius - self.gapwidth - self.centerwidth/2
        #part3 = length - feedlength - np.pi*radius_cav - midlength
        
        # Create feed to shunt
        part1points = [(x0, y0),
                    (x0+feedlength, y0),
                    (x0+feedlength, y0+self.gapwidth),
                    (x0, y0+self.gapwidth)]
        part1 = cad.core.Boundary(part1points, layer=self.layer_bottom)
        part11 = cad.utils.reflect(part1,'x',origin=(0,y0+self.gapwidth+self.centerwidth/2))
        
        
        # Create shunt
        x1 = x0+feedlength
        y1 = y0
        shuntpoints = [(x1, y1+self.gapwidth),
                     (x1, y1-self.shunt[1]/2),
                     (x1+self.shunt[0]+2*self.gapwidth, y1-self.shunt[1]/2),
                     (x1+self.shunt[0]+2*self.gapwidth, y1+self.gapwidth),
                     (x1+self.shunt[0]+self.gapwidth, y1+self.gapwidth),
                     (x1+self.shunt[0]+self.gapwidth, y1+self.gapwidth-self.shunt[1]/2),
                     (x1+self.gapwidth, y1+self.gapwidth-self.shunt[1]/2),
                     (x1+self.gapwidth, y1+self.gapwidth)]
        shunt1 = cad.core.Boundary(shuntpoints, layer=self.layer_bottom)
        shunt11 = cad.utils.reflect(shunt1,'x',origin=(0,y1+self.gapwidth+self.centerwidth/2))
        
        # Connect shunt to first turn
        x2 = x1+self.shunt[0]+2*self.gapwidth
        y2 = y0
        part2l = 2e3
        part2points = [(x2, y2),
                    (x2+part2l, y2),
                    (x2+part2l, y2+self.gapwidth),
                    (x2, y2+self.gapwidth)]
        part2 = cad.core.Boundary(part2points, layer=self.layer_bottom)
        part21 = cad.utils.reflect(part2,'x',origin=(0,y2+self.gapwidth+self.centerwidth/2))
        
        # Create first turn
        x3 = x2+part2l
        y3 = y0
        radius1 = self.radius                
        curve1 = cad.shapes.Disk((x3,y3+self.gapwidth+self.centerwidth+radius1), radius=radius1, inner_radius=radius1-self.gapwidth, initial_angle=270,final_angle=360, layer=self.layer_bottom)
        
        radius11 = self.radius + self.gapwidth + self.centerwidth
        curve11 = cad.shapes.Disk((x3,y3+radius11), radius=radius11, inner_radius=radius11-self.gapwidth, initial_angle=270,final_angle=360, layer=self.layer_bottom)
        
        
        
        
        for toadd in [part1, part11, shunt1, shunt11, part2, part21, curve1, curve11]:
            self.bias_cell.add(toadd)
        return self.bias_cell
        '''
        Insert rest here
        
        
        
        
        
        
        if squid==False:
            hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                            (x0+couplinglength+radius, y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth),
                            (x0+couplinglength+radius-gapwidth,y0-radius)]
        else:
            print 'Adding SQUID'
            hangerpoints_2 = [(x0+couplinglength+radius, y0-radius),
                        (x0+couplinglength+radius, y0-radius-restlength),
                        (x0+couplinglength+radius+50, y0-radius-restlength),
                        (x0+couplinglength+radius+50, y0-radius-restlength-gapwidth-100),
                        (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth-100),
                        (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth),
                        (x0+couplinglength+radius-gapwidth+25-centerwidth,y0-radius-restlength-gapwidth),
                        (x0+couplinglength+radius-gapwidth+25-centerwidth,y0-radius-restlength-gapwidth-50),
                        (x0+couplinglength+radius-gapwidth+25,y0-radius-restlength-gapwidth-50),
                        (x0+couplinglength+radius-gapwidth+25,y0-radius-restlength-gapwidth+centerwidth),
                        (x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth+centerwidth),
                        (x0+couplinglength+radius-gapwidth,y0-radius)]
            hangerpoints_squid_top = [(x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth-100-100),
                        (x0+couplinglength+radius-gapwidth-centerwidth/2,y0-radius-restlength-gapwidth-49),
                        (x0+couplinglength+radius-gapwidth-centerwidth/2+28,y0-radius-restlength-gapwidth-49),
                        (x0+couplinglength+radius-gapwidth-centerwidth/2+28,y0-radius-restlength-gapwidth-49-centerwidth),
                        (x0+couplinglength+radius-gapwidth,y0-radius-restlength-gapwidth-49-centerwidth),
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
        '''

