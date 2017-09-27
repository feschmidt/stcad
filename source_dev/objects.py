import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.meandering_line import MeanderingLine
import gdsCAD as cad
import copy

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



class Drum(cad.core.Cell):
    """docstring for Drum"""
    def __init__(self, base_layer = 1,
                    sacrificial_layer = 2 ,
                    top_layer = 3,
                    outer_radius = 9,
                    head_radius = 7,
                    electrode_radius = 6,
                    cable_width = 0.5,
                    sacrificial_tail_width = 3,
                    sacrificial_tail_length = 3,
                    opening_width = 4,
                    N_holes = 3,
                    hole_angle = 45,
                    hole_distance_to_center = 4.5,
                    hole_distance_to_edge = 0.5,
                    name = ''):
        super(Drum, self).__init__(name)
        hole_radius = (head_radius-hole_distance_to_edge-hole_distance_to_center)/2.
        opening_angle = np.arcsin(float(opening_width)/float(head_radius)/2.)*180/np.pi


        ##################################
        # Head (holey section)
        ##################################

        cad.core.default_layer=top_layer
        holy_section_of_head = cad.core.Elements()


        angle_start = 0
        angle_end = hole_angle
        section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
          initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
        hole_2_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_end/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_end/180.*np.pi)]
        hole_2 = cad.shapes.Disk(hole_2_position, hole_radius,layer=top_layer)
        section=xor_polygons(section,hole_2)
        holy_section_of_head.add(section)


        for i in range(N_holes-1):
          angle_start = hole_angle+i*(180-2*hole_angle)/(N_holes-1)
          angle_end = hole_angle+(i+1)*(180-2*hole_angle)/(N_holes-1)
          section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
            initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
          hole_1_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_start/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_start/180.*np.pi)]
          hole_1 = cad.shapes.Disk(hole_1_position, hole_radius,layer=top_layer)
          hole_2_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_end/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_end/180.*np.pi)]
          hole_2 = cad.shapes.Disk(hole_2_position, hole_radius,layer=top_layer)
          section=xor_polygons(section,hole_1)
          section=xor_polygons(section,hole_2)
          holy_section_of_head.add(section)


        angle_start = 180-hole_angle
        angle_end = 180
        section = cad.shapes.Disk((0,0), head_radius-hole_distance_to_edge, inner_radius = hole_distance_to_center,\
          initial_angle=angle_start, final_angle=angle_end, layer=top_layer)
        hole_1_position=[(hole_distance_to_center+hole_radius)*np.cos(angle_start/180.*np.pi),(hole_distance_to_center+hole_radius)*np.sin(angle_start/180.*np.pi)]
        hole_1 = cad.shapes.Disk(hole_1_position, hole_radius,layer=top_layer)
        section=xor_polygons(section,hole_1)
        holy_section_of_head.add(section)

        ##################################
        # Head (rest + supports)
        ##################################

        drum_head_outer = cad.shapes.Disk((0,0), head_radius, inner_radius = hole_distance_to_center+2*hole_radius, layer=top_layer) 
        drum_head_inner = cad.shapes.Disk((0,0), hole_distance_to_center, layer=top_layer) 


        support_top = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
          initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer)
        support_bottom = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
          initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer).copy().reflect('x')



        ##################################
        # Electrode
        ##################################

        electrode = cad.shapes.Disk((0,0), electrode_radius, layer=base_layer) 
        electrode_tail = cad.core.Path([[-outer_radius,0],[outer_radius,0]], cable_width,layer = base_layer)



        ##################################
        # Sacrificial layer
        ##################################


        sacrificial_drum = cad.shapes.Disk((0,0), head_radius, layer=sacrificial_layer) 
        sacrificial_tail = cad.core.Path([[-head_radius-sacrificial_tail_length,0],[head_radius+sacrificial_tail_length,0]],\
         sacrificial_tail_width,layer = sacrificial_layer)


        ##################################
        # Add all components
        ##################################

        self.add([holy_section_of_head,holy_section_of_head.copy().reflect('x'), drum_head_inner,drum_head_outer,support_bottom,support_top])
        self.add([electrode,electrode_tail])
        self.add([sacrificial_tail,sacrificial_drum])


