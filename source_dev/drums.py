import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad
# import shapely as sh
# import shapely.ops as op
# import os, inspect
# current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

class SuspendedDrum(cad.core.Cell):

    # Parent class for all drum types. Returns a suspended drum 'Boundary' with given size, gap, tether width, 

    def __init__(self, drum_size, drum_gap, tether_width,
        name='', layer = 3):
        super(SuspendedDrum, self).__init__(name)
        self.layer = layer
        self._objects=[]
        self._bounding_box = None

        self.drum_size = drum_size
        self.drum_gap = drum_gap
        self.tether_width = tether_width

        self.delta = (1/np.sqrt(2))*tether_width
        self.alpha = (1/np.sqrt(2))*(drum_size-2*self.delta)
        self.gamma = (1/np.sqrt(2))*self.alpha
        
        self.top_width = self.drum_size-2*self.delta
        self.bottom_width = self.top_width+2*self.drum_gap
        self.height = self.drum_gap
        self.drumhead_radius = self.drum_size

    def add_release_holes(self,release_holes_diameter,release_holes_pitch,release_holes_area_radius):
        rh_range_half_width = release_holes_area_radius-release_holes_pitch-release_holes_diameter/2
        incr = release_holes_pitch+release_holes_diameter
        rh_range_y = np.arange(0,rh_range_half_width,incr*np.sqrt(3)/2)
        rh_range_even = np.arange(0,rh_range_half_width,incr)
        rh_range_odd = np.arange(incr/2,rh_range_half_width,incr)
        for i,y in list(enumerate(rh_range_y))+list(enumerate(-rh_range_y)):
            if i%2 ==0:
                r = rh_range_even
            else:
                r = rh_range_odd
            for x in list(r)+list(-r):
                if (x**2+y**2)<rh_range_half_width**2:
                    self.add(cad.shapes.Disk([x,y],release_holes_diameter/2,layer = self.layer))
        
    def get_details(self):
        return "drum_size = %s, drum_gap = %s, tether_width =  %s." % (self.drum_size, self.drum_gap, self.tether_width)

    def bounding_box(self):
        # Return the smallest rectangle enclosing the drum.
        bb = np.zeros([2,2])
        # if self._bounding_box is not None:
        #     return self._bounding_box.copy()
        for i in range(len(self._objects)):
            if i == 0:
                bb[0,0] = self._objects[i]._points[:,0].min()
                bb[0,1] = self._objects[i]._points[:,1].min()
                bb[1,0] = self._objects[i]._points[:,0].max()
                bb[1,1] = self._objects[i]._points[:,1].max()
            else:
                bb[0,0] = min(self._objects[i]._points[:,0].min(), bb[0,0])
                bb[0,1] = min(self._objects[i]._points[:,1].min(), bb[0,1])
                bb[1,0] = max(self._objects[i]._points[:,0].max(), bb[1,0])
                bb[1,1] = max(self._objects[i]._points[:,1].max(), bb[1,1])

        self._bounding_box = bb
        return bb

    def translate(self, position):
        # Translates the center of the drum from its original position (0,0) by the vector 'position'
        
        for i in range(len(self._objects)):
            self._objects[i].points = cad.utils.translate(self._objects[i].points, position)
        self.bounding_box()

    def add_to_chip(self, Base_Chip):
        Base_Chip.add(self._objects)

    def add_labl(self, position = (0,0), array_indicator = None):
        if self.name != '':
            if array_indicator != None:
                self.name += array_indicator
            label = cad.shapes.Label(text = self.name, size=3, position = position, horizontal=True, angle=0, datatype=None,layer = self.layer)
            for i in range(len(label)):
                self.add(cad.core.Boundary(label[i].points, layer = self.layer))
            self.bounding_box()


class simple_drum(SuspendedDrum): #Drum with 4 tethers, no rounded corners.
    def __init__(self, drum_size, drum_gap, tether_width,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "
        trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer = self.layer)
        trap1 = cad.utils.translate(trap0, [0,-(self.drum_gap+self.drum_size/2)])
        trap2 = cad.utils.rotate(trap1, 90, center=(0,0))
        trap3 = cad.utils.rotate(trap1, 180, center=(0,0))
        trap4 = cad.utils.rotate(trap1, 270, center=(0,0))

        self.add(trap1)
        self.add(trap2)
        self.add(trap3)
        self.add(trap4)

        self.bounding_box()

    def get_details(self):
        return "drum_size = %s, drum_gap = %s, tether_width =  %s." % (self.drum_size, self.drum_gap, self.tether_width)

    
