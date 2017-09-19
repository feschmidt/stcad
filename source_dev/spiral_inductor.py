import numpy as np
from stcad.source_dev.chip import Base_Chip
import gdsCAD as cad
import copy

class SpiralInductor(cad.core.Cell):
    """docstring for SpiralInductor"""
    def __init__(self, 
        exterior = 55.,
        coil_number = 45,
        line_width = 0.25,
        spacing = 0.25,
        bridge_width = 2.,
        overlap_square_width = 3.,
        tail_length = 5.,
        base_layer = 1,
        sacrificial_layer = 2,
        top_layer = 3,
        name=''):   


        super(SpiralInductor, self).__init__(name)
        do = float(exterior)
        n = coil_number
        self.do = do
        self.n = n
        pitch = line_width+spacing
        self.di = do-2.*pitch*n


        ##################
        # Spiral
        ##################


        spiral = cad.core.Elements()
        points = [[0,0]]
        for i in range(n-1):
          points.append([i*pitch,-do+i*pitch])
          points.append([do-i*pitch,-do+i*pitch])
          points.append([do-i*pitch,-i*pitch])
          points.append([(i+1)*pitch,-i*pitch])
        points.append([(n-1)*pitch,-do+(n-1)*pitch])
        points.append([do-(n-1)*pitch,-do+(n-1)*pitch])
        points.append([do-(n-1)*pitch,-do/2.])
        points.append([do/2.,-do/2.])
        spiral.add(cad.core.Path(points, line_width,layer = top_layer))


      # ##################
      # # Base layer
      # ##################


        overlap_square = cad.shapes.Rectangle((do/2.-overlap_square_width/2.,-do/2.-overlap_square_width/2.),\
         (do/2.+overlap_square_width/2.,-do/2.+overlap_square_width/2.), layer = base_layer)
        tail = cad.shapes.Rectangle((-tail_length,-do/2.+line_width),\
         (do/2.,-do/2.-line_width), layer = base_layer)


      # ##################
      # # Sacrificial layer
      # ##################

        sacrificial = cad.shapes.Rectangle((-tail_length,-do/2.+bridge_width/2.),\
         (do/2.-overlap_square_width/2.,-do/2.-bridge_width/2.), layer = sacrificial_layer)



        self.add([spiral,overlap_square,tail,sacrificial])

    def inductance(self):

        k1 = 2.34
        k2 = 2.75
        rho = (self.do-self.di)/(self.do+self.di)
        da = 0.5*(self.do+self.di)
        mu_0 = 4.*np.pi*1.e-7
        return k1*mu_0*float(self.n)**2*da*1.e-6/(1+k2*rho)

if __name__ == '__main__':
  chipsize = 200
  chip = Base_Chip('inductor', chipsize, chipsize,label=False)
  inductor = SpiralInductor()
  print inductor.inductance()
  chip.add_component(inductor, (0,0))
  chip.save_to_gds(show=True, save=True,loc='')