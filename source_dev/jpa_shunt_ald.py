import numpy as np
import gdsCAD as cad
import source_dev.utilities as utils

class JPA():
    """
    Class for JPA from Appl. Phys. Lett. 103, 122602 (2013)
    """

    def __init__(self, name, dict_jpa, overlap=2, box=(60,90)):

        self.name = name
        self.dict_jpa = dict_jpa
        self.feedlength = self.dict_jpa['feedlength']
        self.pos = self.dict_jpa['position']    # (x0,y0)
        self.shunt = self.dict_jpa['shunt']     # (xdim,ydim)
        self.squid = self.dict_jpa['squid']     # (loopx,loopy,xdimj,xdimy)
        self.squidfeed = self.dict_jpa['squidfeed']
        self.centerwidth = self.dict_jpa['centerwidth']
        self.gapwidth = self.dict_jpa['gapwidth']
        self.overlap = overlap
        self.box = box

        self.layer_bottom = 1
        self.layer_top = 2
        self.layer_ins = 3

        self.cell = cad.core.Cell('JPA CELL')

    def gen_full(self):
        """
        Generate JPA
        """

        baselayer = self.gen_baselayer(self.pos)
        shuntins = self.gen_shuntinsulation(self.pos)
        toplayer = self.gen_toplayer(self.pos)
        
        self.cell.add(baselayer)
        self.cell.add(shuntins)
        self.cell.add(toplayer)

        return self.cell


    def gen_baselayer(self, pos):
        
        self.basecell = cad.core.Cell('JPA 0')
        x0 = pos[0]
        y0 = pos[1]
        
        basepoints_feed = [(x0, y0),
                        (x0+self.feedlength+self.gapwidth, y0),
                        (x0+self.feedlength+self.gapwidth, y0+2*self.gapwidth+self.centerwidth),
                        (x0, y0+2*self.gapwidth+self.centerwidth),
                        (x0, y0+self.gapwidth+self.centerwidth),
                        (x0+self.feedlength, y0+self.gapwidth+self.centerwidth),
                        (x0+self.feedlength, y0+self.gapwidth),
                        (x0, y0+self.gapwidth)]
        
        x1 = x0+self.feedlength+self.gapwidth+self.shunt[0]
        y1 = y0+self.gapwidth+self.centerwidth/2-self.shunt[1]/2
        basepoints_dev = [(x1, y1),
                        (x1, y1+self.box[1]*2/3),
                        (x1+self.squidfeed, y1+self.box[1]*2/3),
                        (x1+self.squidfeed, y1+self.box[1]*2/3-self.squid[3]),
                        (x1+self.squidfeed-(self.squid[0]+5)/2-1, y1+self.box[1]*2/3-self.squid[3]),
                        (x1+self.squidfeed-(self.squid[0]+5)/2-1, y1+self.box[1]*2/3-2*self.squid[3]),
                        (x1+self.squidfeed+(self.squid[0]+5)/2+self.squid[3], y1+self.box[1]*2/3-2*self.squid[3]),
                        (x1+self.squidfeed+(self.squid[0]+5)/2+self.squid[3], y1+self.box[1]*2/3-self.squid[3]),
                        (x1+self.squidfeed+self.squid[3], y1+self.box[1]*2/3-self.squid[3]),
                        (x1+self.squidfeed+self.squid[3], y1+self.box[1]*2/3+self.squid[3]),
                        (x1, y1+self.box[1]*2/3+self.squid[3]),
                        (x1, y1+self.box[1]),
                        (x1+self.box[0], y1+self.box[1]),
                        (x1+self.box[0], y1+self.box[1]*4/5-self.gapwidth),
                        (x1+30, y1+self.box[1]*4/5-self.gapwidth),
                        (x1+30, y1+self.box[1]*1/5+self.gapwidth),
                        (x1+self.box[0], y1+self.box[1]*1/5+self.gapwidth),
                        (x1+self.box[0], y1)]
        basepoints_loop = [(x1+self.box[0], y1+self.box[1]*4/5-self.gapwidth-self.centerwidth),
                        (x1+self.box[0], y1+self.box[1]*1/5+self.gapwidth+self.centerwidth),
                        (x1+30+self.centerwidth, y1+self.box[1]*1/5+self.gapwidth+self.centerwidth),
                        (x1+30+self.centerwidth, y1+self.box[1]*4/5-self.gapwidth-self.centerwidth)]
        
        x2 = x1+self.box[0]
        y2 = y1+self.box[1]*4/5-2*self.gapwidth-self.centerwidth
        basepoints_fluxfeed1 = [(x2, y2+self.gapwidth),
                            (x2, y2),
                            (10e-3-pos[0], y0),
                            (10e-3-pos[0], y0+self.gapwidth)]
        x3 = x2
        y3 = y2+self.gapwidth+self.centerwidth
        basepoints_fluxfeed2 = [(x3, y3+self.gapwidth),
                            (x3, y3),
                            (10e-3-pos[0], y0+self.gapwidth+self.centerwidth),
                            (10e-3-pos[0], y0+self.gapwidth+self.gapwidth+self.centerwidth)]
        
        for points in [basepoints_feed,basepoints_dev,basepoints_loop,basepoints_fluxfeed1,basepoints_fluxfeed2]:
            element = cad.core.Boundary(points, layer=self.layer_bottom)
            self.basecell.add(element)
        return self.basecell
    
    
    
    def gen_shuntinsulation(self, pos):
    
        self.inscell = cad.core.Cell('JPA 1')
        x0 = pos[0]+self.feedlength+self.gapwidth
        y0 = pos[1]+self.gapwidth-self.shunt[1]/2
        
        inspoints = [(x0-self.overlap, y0-self.overlap),
                    (x0+self.shunt[0]+self.overlap, y0-self.overlap),
                    (x0+self.shunt[0]+self.overlap, y0+self.shunt[1]+self.overlap),
                    (x0-self.overlap, y0+self.shunt[1]+self.overlap)]
        insulator = cad.core.Boundary(inspoints, layer=self.layer_ins)
        self.inscell.add(insulator)
        return self.inscell
        
    
      
    def gen_toplayer(self, pos):
    
        self.inscell = cad.core.Cell('JPA 2')
        x0 = pos[0]+self.feedlength
        y0 = pos[1]+self.gapwidth
        
        shunttoppoints = [(x0-40, y0),
                    (x0+self.gapwidth, y0),
                    (x0+self.gapwidth, y0-self.shunt[1]/2),
                    (x0+self.gapwidth+self.shunt[0], y0-self.shunt[1]/2),
                    (x0+self.gapwidth+self.shunt[0], y0+self.shunt[1]/2),
                    (x0+self.gapwidth, y0+self.shunt[1]/2),
                    (x0+self.gapwidth, y0+self.centerwidth),
                    (x0-40, y0+self.centerwidth)]
        
        x1 = x0+self.gapwidth+self.shunt[0]+self.squidfeed-(self.squid[0]+5)/2
        y1 = y0+self.centerwidth/2-self.shunt[1]/2+self.box[1]*2/3-2*self.squid[3]
        squidtoppoints = [(x1, y1+self.squid[2]),
                        (x1, y1-self.squid[1]-self.squid[3]),
                        (x1+(self.squid[0]+self.squid[3])/2, y1-self.squid[1]-self.squid[3]),
                        (x1+(self.squid[0]+self.squid[3])/2, y1-self.squid[1]-2*self.squid[3]),
                        (pos[0]+self.feedlength+self.gapwidth+self.shunt[0], y1-self.squid[1]-2*self.squid[3]),
                        (pos[0]+self.feedlength+self.gapwidth+self.shunt[0], y1-self.squid[1]-3*self.squid[3]),
                        (x1+self.squid[0]/2+1.5*self.squid[3], y1-self.squid[1]-3*self.squid[3]),
                        (x1+self.squid[0]/2+1.5*self.squid[3], y1-self.squid[1]-self.squid[3]),
                        (x1+self.squid[0]+2*self.squid[3], y1-self.squid[1]-self.squid[3]),
                        (x1+self.squid[0]+2*self.squid[3], y1+self.squid[2]),
                        (x1+self.squid[0]+self.squid[3], y1+self.squid[2]),
                        (x1+self.squid[0]+self.squid[3], y1-self.squid[1]),
                        (x1+self.squid[3], y1-self.squid[1]),
                        (x1+self.squid[3], y1+self.squid[2])]
         
                    
        shunttop = cad.core.Boundary(shunttoppoints, layer=self.layer_top)
        squidtop = cad.core.Boundary(squidtoppoints, layer=self.layer_top)
        self.inscell.add(shunttop)
        self.inscell.add(squidtop)
        return self.inscell
                    
        
        