class rounded_drum(SuspendedDrum): #Drum with 4 tethers, rounded corners. Gaps are created by joining a trapezoid to a partial disk.
    def __init__(self, drum_size, drum_gap, tether_width,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "

        trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height,layer = self.layer)

        disk_offset = drum_gap-self.gamma
        disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=45,final_angle=135,layer = self.layer)

        gap0 = join_polygons(disk0, trap0, format_shapely=False)

        gap1 = cad.utils.translate(gap0, [0,-(drum_gap+drum_size/2)])
        gap2 = cad.utils.rotate(gap1, 90, center=(0,0))
        gap3 = cad.utils.rotate(gap1, 180, center=(0,0))
        gap4 = cad.utils.rotate(gap1, 270, center=(0,0))

        self.add(gap1)
        self.add(gap2)
        self.add(gap3)
        self.add(gap4)

        self.bounding_box()


class simple_drum3(SuspendedDrum): #Drum with 3 tethers, no rounding of corners.
    def __init__(self, drum_size, drum_gap, tether_width,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "
        self.detla = tether_width/(np.sin(np.deg2rad(30)))
        
        self.top_width = self.drum_size-2*self.delta
        self.bottom_width = 2*(np.tan(np.deg2rad(60))*drum_gap)+self.top_width
        self.height = drum_gap

        trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height,layer = self.layer)

        trap1 = cad.utils.translate(trap0, [0,-(drum_gap+0.5*np.tan(np.deg2rad(30))*drum_size)])
        trap2 = cad.utils.rotate(trap1, 120, center = (0,0))
        trap3 = cad.utils.rotate(trap1, 240, center = (0,0))
        self.add(trap1)
        self.add(trap2)
        self.add(trap3)

        self.bounding_box()

class rounded_base_drum3(SuspendedDrum): #Drum with 3 tethers, rounded corners. Gaps are made by joining a trapezoid and a partial disk. At the interface between the partical disk and the trapezoid the radius of the disk is such that the connection to the trapezoid is smooth (no corner). The corners at the base of the trapezoid are rounded using the function round_corner.
    def __init__(self, drum_size, drum_gap, tether_width, corner_rad, nr_of_points,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "


        self.corner_rad = corner_rad
        self.nr_of_points = nr_of_points

        self.delta = tether_width/(np.sin(np.deg2rad(30)))
        
        self.top_width = self.drum_size-2*self.delta
        self.bottom_width = 2*(np.tan(np.deg2rad(60))*drum_gap)+self.top_width
        self.height = drum_gap

        trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height,layer = self.layer)

        # corner_rad = .90

        self.alpha = 0.5*self.top_width/(np.sin(np.deg2rad(30)))
        self.gamma = 0.5*self.top_width/(np.tan(np.deg2rad(30)))

        disk_offset = self.drum_gap-self.gamma
        disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=60,final_angle=120,layer = self.layer)
        gap0 = join_polygons(disk0, trap0, format_shapely=False)
    
        gap0_rounded_points = round_corner(gap0.points,[gap0.points.shape[0]-3,gap0.points.shape[0]-2], 
            corner_rad=corner_rad,nr_of_points=self.nr_of_points, layer = self.layer) # Point list now starts at first point of the disk!

        gap0_rounded = cad.core.Boundary(gap0_rounded_points)

        gap1 = cad.utils.translate(gap0_rounded, [0,-(drum_gap+0.5*np.tan(np.deg2rad(30))*drum_size)])
        gap2 = cad.utils.rotate(gap1, 120, center = (0,0))
        gap3 = cad.utils.rotate(gap1, 240, center = (0,0))

        self.add(gap1)
        self.add(gap2)
        self.add(gap3)

        self.bounding_box()
        self.total_radius = drum_size/2

