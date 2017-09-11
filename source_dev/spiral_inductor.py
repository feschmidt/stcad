import numpy as np
import gdsCAD as cad
import copy

class SpiralInductor(cad.core.Cell):
    """docstring for SpiralInductor"""
    def __init__(self,
        interior = 3, 
        exterior = 90,
        coil_number = 40,
        linewidth = 0.5,
        bridge_gap = 2,
        bridge_base_length = 3,
        bridge_base_overlap_length = 0.1,
        bridge_base_overlap_width = 0.05,
        base_layer = 1,
        sacrificial_layer = 2,
        bridge_layer = 3,
        name=''):   


        super(SpiralInductor, self).__init__(name)
        di = interior
        self.di = di
        do = exterior
        self.do = do
        n = coil_number
        self.n = n
        width = linewidth
        gap = bridge_gap
        pitch = (do-di)/(n-1)/2


        ##################
        # Draw Spiral
        ##################


        spiral = cad.core.Elements()
        points = [[0,0]]
        for i in range(n-1):
          points.append([i*pitch,-do/2+gap/2])
          spiral.add(cad.core.Path(points, width,layer = base_layer))
          points = []
          points.append([i*pitch,-do/2-gap/2])
          points.append([i*pitch,-do+i*pitch])
          points.append([do-i*pitch,-do+i*pitch])
          points.append([do-i*pitch,-i*pitch])
          points.append([(i+1)*pitch,-i*pitch])
        points.append([(n-1)*pitch,-do/2+gap/2])
        spiral.add(cad.core.Path(points, width,layer = base_layer))
        points = []
        points.append([(n-1)*pitch,-do/2-gap/2])
        points.append([(n-1)*pitch,-do+(n-1)*pitch])
        points.append([do-(n-1)*pitch,-do+(n-1)*pitch])
        points.append([do-(n-1)*pitch,-do/2])
        # points.append([(n)*pitch,-(n-1)*pitch])
        # points.append([(n)*pitch,-do/2])
        spiral.add(cad.core.Path(points, width,layer = base_layer))



        ##################
        # Draw tail of spiral
        ##################


        start_tail = copy.copy(points[-1])
        end_tail = [0,-do/2]
        tail = cad.core.Path([start_tail,end_tail], width,layer = base_layer)



        ##################
        # Draw base of bridge
        ##################


        bridge_base = cad.core.Elements()
        for i in range(n):
          points = []
          points.append([i*pitch,-do/2+gap/2+bridge_base_length])
          points.append([i*pitch,-do/2+gap/2-bridge_base_overlap_length])
          bridge_base.add(cad.core.Path(points, width+bridge_base_overlap_width*2,layer = sacrificial_layer))
          points = []
          points.append([i*pitch,-do/2-gap/2+bridge_base_overlap_length])
          points.append([i*pitch,-do/2-gap/2-bridge_base_length])
          bridge_base.add(cad.core.Path(points, width+bridge_base_overlap_width*2,layer = sacrificial_layer))


        ##################
        # Draw bridge
        ##################

        bridge_metal = cad.core.Elements()
        for i in range(n):
          points = []
          points.append([i*pitch,-do/2+gap/2])
          points.append([i*pitch,-do/2-gap/2])
          bridge_metal.add(cad.core.Path(points, width,layer = bridge_layer))


        self.add([spiral,bridge_metal,bridge_base,tail])

    def inductance(self):

        k1 = 2.34
        k2 = 2.75
        rho = (self.do-self.di)/(self.do+self.di)
        da = 0.5*(self.do+self.di)
        mu_0 = 4.*np.pi*1.e-7
        return k1*mu_0*self.n**2*da*1.e-6/(1+k2*rho)


