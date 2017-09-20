import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.utilities import double_line_polygon,double_arc_polygon
from stcad.source_dev.meandering_line import MeanderingLine
import gdsCAD as cad
import copy
import numpy as np

class CPW(cad.core.Cell):
    """docstring for CPW"""
    def __init__(self, 
        points = [[-100,0],[-100,-50],[-50,-50],[-50,0],[50,0],[50,-50],[0,-50]],
        turn_radius = 5.,
        pin = 1.,
        gap = 1.,
        layer = 1,
        name=''):   

        def sign(x):
          if x<0:
            return -1.
          if x==0:
            return 0.
          if x>0:
            return 1.

        def angle(vec):
            return np.arctan2(vec[1],vec[0])*180./np.pi

        super(CPW, self).__init__(name)
        cad.core.default_layer=layer

        if len(points) == 2:
            line = line_polygon(points[0],points[1], pin)
        else:
            n_last = len(points)-1
            sec = [points[0]]
            for i in range(1,n_last):
                p = np.array(points[i])
                p_before = np.array([points[i][0]+turn_radius*sign(points[i-1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i-1][1]-points[i][1])])
                p_after = np.array([points[i][0]+turn_radius*sign(points[i+1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i+1][1]-points[i][1])])
                curve_center = p_after + p_before - p
                angle_i = angle(p_before - curve_center)
                angle_delta = angle(p_after - curve_center)-angle_i
                if angle_delta < -180.:
                    angle_delta+=360.
                if angle_delta > 180.:
                    angle_delta-=360.
                sec.append(p_before)
                self.add(double_line_polygon(sec[0],sec[1], pin,gap))
                self.add(double_arc_polygon(curve_center, turn_radius, pin,gap,\
                                    initial_angle=angle_i, final_angle=angle_i+angle_delta, number_of_points = 199))
                sec=[p_after]
            sec.append([points[n_last][0],points[n_last][1]])
            self.add(double_line_polygon(sec[0],sec[1], pin,gap))
        
        


if __name__ == '__main__':
  chipsize = 250
  chip = Base_Chip('CPW', chipsize, chipsize,label=False)
  cp = CPW()
  chip.add_component(cp, (0,0))
  chip.save_to_gds(show=True, save=True,loc='')