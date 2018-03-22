import numpy as np
from scipy.constants import epsilon_0
from stcad.source_dev.utilities import *
import gdsCAD as cad
import copy
from stcad.source_dev.chip import Base_Chip

def increment(points,dx,dy):
    return points+[[points[-1][0]+dx,points[-1][1]+dy]]

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



class WaffleCapacitor(cad.core.Cell):
    """docstring for WaffleCapacitor"""
    def __init__(self,base_width, 
        base_lead_length, 
        base_line_width, 
        ground_length, 
        n_holes, 
        base_hole_diameter, 
        sacrificial_width_overlap, 
        side_support, 
        release_hole_diameter, 
        ground = True,
        base_layer =1, 
        base_hole_layer =4, 
        sacrificial_layer =2, 
        sacrificial_hole_layer =5, 
        top_layer =3, 
        top_hole_layer =6,
        name = ''):
        super(WaffleCapacitor, self).__init__(name)
        self.base_width = base_width
        self.base_lead_length = base_lead_length
        self.base_line_width = base_line_width
        self.ground_length = ground_length
        self.n_holes = n_holes
        self.base_hole_diameter = base_hole_diameter
        self.sacrificial_width_overlap = sacrificial_width_overlap
        self.side_support = side_support
        self.release_hole_diameter = release_hole_diameter
        self.base_layer = base_layer
        self.base_hole_layer = base_hole_layer
        self.sacrificial_layer = sacrificial_layer
        self.sacrificial_hole_layer = sacrificial_hole_layer
        self.top_layer = top_layer
        self.top_hole_layer = top_hole_layer

        # base layer
        base_hex = Hexagon(width = base_width,layer = base_layer, name = name+'base_hex')
        hex_width = base_width+base_lead_length*2.


        if ground:
            base_hex.add_leads_on_sides(base_lead_length,base_line_width)
            points = [[-hex_width/2.+base_lead_length*np.sin(np.pi/6),base_lead_length*np.cos(np.pi/6)],\
                        [-hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
                        [+hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
                        [+hex_width/2.,0],\
                        [+hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
                        [-hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)],
                        [-hex_width/2.+base_lead_length*np.sin(np.pi/6),-base_lead_length*np.cos(np.pi/6)],
                        [-hex_width/2.-ground_length,-base_lead_length*np.cos(np.pi/6)],
                        [-hex_width/2.-ground_length,-hex_width/2.-ground_length],
                        [+hex_width/2.+ground_length,-hex_width/2.-ground_length],
                        [+hex_width/2.+ground_length,+hex_width/2.+ground_length],
                        [-hex_width/2.-ground_length,+hex_width/2.+ground_length],
                        [-hex_width/2.-ground_length,+base_lead_length*np.cos(np.pi/6)],]
            self.add(cad.core.Boundary(points,layer = base_layer))
            self.add(cad.core.Boundary(points,layer = top_layer))
        else:
            base_hex.add_lead_on_1_side(base_lead_length,base_line_width)


        self.add(base_hex)

        # base holes
        base_margin = base_width/(n_holes)/np.sqrt(2)
        base_holes = hex_array_of_holes(base_margin,base_width,n_holes,base_hole_diameter,base_hole_layer, name = name+'base_holes')
        self.n_base_holes = base_holes.n
        self.add(base_holes)

        # sacrificial layer
        sacrificial_width = base_width+2*sacrificial_width_overlap
        sacrificial_hex = Hexagon(width = sacrificial_width,layer = sacrificial_layer, name = name+'sacrificial_hex')
        if ground:
            sacrificial_hex.add_leads_on_sides(base_lead_length,base_line_width+2*sacrificial_width_overlap)
        else:
            sacrificial_hex.add_lead_on_1_side(base_lead_length,base_line_width+2*sacrificial_width_overlap)
        self.add(sacrificial_hex)

        # sacrificial holes
        sacrificial_holes = hex_array_of_holes(base_margin,base_width,n_holes,base_hole_diameter-2*sacrificial_width_overlap,sacrificial_hole_layer, name = name+'sacrificial_holes')
        self.n_sacrificial_holes = sacrificial_holes.n
        self.add(sacrificial_holes)

        # top layer
        top_width =  sacrificial_width+2*side_support
        sacrificial_hex = Hexagon(width =top_width,layer = top_layer, name = name+'top_hex')
        self.add(sacrificial_hex)
        cad.core.default_layer=top_layer
        self.add(line_polygon([-top_width/2.+base_line_width,0], [-hex_width/2.-ground_length,0], base_line_width))

        # top holes
        top_holes = hex_array_of_holes(base_margin/2.,base_width,2*n_holes+1,release_hole_diameter,top_hole_layer, skip_some=True, name = name+'top_holes')
        self.n_top_holes = top_holes.n
        self.add(top_holes)
        
        self.area = 3.*np.sqrt(3)/2.*float(self.base_width*1.e-6)**2
        self.area -=self.n_base_holes*np.pi*(float(self.base_hole_diameter*1.e-6)/2.)**2
        self.area -=self.n_top_holes*np.pi*(float(self.release_hole_diameter*1.e-6)/2.)**2

    def capacitance(self,gap):

        return epsilon_0*self.area/gap

class hex_array_of_holes(cad.core.Cell):
    """docstring for ClassName"""
    def __init__(self, margin, base_width,n_holes, hole_diameter, layer, skip_some = False, name=''):
        super(hex_array_of_holes, self).__init__(name)

        self.n = 0

        if n_holes%2==0:
            raise ValueError("the width should contain an odd number of holes") 
        half_height = np.sqrt(base_width**2/4.-base_width**2/16.)-margin
        pitch_vertical = half_height/float((n_holes+1)/2-1)
        if skip_some == False:
            for i in range((n_holes+1)/2):
                y = i*pitch_vertical
                x_start = (base_width)/2.-margin*2./np.sqrt(3)-(y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                for x in x_array:
                    self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                    self.n +=1
            for i in range(1,(n_holes+1)/2):
                y = -i*pitch_vertical
                x_start = (base_width)/2.-margin-(-y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                for x in x_array:
                    self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                    self.n +=1
        else:
            for i in range((n_holes+1)/2):
                y = i*pitch_vertical
                x_start = (base_width)/2.-margin*2./np.sqrt(3)-(y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                j = 0
                for x in x_array:
                    if i%2==0 and (j+1)%2==0:
                        pass
                    else:
                        self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                        self.n +=1
                    j+=1
            for i in range(1,(n_holes+1)/2):
                y = -i*pitch_vertical
                x_start = (base_width)/2.-margin-(-y)/np.tan(np.pi/3.)
                x_array = np.linspace(-x_start,x_start,n_holes-i)
                j = 0
                for x in x_array:
                    if i%2==0 and (j+1)%2==0:
                        pass
                    else:
                        self.add(cad.shapes.Disk((x,y), hole_diameter/2.,layer =layer))
                        self.n +=1
                    j+=1


class MeanderingLine(cad.core.Cell):
    """docstring for MeanderingLine"""
    def __init__(self, 
        points = [[-100,0],[-100,-50],[-50,-50],[-50,0],[50,0],[50,-50],[0,-50]],
        turn_radius = 16.,
        line_width = 10.,
        layer = None,
        path = False,
        name=''):   

        def sign(x):
          if x<0:
            return -1.
          if x==0:
            return 0.
          if x>0:
            return 1.

        super(MeanderingLine, self).__init__(name)
        if layer != None:
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
                if angle_delta < -180.:
                    angle_delta+=360.
                if angle_delta > 180.:
                    angle_delta-=360.
                sec.append(p_before)
                line.add(cad.core.Path(sec, line_width))
                line.add(cad.shapes.Circle(curve_center, turn_radius, line_width,\
                    initial_angle=angle_i, final_angle=angle_i+angle_delta))
                sec=[p_after]
            sec.append([points[n_last][0],points[n_last][1]])
            line.add(cad.core.Path(sec, line_width))

            self.add([line])

class Hexagon(cad.core.Cell):
    """docstring for Hexagon"""
    def __init__(self, width, layer = cad.core.default_layer,name=''):
        super(Hexagon, self).__init__(name)
        self.width = width
        self.name = name
        self.layer = layer
        hex_width = width

        self.points = [[-hex_width/2.,0],\
            [-hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
            [+hex_width/4.,np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
            [+hex_width/2.,0],\
            [+hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)],\
            [-hex_width/4.,-np.sqrt(hex_width**2/4.-hex_width**2/16.)]]
        self.add(cad.core.Boundary(self.points,layer = self.layer))

    def add_leads_on_sides(self,lead_length,line_width):
        cad.core.default_layer = self.layer
        for i in range(-1,5):
            self.add(perpendicular_line(self.points[i],self.points[i+1],lead_length,line_width))

    def add_lead_on_1_side(self,lead_length,line_width):
        cad.core.default_layer = self.layer
        self.add(perpendicular_line(self.points[0],self.points[1],lead_length,line_width))


class Drum(cad.core.Cell):
    """docstring for Drum"""
    def __init__(self, base_layer = 1,
                    sacrificial_layer = 2 ,
                    top_layer = 3,
                    hole_layer = None,
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
                    split_electrode = False,
                    electrode_splitting = 0.25,
                    right_sacrificial_tail = None,
                    name = ''):
        super(Drum, self).__init__(name)

        self.base_layer = base_layer,
        self.sacrificial_layer = sacrificial_layer ,
        self.top_layer = top_layer,
        self.hole_layer = hole_layer,
        self.outer_radius = outer_radius,
        self.head_radius = head_radius,
        self.electrode_radius = electrode_radius,
        self.cable_width = cable_width,
        self.sacrificial_tail_width = sacrificial_tail_width,
        self.sacrificial_tail_length = sacrificial_tail_length,
        self.opening_width = opening_width,
        self.N_holes = N_holes,
        self.hole_angle = hole_angle,
        self.hole_distance_to_center = hole_distance_to_center,
        self.hole_distance_to_edge = hole_distance_to_edge,
        self.split_electrode = split_electrode,
        self.electrode_splitting = electrode_splitting,
        self.right_sacrificial_tail = right_sacrificial_tail



        hole_radius = (head_radius-hole_distance_to_edge-hole_distance_to_center)/2.
        opening_angle = np.arcsin(float(opening_width)/float(head_radius)/2.)*180/np.pi


        ##################################
        # Head (holey section)
        ##################################

        cad.core.default_layer=top_layer
        holy_section_of_head = cad.core.Elements()
        hole_cell = cad.core.Elements()


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

          # Just hole cell for the substraction case
          if hole_layer != None:
              hole_cell.add(cad.shapes.Disk(hole_1_position, hole_radius,layer=hole_layer))
              hole_cell.add(cad.shapes.Disk(hole_2_position, hole_radius,layer=hole_layer))



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


        if hole_layer != None:
            
            # With substracting holes
            drum_head = cad.shapes.Disk((0,0), head_radius, layer=top_layer) 



        support_top = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
          initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer)
        support_bottom = cad.shapes.Disk((0,0), outer_radius, inner_radius = head_radius,\
          initial_angle=opening_angle, final_angle=180-opening_angle, layer=top_layer).copy().reflect('x')


        ##################################
        # Sacrificial layer
        ##################################


        cad.core.default_layer=sacrificial_layer
        sacrificial_drum = cad.shapes.Disk((0,0), head_radius, layer=sacrificial_layer) 
        if right_sacrificial_tail == None:
            sacrificial_tail = cad.core.Path([[-head_radius-sacrificial_tail_length,0],[head_radius+sacrificial_tail_length,0]],\
         sacrificial_tail_width,layer = sacrificial_layer)
        else:
            sacrificial_tail = cad.core.Path([[-head_radius-sacrificial_tail_length,0],[head_radius+right_sacrificial_tail,0]],\
         sacrificial_tail_width,layer = sacrificial_layer)


        ##################################
        # Electrode
        ##################################

        cad.core.default_layer=base_layer
        if split_electrode == False:
            electrode = cad.shapes.Disk((0,0), electrode_radius, layer=base_layer) 
            self.add([electrode])
        else:
            disk = cad.shapes.Disk((0,0), electrode_radius, layer=base_layer) 
            square_left = cad.shapes.Rectangle([-electrode_radius,electrode_radius],[+electrode_splitting/2.,-electrode_radius])
            square_right = cad.shapes.Rectangle([+electrode_radius,electrode_radius],[-electrode_splitting/2.,-electrode_radius])
            
            self.add([xor_polygons(disk,square_left)])
            self.add([xor_polygons(disk,square_right)])

        ##################################
        # Add all components
        ##################################

        if hole_layer==None:
            self.add([holy_section_of_head,holy_section_of_head.copy().reflect('x'), drum_head_inner,drum_head_outer,support_bottom,support_top])
        else:
            self.add([hole_cell,hole_cell.copy().reflect('x'), drum_head,support_bottom,support_top])
        
        # self.add([electrode_tail])
        self.add([sacrificial_tail,sacrificial_drum])

class WheelDrum(cad.core.Cell):
    """docstring for Drum"""
    def __init__(self, base_layer = 1,
                    sacrificial_layer = 2 ,
                    top_layer = 3,
                    electrode_radius = 6.,
                    spoke_length = 3.,
                    rim_width = 10.,
                    lead_width = 0.5,
                    opening_width = 1.,
                    top_base_overlap = 4.,
                    drum_head_radius = 5.,
                    n_spokes = 7,
                    spoke_width = 0.5,
                    entrance_support_width = 0.5,
                    name = ''):
        super(WheelDrum, self).__init__(name)
        opening_angle_top = np.arcsin(float(opening_width)/float(electrode_radius+spoke_length)/2.)*180/np.pi
        opening_angle_base = np.arcsin(float(opening_width+2.*entrance_support_width)/float(electrode_radius+spoke_length)/2.)*180/np.pi


        ##################################
        # base layer
        ##################################

        cad.core.default_layer=base_layer

        # Electrode
        disk = cad.shapes.Disk((0,0), electrode_radius, layer=base_layer)         
        self.add(disk)

        # Lead
        lead = MeanderingLine(points = [[0,0],[(electrode_radius+spoke_length+rim_width),0]],
            line_width = lead_width,
            layer = base_layer,
            name = name+'_lead')
        self.add(lead)

        # Rim
        rim = cad.shapes.Disk((0,0), ( spoke_length+rim_width+electrode_radius), inner_radius =( spoke_length+electrode_radius), layer=base_layer)
        gap = cad.shapes.Rectangle([0,-opening_width/2.-entrance_support_width],[electrode_radius+spoke_length+rim_width,opening_width/2.+entrance_support_width])
            
        self.add([xor_polygons(rim,gap)])

        ##################################
        # sacrificial layer
        ##################################

        cad.core.default_layer=sacrificial_layer
        rim = cad.shapes.Disk((0,0), ( spoke_length+rim_width+electrode_radius-top_base_overlap), inner_radius =( spoke_length+electrode_radius), layer=sacrificial_layer)
        gap = cad.shapes.Rectangle([0,-opening_width/2.-entrance_support_width],[electrode_radius+spoke_length+rim_width,opening_width/2.+entrance_support_width])
        self.add([xor_polygons(rim,gap)])


        center = cad.shapes.Disk((0,0), ( spoke_length+electrode_radius), layer=sacrificial_layer)
        self.add(center)

        ##################################
        # top layer
        ##################################

        cad.core.default_layer=top_layer

        # Rim
        rim = cad.shapes.Disk((0,0), ( spoke_length+rim_width+electrode_radius), inner_radius =( spoke_length+electrode_radius), layer=top_layer)
        gap = cad.shapes.Rectangle([0,-opening_width/2.],[electrode_radius+spoke_length+rim_width,opening_width/2.])
        self.add(xor_polygons(rim,gap))

        # Drum head
        drum_head = cad.shapes.Disk((0,0), drum_head_radius, layer=top_layer)         
        self.add(drum_head)

        # Spokes

        delta_angle = 360./float(n_spokes)
        radius = spoke_length+rim_width+electrode_radius
        angle = 0.+delta_angle/2.
        for n in range(n_spokes):
            x = radius*np.cos(angle*np.pi/180.)
            y = radius*np.sin(angle*np.pi/180.)
            spoke = MeanderingLine(points = [[0,0],[x,y]],
            line_width = spoke_width,
            layer = top_layer,
            name = name+'spoke_'+str(n))
            self.add(spoke)
            angle+=delta_angle




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
        cad.core.default_layer = layer
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
        kinetic_inductance = 0.,
        patch = False,
        patching_layer = None,
        name=''):   


        super(SpiralInductor, self).__init__(name)
        do = float(exterior)
        n = coil_number
        self.do = do
        self.n = n
        self.line_width = line_width
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
        self.length = length_path(points)

      # ##################
      # # Base layer
      # ##################


        overlap_square_base = cad.shapes.Rectangle((do/2.-overlap_square_width/2.,-do/2.-overlap_square_width/2.),\
         (do/2.+overlap_square_width/2.,-do/2.+overlap_square_width/2.), layer = base_layer)

        overlap_square_top = cad.shapes.Rectangle((do/2.-overlap_square_width/2.-1,-do/2.-overlap_square_width/2.-1),\
         (do/2.+overlap_square_width/2.+1,-do/2.+overlap_square_width/2.+1), layer = top_layer)

        if patch:
            self.add(cad.shapes.Rectangle((do/2.-overlap_square_width/2.,-do/2.-overlap_square_width/2.),\
         (do/2.+overlap_square_width/2.,-do/2.+overlap_square_width/2.), layer = patching_layer))

        tail = cad.shapes.Rectangle((-tail_length,-do/2.+line_width/2.),\
         (do/2.,-do/2.-line_width/2.), layer = base_layer)

        self.length += do/2.+tail_length

      # ##################
      # # Sacrificial layer
      # ##################

        sacrificial = cad.shapes.Rectangle((-tail_length,-do/2.+bridge_width/2.),\
         (do/2.,-do/2.-bridge_width/2.), layer = sacrificial_layer)



        self.add([spiral,overlap_square_base, overlap_square_top,tail,sacrificial])

        k1 = 2.34
        k2 = 2.75
        rho = (self.do-self.di)/(self.do+self.di)
        da = 0.5*(self.do+self.di)
        mu_0 = 4.*np.pi*1.e-7
        self.Lg = k1*mu_0*float(self.n)**2*da*1.e-6/(1+k2*rho)
        if line_width == 0.25 and spacing == 0.25:
            self.C = self.do*6.7e-15/40.
        elif line_width == 0.5 and spacing == 1.: 
            self.C = self.do*42.4e-15/130.
        elif line_width == 0.5 and spacing == 0.5: 
            self.C = self.do*22.5e-15/67.
        else:
            self.C = 1.
            print 'No formula for C'
        self.Lk = self.length/self.line_width*kinetic_inductance
        self.self_resonance = 1./np.sqrt((self.Lk+self.Lg)*self.C)/2./np.pi

    def resonance(self, C):

        return 1./np.sqrt((self.Lk+self.Lg)*(self.C+C))/2./np.pi
        
class SpiralProbe(cad.core.Cell):
    """docstring for SpiralProbe"""
    def __init__(self, 
        exterior = 55.,
        coil_number = 45,
        line_width = 0.25,
        spacing = 0.25,
        bridge_width = 2.,
        overlap_square_width = 3.,
        tail_length = 10.,
        base_layer = 1,
        sacrificial_layer = 2,
        top_layer = 3,
        kinetic_inductance = 0.,
        patch = False,
        patching_layer = None,
        taper_start_width = 100, 
        taper_length = 100, 
        name = ""):
        super(SpiralProbe, self).__init__(name)
        self.name = name


        self.add(probe_pad(
            [0,0], 
            orientation = 'right', 
            layer = top_layer,
            taper_start_width = taper_start_width, 
            taper_end_width = line_width, 
            taper_length = taper_length, 
            line_length = line_width))
        self.add(probe_pad(
            [exterior+tail_length,0], 
            orientation = 'left', 
            layer = top_layer,
            taper_start_width = taper_start_width, 
            taper_end_width = line_width, 
            taper_length = taper_length, 
            line_length = line_width))
        self.add(SpiralInductor(  
            exterior,
            coil_number,
            line_width ,
            spacing,
            bridge_width,
            overlap_square_width,
            tail_length,
            base_layer ,
            sacrificial_layer,
            top_layer,
            kinetic_inductance,
            patch ,
            patching_layer ,
            name=name+'_spiral'))

        # connect spiral with left probe
        points = [[exterior+tail_length,0]]
        points = increment(points,0,-(exterior+tail_length))
        points = increment(points,-(exterior+2.*tail_length),0.)
        points = increment(points,0,(exterior/2.+tail_length))
        self.add(MeanderingLine(
            points = points,
            turn_radius = line_width,
            line_width = line_width,
            layer = top_layer,
            path = True,
            name = name+"_m1"))

        do = float(exterior)
        overlap_square_base = cad.shapes.Rectangle((-tail_length-overlap_square_width/2.,-do/2.-overlap_square_width/2.),\
         (-tail_length+overlap_square_width/2.,-do/2.+overlap_square_width/2.), layer = base_layer)
        self.add(overlap_square_base)
        overlap_square_width+=1
        overlap_square_top = cad.shapes.Rectangle((-tail_length-overlap_square_width/2.,-do/2.-overlap_square_width/2.),\
         (-tail_length+overlap_square_width/2.,-do/2.+overlap_square_width/2.), layer = top_layer)
        self.add(overlap_square_top)




       
        

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



class MeanderingInductor(MeanderingLine):
    """docstring for MeanderingLine"""


    def __init__(self, n_legs, cond_width, cond_spacing, length, bend_radius,layer,name = ""):


        self.n_legs = n_legs
        self.cond_width = cond_width
        self.cond_spacing = cond_spacing
        self.length = length
        self.bend_radius = bend_radius
        pitch = cond_spacing+cond_width

        if n_legs%2==1:
            print "Meandering inductors with odd number of legs not yet implemented"
            return

        meander = []
        for i in range(int(n_legs)/2):
            i*=2.
            meander.append([0,-i*pitch])
            meander.append([length,-i*pitch])
            meander.append([length,-i*pitch-pitch])
            meander.append([0,-i*pitch-pitch])

        
        super(MeanderingInductor, self).__init__(
        points = meander,
        turn_radius = bend_radius,
        line_width = cond_width,
        layer = layer,
        path = True,
        name=name)



class MeanderAndDrum(cad.core.Cell):
    """docstring for MeanderAndDrum"""
    def __init__(self, base_layer = 1,
        sacrificial_layer = 2 ,
        top_layer = 3,
        hole_layer = 4,
        outer_radius = 9,
        head_radius = 7,
        electrode_radius = 6,
        cable_width = 0.5,
        sacrificial_tail_width = 3,
        opening_width = 4,
        N_holes = 3,
        hole_angle = 45,
        hole_distance_to_center = 4.5,
        hole_distance_to_edge = 0.5,
        split_electrode = False,
        electrode_splitting = 1.,
        n_legs = 20, 
        cond_spacing = 10., 
        meander_length = 300., 
        bend_radius = 1.,
        meander_to_ground = 200.,
        overlap_square = 20.,
        label = None,
        name = ""):
        super(MeanderAndDrum, self).__init__(name)
        meander = MeanderingInductor(n_legs, cable_width, cond_spacing, meander_length, bend_radius,top_layer, name = name+"_m1")
        drum = Drum(base_layer,sacrificial_layer  ,top_layer ,hole_layer ,outer_radius,head_radius ,electrode_radius ,
            cable_width ,sacrificial_tail_width ,meander_to_ground/2.-head_radius -overlap_square/4.,opening_width ,
            N_holes,hole_angle ,hole_distance_to_center,hole_distance_to_edge ,split_electrode ,electrode_splitting , right_sacrificial_tail = 5., name=name+"_drum")

        self.add(cad.core.CellReference(meander,origin=(meander_to_ground,0)))
        self.add(cad.core.CellReference(drum,origin=(meander_to_ground/2.,-outer_radius-overlap_square/2.)))
        ground_rectangle = [[-overlap_square/2.,-overlap_square/2.-outer_radius-overlap_square/2.],[+overlap_square/2.,+overlap_square/2.-outer_radius-overlap_square/2.]]
        self.add(cad.shapes.Rectangle(ground_rectangle[0],ground_rectangle[1],layer = base_layer))
        self.add(cad.shapes.Rectangle(ground_rectangle[0],ground_rectangle[1],layer = top_layer))

        # connect ground to drum
        self.add(MeanderingLine(
            points = [[meander_to_ground/2.,-outer_radius-overlap_square/2.+head_radius],[meander_to_ground/2.,0],[meander_to_ground,0]],
            turn_radius = bend_radius,
            line_width = cable_width,
            layer = top_layer,
            path = False,
            name = name+"_m2"))
        self.add(MeanderingLine(
            points = [[0,-outer_radius-overlap_square/2.],[meander_to_ground/2.,-outer_radius-overlap_square/2.]],
            turn_radius = bend_radius,
            line_width = cable_width,
            layer = base_layer,
            path = False,
            name = name+"_m3"))
        # Connect inductor to ground
        self.vertical_length = (n_legs-1)*(cond_spacing + cable_width)
        self.add(MeanderingLine(
            points = [[0,-self.vertical_length],[meander_to_ground,-self.vertical_length]],
            turn_radius = bend_radius,
            line_width = cable_width,
            layer = top_layer,
            path = False,
            name = name+"_m4"))
        if label !=None:
            self.add(cad.shapes.Label(label, 20, [meander_to_ground/2.,30.], layer=base_layer))