class rounded_base_drum4(SuspendedDrum): #Drum with 4 tethers, rounded corners. Gaps are made by joining a trapezoid and a partial disk. At the interface between the partical disk and the trapezoid the radius of the disk is such that the connection to the trapezoid is smooth (no corner). The corners at the base of the trapezoid are rounded using the function round_corner.
    def __init__(self, drum_size, drum_gap, tether_width, corner_rad, nr_of_points,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "
        self.corner_rad = corner_rad
        self.nr_of_points = nr_of_points
        trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height,layer = self.layer)

        corner_rad = .90

        disk_offset = drum_gap-self.gamma
        disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=45,final_angle=135,layer = self.layer)
        gap0 = join_polygons(disk0, trap0, format_shapely=False)
    
        gap0_rounded_points = round_corner(gap0.points,[gap0.points.shape[0]-3,gap0.points.shape[0]-2], 
            corner_rad=corner_rad,nr_of_points=self.nr_of_points, layer = self.layer) # Point list now starts at first point of the disk!

        gap0_rounded = cad.core.Boundary(gap0_rounded_points)


        gap1 = cad.utils.translate(gap0_rounded, [0,-(drum_gap+drum_size/2)])
        gap2 = cad.utils.rotate(gap1, 90, center=(0,0))
        gap3 = cad.utils.rotate(gap1, 180, center=(0,0))
        gap4 = cad.utils.rotate(gap1, 270, center=(0,0))

        self.add(gap1)
        self.add(gap2)
        self.add(gap3)
        self.add(gap4)

        self.bounding_box()
        self.total_radius =  np.sqrt(self._bounding_box[1][1]**2+self._bounding_box[1][0]**2)
        self.drumhead_radius = np.amin(gap3.points[:,1])

class rounded_base_drum5(SuspendedDrum): 
    '''
    Drum with 5 tethers, rounded corners. Holes are made by joining a trapezoid and a partial disk.
     At the interface between the partical disk and the trapezoid the radius of the disk is such that the 
     connection to the trapezoid is smooth (no corner). The corners at the base of the trapezoid are 
     rounded using the function round_corner.
     '''
    def __init__(self, drum_size, drum_gap, tether_width, corner_rad, nr_of_points,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "


        self.corner_rad = corner_rad
        self.nr_of_points = nr_of_points

        self.delta = tether_width/(np.sin(np.deg2rad(54)))
        
        self.top_width = self.drum_size-2*self.delta
        self.bottom_width = 2*(np.tan(np.deg2rad(36))*drum_gap)+self.top_width
        self.height = drum_gap

        trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height,layer = self.layer)

        corner_rad = .90

        self.alpha = 0.5*self.top_width/(np.sin(np.deg2rad(54)))
        self.gamma = 0.5*self.top_width/(np.tan(np.deg2rad(54)))

        disk_offset = self.drum_gap-self.gamma
        disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=36,final_angle=144,layer = self.layer)
        gap0 = join_polygons(disk0, trap0, format_shapely=False)
    
        gap0_rounded_points = round_corner(gap0.points,[gap0.points.shape[0]-3,gap0.points.shape[0]-2], 
            corner_rad=corner_rad,nr_of_points=self.nr_of_points, layer = self.layer) # Point list now starts at first point of the disk!

        gap0_rounded = cad.core.Boundary(gap0_rounded_points)

        gap1 = cad.utils.translate(gap0_rounded, [0,-(drum_gap+0.5*np.tan(np.deg2rad(54))*drum_size)])
        gap2 = cad.utils.rotate(gap1, 72, center = (0,0))
        gap3 = cad.utils.rotate(gap1, 144, center = (0,0))
        gap4 = cad.utils.rotate(gap1, 216, center = (0,0))
        gap5 = cad.utils.rotate(gap1, 288, center = (0,0))

        self.add(gap1)
        self.add(gap2)
        self.add(gap3)
        self.add(gap4)
        self.add(gap5)

        self.bounding_box()
        self.total_radius = self._bounding_box[1][1]
        self.drumhead_radius = -np.amax(gap1.points[:,1])


class simple_drum2(SuspendedDrum): # Rectangular drum with 2 tethers. no rounded corners.
    def __init__(self, drum_size, drum_length, drum_gap, tether_width, tether_length,name='', layer = 3):
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "
        self.points = [[-(0.5*drum_length + tether_length),0],[-(0.5*drum_length + tether_length),drum_gap+0.5*(drum_size-tether_width)],[-(0.5*drum_length),drum_gap+0.5*(drum_size-tether_width)],[-(0.5*drum_length),drum_gap],[(0.5*drum_length),drum_gap],[(0.5*drum_length),drum_gap+0.5*(drum_size-tether_width)],[(0.5*drum_length + tether_length),drum_gap+0.5*(drum_size-tether_width)],[(0.5*drum_length + tether_length),0],[-(0.5*drum_length + tether_length),0]]
        gap0 = cad.core.Boundary(self.points)
        gap1 = cad.utils.translate(gap0,[0,-(0.5*(drum_size+tether_width)+drum_gap)])
        gap2 = cad.utils.rotate(gap1, 180, center=(0,0))

        self.add(gap1)
        self.add(gap2)

        self.bounding_box()
        self.total_radius = self._bounding_box[1][1]
        

