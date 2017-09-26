import numpy as np
from stcad.source_dev.chip import Base_Chip
from stcad.source_dev.utilities import double_line_polygon,double_arc_polygon,line_polygon
from stcad.source_dev.meandering_line import MeanderingLine
import gdsCAD as cad
import copy
import numpy as np

def sign(x):
  if x<0:
    return -1.
  if x==0:
    return 0.
  if x>0:
    return 1.

def angle(vec):
    return np.arctan2(vec[1],vec[0])*180./np.pi

def norm(vec):
    return np.sqrt(vec[0]**2+vec[1]**2)

class CPW(cad.core.Cell):
    """docstring for CPW"""
    def __init__(self, 
        points,
        turn_radius = 5.,
        pin = 1.,
        gap = 1.,
        layer = 1,
        name='cpw'):   


        super(CPW, self).__init__(name)
        cad.core.default_layer=layer
        points = np.array(points)
        self.points = points
        self.length = 0.
        self.pin = pin
        self.gap = gap
        self.layer = layer

        if len(points) == 2:
            self.add(double_line_polygon(points[0],points[1],gap,pin))
            self.length += norm(points[1]-points[0])
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
                self.add(double_line_polygon(sec[0],sec[1],gap,pin))
                self.length += norm(sec[1]-sec[0])
                self.add(double_arc_polygon(curve_center, turn_radius,gap,pin,\
                                    initial_angle=angle_i, final_angle=angle_i+angle_delta, number_of_points = 199))
                self.length += 2*np.pi*turn_radius*abs(angle_delta)/360.
                sec=[p_after]
            sec.append([points[n_last][0],points[n_last][1]])
            self.add(double_line_polygon(sec[0],sec[1],gap,pin))
            self.length += norm(sec[1]-sec[0])

    def add_launcher(self,pos,bonding_pad_length = 50,bonding_pad_gap = 30,bonding_pad_width =40,taper_length = 100,buffer_length = 30):
        if pos == 'beginning' or pos=='b':
            p_0 = self.points[0]
            p_1 = self.points[1]
        elif pos=='end' or pos=='e':
            p_0 = self.points[-1]
            p_1 = self.points[-2]
        else:
            raise ValueError("First argumnet should be either 'beginning' or 'b' or 'end' or 'e'")
        cad.core.default_layer=self.layer
        
        vec = p_1-p_0
        if vec[0] == 0:
            if vec[1] > 0:
                dir = 'up'
            else:
                dir = 'down'
        else:
            if vec[0] > 0:
                dir = 'right'
            else:
                dir = 'left'

        startpoint = 0
        transl = pos

        launchpoints_top = [[-buffer_length-taper_length-bonding_pad_length, 0 ],
                            [-buffer_length-taper_length-bonding_pad_length, bonding_pad_gap + bonding_pad_width/2. ],
                            [-buffer_length-taper_length-bonding_pad_length, bonding_pad_gap + bonding_pad_width/2. ],
                            [-taper_length, bonding_pad_gap + bonding_pad_width/2. ],
                            [0, self.gap + self.pin/2. ],
                            [0, self.pin/2. ],
                            [-taper_length, bonding_pad_width/2. ],
                            [-taper_length-bonding_pad_length, bonding_pad_width/2. ],
                            [-taper_length-bonding_pad_length,0. ]]

        launcher1 = cad.core.Boundary(launchpoints_top,layer = self.layer)
        launcher2 = cad.utils.reflect(launcher1, 'x')

        launcherlist = cad.core.Elements([launcher1, launcher2])

        if dir == 'left':
            launcherlist = cad.utils.reflect(launcherlist, 'y')
        elif dir == 'down':
            launcherlist = cad.utils.rotate(launcherlist, -90)
        elif dir == 'up':
            launcherlist = cad.utils.rotate(launcherlist, 90)
        elif dir == 'right':
            pass

        launcherlist = cad.utils.translate(launcherlist, p_0)
        self.add(launcherlist)

    def add_open(self,pos,length = 10):
        if pos == 'beginning' or pos=='b':
            p_0 = self.points[1]
            p_1 = self.points[0]
        elif pos=='end' or pos=='e':
            p_0 = self.points[-2]
            p_1 = self.points[-1]
        else:
            raise ValueError("First argumnet should be either 'beginning' or 'b' or 'end' or 'e'")
        cad.core.default_layer=self.layer
        # normalize vector
        vec = p_1-p_0
        vec = vec/norm(vec)
        vec*=length
        self.add(line_polygon(p_1,p_1+vec, self.gap*2.+self.pin))




if __name__ == '__main__':
  chipsize = 250
  chip = Base_Chip('CPW', chipsize, chipsize,label=False)
  cp = CPW([[-100,-50],[-50,-50],[-50,0],[50,0],[50,-50],[0,-50]],pin=3,gap=5)
  print cp.length
  cp.add_launcher('beginning')
  cp.add_open('end')
  chip.add_component(cp, (0,0))
  chip.save_to_gds(show=True, save=True,loc='')
