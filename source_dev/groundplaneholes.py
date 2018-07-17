import numpy as np
import gdsCAD as cad
from .objects import CPW
from .testing_fillet import fillet

class GroundPlaneHoles():
    '''
    '''
    def __init__(self, name, dict_holes):

        self.name = name
        self.cell = cad.core.Cell('HOLES') 

        self.xdim = 10e3
        self.ydim = 10e3
        self.smallx = 1e2
        self.smally = 1e2
        self.holes = [2.,2.]
        self.streets = [1.,1.]

        self.layer = 99
        
        for key,val in list(dict_holes.items()):
            setattr(self,key,val)

    
    def gen_full(self):
        """
        """
        self.smallcell = cad.core.Cell('SMALL HOLES')

        xlist = np.arange(-self.smallx/2.,self.smallx/2.,self.holes[0]+self.streets[0])
        ylist = np.arange(-self.smally/2.,self.smally/2.,self.holes[1]+self.streets[1])
        holes = []

        k = 0.
        for i,x in enumerate(xlist):
            for j,y in enumerate(ylist):
                hole = cad.shapes.Rectangle((x,y),(x+self.holes[0],y+self.holes[1]),layer=self.layer)
                self.smallcell.add(hole)
                k += 1.
                print('smallcell',(x,y), '{:.4} %'.format(k/len(xlist)/len(ylist)*100.))

        smallxlist = np.arange(-self.xdim/2.,self.xdim/2.,int(self.smallx+2*self.streets[0]))
        smallylist = np.arange(-self.ydim/2.,self.ydim/2.,int(self.smally+2*self.streets[0]))
 
        k = 0
        for i,x in enumerate(smallxlist):
            for j,y in enumerate(smallylist):
                self.cell.add(cad.core.CellReference(self.smallcell,origin=(x+self.smallx/2.,y+self.smally/2.)))
                print('bigcell',(x,y), '{:.4} %'.format(k/len(smallxlist)/len(smallylist)*100.))
                k+=1
        return self.cell