class CPW(cad.core.Cell):
    """docstring for CPW"""
    def __init__(self, 
        points,
        turn_radius = 5.,
        pin = 4.,
        gap = 2.,
        layer = 1,
        name=''):   


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

    def add_launcher(self,pos,bonding_pad_length = 400,bonding_pad_gap = 200,bonding_pad_width =500,taper_length = 500,buffer_length = 100):
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
        L = k1*mu_0*float(self.n)**2*da*1.e-6/(1+k2*rho)
        C = self.do*6.7e-15/40.
        print "L = " +str(L*1.e9) +" nH"
        print "C = " +str(C*1.e15) +" fF"
        print "(self-resonance) f = " +str(1./np.sqrt(L*C)/2./np.pi/1e9) +" GHz"


    def resonance(self, C):

        k1 = 2.34
        k2 = 2.75
        rho = (self.do-self.di)/(self.do+self.di)
        da = 0.5*(self.do+self.di)
        mu_0 = 4.*np.pi*1.e-7
        L = k1*mu_0*float(self.n)**2*da*1.e-6/(1+k2*rho)
        C_self = self.do*6.7e-15/40.
        print "f = " +str(1./np.sqrt(L*(C+C_self))/2./np.pi/1e9) +" GHz"
        
        
class FourPointProbe(cad.core.Cell):
    """
    Creates a four point probe setup
    """
    def __init__(self, w=10, l=100, padw=300, lead=50, probew=5, negative=False, layer=1, name='4P'):   

        super(FourPointProbe, self).__init__(name)
        
        # negative
        points_neg = [(0,w),
                    (l/2+lead,w),
                    (l/2+lead,lead+padw),
                    (l/2+lead+padw,lead+padw),
                    (l/2+lead+padw,lead),
                    (l/2+lead+w,lead),
                    (l/2+lead+w,0),
                    (l/2+probew,0),
                    (l/2+probew,-lead),
                    (l/2+probew+lead+padw,-lead),
                    (l/2+probew+lead+padw,-lead-padw),
                    (l/2+probew+lead,-lead-padw),
                    (l/2+probew+lead,-lead-probew),
                    (l/2,-lead-probew),
                    (l/2,0),
                    (0,0),
                    (0,-lead-1.2*padw),
                    (l/2+lead+1.2*padw,-lead-1.2*padw),
                    (l/2+lead+1.2*padw,lead+1.2*padw),
                    (0,lead+1.2*padw)]
                    
        # positive
        points_pos = [(0,w),
                    (l/2+lead,w),
                    (l/2+lead,lead+padw),
                    (l/2+lead+padw,lead+padw),
                    (l/2+lead+padw,lead),
                    (l/2+lead+w,lead),
                    (l/2+lead+w,0),
                    (l/2+probew,0),
                    (l/2+probew,-lead),
                    (l/2+probew+lead+padw,-lead),
                    (l/2+probew+lead+padw,-lead-padw),
                    (l/2+probew+lead,-lead-padw),
                    (l/2+probew+lead,-lead-probew),
                    (l/2,-lead-probew),
                    (l/2,0),
                    (0,0)]
                    
        if negative:
            bound = cad.core.Boundary(points_neg,layer=layer)
            labelloc = (l/2+lead,padw)
        else:
            bound = cad.core.Boundary(points_pos,layer=layer)
            labelloc = (-100,padw)
        bound2 = cad.utils.reflect(bound,'y')
        
        probecell = cad.core.Cell('4POINT')
        probecell.add(bound)
        probecell.add(bound2)

        # Add label
        labelcell = cad.core.Cell('LABEL')
        label = cad.shapes.Label('l='+str(l)+'\nw='+str(w), 50, labelloc, layer=layer)
        labelcell.add(label)
        
        self.add(probecell)
        self.add(labelcell)
