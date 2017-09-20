import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.utilities import line_polygon,arc_polygon, join_polygons
import gdsCAD as cad
import copy
import numpy as np

class MeanderingLine(cad.core.Cell):
    """docstring for MeanderingLine"""
    def __init__(self, 
        points = [[-100,0],[-100,-50],[-50,-50],[-50,0],[50,0],[50,-50],[0,-50]],
        turn_radius = 16.,
        line_width = 10.,
        layer = 1,
        path = False,
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

        super(MeanderingLine, self).__init__(name)
        cad.core.default_layer=layer

        if path == False:
            # i.e. make a boundary
            if len(points) == 2:
                line = line_polygon(points[0],points[1], line_width)
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
                    if i ==1:
                        line = line_polygon(sec[0],sec[1], line_width)
                    else:
                        line =join_polygons(line,line_polygon(sec[0],sec[1], line_width))
                    line = join_polygons(line,arc_polygon(curve_center, turn_radius, line_width,\
                                        initial_angle=angle_i, final_angle=angle_i+angle_delta, number_of_points = 199))
                    sec=[p_after]
                sec.append([points[n_last][0],points[n_last][1]])
                line = join_polygons(line,line_polygon(sec[0],sec[1], line_width))
            
            self.boundary = line
            self.add(line)


        if path == True:
            line  = cad.core.Elements()
            n_last = len(points)-1
            sec = [points[0]]
            for i in range(1,n_last):
                p = np.array(points[i])
                p_before = np.array([points[i][0]+turn_radius*sign(points[i-1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i-1][1]-points[i][1])])
                p_after = np.array([points[i][0]+turn_radius*sign(points[i+1][0]-points[i][0]),points[i][1]+turn_radius*sign(points[i+1][1]-points[i][1])])
                curve_center = p_after + p_before - p
                angle_i = angle(p_before - curve_center)
                angle_delta = angle(p_after - curve_center)-angle_i
                print angle_i,angle_delta
                if angle_delta < -180.:
                    angle_delta+=360.
                if angle_delta > 180.:
                    angle_delta-=360.
                print angle_i,angle_delta
                sec.append(p_before)
                line.add(cad.core.Path(sec, line_width))
                line.add(cad.shapes.Circle(curve_center, turn_radius, line_width,\
                    initial_angle=angle_i, final_angle=angle_i+angle_delta))
                sec=[p_after]
            sec.append([points[n_last][0],points[n_last][1]])
            line.add(cad.core.Path(sec, line_width))

            self.add([line])



if __name__ == '__main__':
  chipsize = 250
  chip = Base_Chip('line', chipsize, chipsize,label=False)
  cp = MeanderingLine()
  chip.add_component(cp, (0,0))
  chip.save_to_gds(show=True, save=False,loc='')