class circular_drum2(SuspendedDrum): # Circular drum with 2 tethers, no rounded corners.
    def __init__(self, drum_size, drum_gap, tether_width,name='', layer = 3):
        self.name = f"{tether_width}, {drum_gap}, {drum_size} "
        SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width, name, layer)

        disk0 = cad.shapes.Disk((0,0),radius=drum_size/2+drum_gap, inner_radius=drum_size/2, initial_angle=0, final_angle=180, number_of_points=199,layer = self.layer)
        disk1 = cad.utils.translate(disk0,[0,tether_width])
        disk2 = cad.utils.rotate(disk1, 180, center=(0,0))

        self.add(disk1)
        self.add(disk2)

        self.bounding_box()
        self.total_radius = self._bounding_box[1][1]

class circ_gap_drum(SuspendedDrum): # Drums created by making gaps out of Disk shapes centered along a circle with radius depending on drum_size, tether_width, and number_of_tethers. 
    def __init__(self,drum_size, tether_width, number_of_tethers,name='', layer = 3):
        
        

        self.number_of_tethers = number_of_tethers

        alpha = 360/(self.number_of_tethers)
        self.gap_radius = (tether_width/2 - np.sin(np.deg2rad(alpha/2))*drum_size)/(np.sin(np.deg2rad(alpha/2))-1)
        self.name = f"{tether_width}, {round(2*self.gap_radius,1)}, {drum_size} "
        SuspendedDrum.__init__(self, drum_size, 2*self.gap_radius, tether_width)
        print(self.gap_radius)
        size = drum_size + self.gap_radius
        points = []
        i=0
        while i < number_of_tethers:
            new_point = [np.cos(np.deg2rad(i*alpha))*size,np.sin(np.deg2rad(i*alpha))*size]
            gap = cad.shapes.Disk(center = new_point, radius = self.gap_radius,layer = self.layer)
            self.add(gap)
            if i == 0:
                points = [new_point]
            else:
                points = np.vstack([points, new_point])
            i += 1
        print(points)

        self.total_radius = drum_size + self.gap_radius*2
        self._references = []
        self.bounding_box()



def round_corner(arr, points, corner_rad, nr_of_points,layer):
    # Takes a point from a point list and replaces it by a series of points that create a partial circle connected to the points above and below on the list.
    corners = arr
    # print("Points: ",points)
    amnt_points = arr.shape[0]
    # print("amnt_points",amnt_points)
    corners_temp = corners
    for i in range(len(points)):
        if points[i] > amnt_points:
            print("There is no point with number ",points[i])
        point_nr = points[i]+i*(nr_of_points-1) #Points will be pushed down by those added with the circle
        point = corners_temp[point_nr,:]
        # print("point: ", point)
        if point_nr == amnt_points-1:    #Find vector between the last point on the list and the first point.
            vec1 = corners_temp[0,:] - point
            # print("vec1_A = ", vec1)
        else:
            vec1 = corners_temp[point_nr+1,:] - point
            # print("vec1_B = ", vec1)
        if point_nr == 0:
            vec2 = corners_temp[amnt_points-2,:] - point
        else:
            vec2 = corners_temp[point_nr-1,:] - point
        angle1 = angle(vec1)
        angle2 = angle(vec2)
        angle_delta = angle1 - angle2

        length1 = np.sqrt(vec1.dot(vec1))
        length2 = np.sqrt(vec2.dot(vec2))

        if corner_rad > length1 or corner_rad > length2:
            print("Corner_rad too large")
        
        circ_delta = corner_rad/(np.sin(np.deg2rad(angle_delta/2)))
        corner_center_point = (point[0]+circ_delta*np.cos(np.deg2rad(angle2 + angle_delta/2)), point[1] + circ_delta*np.sin(np.deg2rad(angle2 + angle_delta/2)))

        vec3 = corner_center_point - point
        angle3 = angle(vec3)

        proj3_1 = ((vec3.dot(vec1))/(length1**2))*vec1
        vec4 = proj3_1-vec3
        angle4 = angle(vec4)

        proj3_2 = ((vec3.dot(vec2))/(length2**2))*vec2
        vec5 = proj3_2-vec3
        angle5 = angle(vec5)

        if angle4 > angle5:
            angle4 -= 360

        circ_init_angle = angle5 #ensure initial angle is always larger than final angle in case angle() gives a negative value. Partial circle is then drawn in correct direction (clockwise).
        circ_fin_angle = angle4
        
        # print("vec2 = ", vec2)
        # print("corner_center_point = ",corner_center_point)
        # print("vec3 = ", vec3)
        # print("vec4 = ", vec4)
        # print("vec5 = ", vec5)
        # print("corner_rad = ",corner_rad)
        # print("angle5 = ", angle5)
        # print("angle4 = ", angle4)
        circ=cad.shapes.Circle(corner_center_point, corner_rad, 0,initial_angle=circ_init_angle, final_angle=circ_fin_angle, number_of_points=20,layer = layer, datatype=None)

        corners_temp = np.delete(corners_temp,point_nr,0)
        corners_temp = np.insert(corners_temp,point_nr, circ.points, axis=0)

        # Close the loop again if the start/end point was rounded
        if point_nr == 0:
            new_amnt_points = corners_temp.shape[0]
            end_point = corners_temp[0,:]
            corners_temp = np.delete(corners_temp, new_amnt_points-1,0)
            corners_temp = np.vstack([corners_temp, end_point])
    return corners_temp;

class Array(cad.core.Layout): # Parent class for all drum array types.
    def __init__(self, label_separation=30, separation=30, sub_array_separation = 60, array_indicator=None, name='', layer = 3):
        super(Array, self).__init__(name=name)
        self.label_separation = label_separation
        self.separation = separation
        self.sub_array_separation = sub_array_separation
        if array_indicator != None:
            self.array_indicator = array_indicator

    def add_to_chip(self, Base_Chip):
        for i in range(len(self.get_dependencies())):
            Base_Chip.add(self.get_dependencies()[i]._objects)

    def translate(self, position):
        for i in range(len(self.get_dependencies())):
            self.get_dependencies()[i].translate(position)
        self.bounding_box()

    def bounding_box(self):
        # Return the smallest rectangle enclosing the drum.
        bb = np.zeros([2,2])
        # if self._bounding_box is not None:
        #     return self._bounding_box.copy()
        for i in range(len(self.get_dependencies())):
            if i == 0:
                bb[0,0] = self.get_dependencies()[i]._bounding_box[0,0]
                bb[0,1] = self.get_dependencies()[i]._bounding_box[0,1]
                bb[1,0] = self.get_dependencies()[i]._bounding_box[1,0]
                bb[1,1] = self.get_dependencies()[i]._bounding_box[1,1]
            else:
                bb[0,0] = min(self.get_dependencies()[i]._bounding_box[0,0], bb[0,0])
                bb[0,1] = min(self.get_dependencies()[i]._bounding_box[0,1], bb[0,1])
                bb[1,0] = max(self.get_dependencies()[i]._bounding_box[1,0], bb[1,0])
                bb[1,1] = max(self.get_dependencies()[i]._bounding_box[1,1], bb[1,1])

        self._bounding_box = bb

    def add_labl(self, text = "SD4"): # not used.
        self.text = text
        label = cad.shapes.Label(text = self.text, size=200, position = (self._bounding_box[1,0]+50, self._bounding_box[1,1] - 200), horizontal=False, angle=0, layer=None, datatype=None)
        bb = np.zeros([2,2])
        container = cad.core.Cell(name=label)
        for i in range(len(label)):
            character_temp = cad.core.Boundary(label[i].points, layer=1)
            character_temp.name = f"{i}"
            container.add(character_temp)
            
            if i == 0:
                bb[0,0] = label[i].points[:,0].min()
                bb[0,1] = label[i].points[:,1].min()
                bb[1,0] = label[i].points[:,0].max()
                bb[1,1] = label[i].points[:,1].max()
            else:
                bb[0,0] = min(label[i].points[:,0].min(), bb[0,0])
                bb[0,1] = min(label[i].points[:,1].min(), bb[0,1])
                bb[1,0] = max(label[i].points[:,0].max(), bb[1,0])
                bb[1,1] = max(label[i].points[:,1].max(), bb[1,1])
        container._bounding_box = bb
        self.add(container)


        self.bounding_box()



class simple_drum_Array(Array): # Puts drums of type simple_drum with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None, name='', layer = 3):
        super(simple_drum_Array, self).__init__(name=name)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "

        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = simple_drum(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = simple_drum(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class rounded_drum_Array(Array): # Puts drums of type rounded_drum with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None, name = ''):
        Array.__init__(self)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(rounded_drum_Array, self).__init__(name=name)
        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = rounded_drum(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = rounded_drum(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class rounded_base_drum4_Array(Array): # Puts drums of type rounded_base_drum4 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, corner_rad = 1, nr_of_points = 20, array_indicator = None,name = ""):
        Array.__init__(self)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(rounded_base_drum4_Array, self).__init__(name=name)
        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = rounded_base_drum4(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=.5, corner_rad = 1, nr_of_points=20)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = rounded_base_drum4(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i],corner_rad = 1, nr_of_points = 20)
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class rounded_base_drum3_Array(Array): # Puts drums of type rounded_base_drum3 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, corner_rad = 1, nr_of_points = 20, array_indicator = None,name = ''):
        Array.__init__(self)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(rounded_base_drum3_Array, self).__init__(name=name)
        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = rounded_base_drum3(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=.5, corner_rad = 1, nr_of_points=20)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = rounded_base_drum3(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i],corner_rad = .5, nr_of_points = 20)
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class rounded_base_drum5_Array(Array): # Puts drums of type rounded_base_drum5 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, corner_rad = 1, nr_of_points = 20, array_indicator = None, name = ''):
        super(rounded_base_drum5_Array, self).__init__(name=name)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = rounded_base_drum5(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=.5, corner_rad = 1, nr_of_points=20)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = rounded_base_drum5(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i],corner_rad = 1, nr_of_points = 20)
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()


class simple_drum2_Array(Array): # Puts drums of type simple_drum2 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_length, drum_gaps, tether_widths, tether_length, array_indicator = None,name = ''):
        Array.__init__(self)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(simple_drum2_Array, self).__init__(name=name)

        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = simple_drum2(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5, drum_length=drum_length, tether_length=10)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = simple_drum2(drum_size=drum_sizes[k], drum_length=drum_length, drum_gap=drum_gaps[j], tether_width=tether_widths[i], tether_length=10)
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class simple_drum3_Array(Array): # Puts drums of type simple_drum3 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None,name='', layer = 3):
        Array.__init__(self)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(simple_drum3_Array, self).__init__(name=name)

        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = simple_drum3(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = simple_drum3(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class circular_drum2_Array(Array): # Puts drums of type circular_drum2 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None,name='', layer = 3):
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(circular_drum2_Array, self).__init__(name=name)
        max_drum_size = max(drum_sizes)
        max_drum_gap = max(drum_gaps)

        max_drum = circular_drum2(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


        for i in range(len(tether_widths)):
            for j in range(len(drum_gaps)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = circular_drum2(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
                    drum_temp.name = name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class circ_gap_drum_Array(Array): # Puts drums of type circ_gap_drum with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
    def __init__(self,drum_sizes = [5], tether_widths = [2], numbers_of_tethers = [3,4,5,6,7], array_indicator = None,name = '' ):
        Array.__init__(self)
        if array_indicator != None:
            self.array_indicator = array_indicator
        else:
            self.array_indicator = " "
        super(circ_gap_drum_Array, self).__init__(name=name)
        max_drum_size = max(drum_sizes)
        max_tether_width = max(tether_widths)
        max_nr_of_tethers = min(numbers_of_tethers)

        max_drum = circ_gap_drum(drum_size=max_drum_size, tether_width=max_tether_width, number_of_tethers=max_nr_of_tethers)
        max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

        bb = max_drum.bounding_box()
        max_width = abs(bb[0,0]-bb[1,0])
        max_height = abs(bb[0,1]-bb[1,1])
        sub_array_height = (max_height+self.sub_array_separation)*len(numbers_of_tethers)

        for i in range(len(numbers_of_tethers)):
            for j in range(len(tether_widths)):
                for k in range(len(drum_sizes)):
                    name = self.name+f"{i}.{j}.{k}"
                    drum_temp = circ_gap_drum(drum_size=drum_sizes[k],tether_width=tether_widths[j], number_of_tethers=numbers_of_tethers[i])
                    drum_temp.name=name


                    # print(drum_temp._objects)
                    drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
                    drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
                    # print(drum_temp._objects[:])
                    drum_temp._references = []
                    self.add(drum_temp)
        self.bounding_box()

class MyLabel(cad.core.Cell):
    def __init__(self, text,name = ''):
        super(MyLabel, self).__init__(name=name)

