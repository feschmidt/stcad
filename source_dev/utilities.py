import gdsCAD as cad
import shapely
from shapely import geometry
import numpy as np
import collections

def length_path(points):
	length=0
	for i in range(len(points)-1):
		length += np.sqrt((points[i+1][1]-points[i][1])**2+(points[i+1][0]-points[i][0])**2)
	return length

def shapely_to_poly(shapely_Polygon):
	"""
	converts a shapely polygon to a gdsCAD Boundary.
	"""
	pol_type = shapely_Polygon.geom_type
	if pol_type != 'Polygon':
		raise ValueError('Shapely to Polygon > Input is not a polygon!')
	else:
		points = np.array(shapely_Polygon.exterior.coords.xy)
		reshaped_points = np.transpose(points)
		polygon = cad.core.Boundary(reshaped_points)

	return polygon

def poly_to_shapely(polygon):
	"""
	converts a polygon or Boundary to a shapely polygon
	"""
	points = polygon.points
	shapely_polygon = shapely.geometry.Polygon(points)

	return shapely_polygon


def make_rounded_edges(rectangle, radius, dict_corners):
	
	"""
	Rectangle: is a gdscad object (rectangle)
	layer : layer to place the object in
	list_corners: [BL,BR,TR,TL] order is important
	Note that the length of the corner list cannot exceed the corners
	of the object. If the length is smaller, the first n corners will be 
	rounded and smoothed

	This function returns an object with rounded corners

	"""

	original_layer = rectangle.layer
	corners = rectangle.bounding_box
	


	if (len(dict_corners) >(len(rectangle.points) - 1) ):
		raise ValueError('corner list is not equal to \
			number of corners')


	corner_coord = rectangle.points
	
	rectangle_shapely = poly_to_shapely(rectangle)
	rounded_rect = rectangle_shapely
	for key, value in dict_corners.items():
		if key[:2] == 'BL':
			rot = 0
		elif key[:2] == 'BR':
			rot = 90
		elif key[:2] == 'TR':
			rot = 180
		elif key[:2] == 'TL':
			rot = 270

		else:
			raise NameError('invalid Corner')

		
		mask_gdscad =mask_disk(radius).rotate(rot).translate(corner_coord[value] )

		mask_shapely = poly_to_shapely(mask_gdscad)

		
		# O stands for open corner
		if key[-1] == 'O':
			rounded_rect = join_polygons(rounded_rect,mask_shapely,
										format_shapely = True)

		else:
			rounded_rect = rounded_rect.difference(mask_shapely)
		
		rounded_rect = correct_for_multipol(rounded_rect)

	out = shapely_to_poly(rounded_rect)
	out.layer = original_layer
	return out

def mask_disk(radius):

	circle = shapely.geometry.Point(0, 0).buffer(radius, resolution=64)
	polygon = shapely.geometry.Polygon(
		[(0, 0), (0, radius), (radius, radius), (radius, 0)])
	cutoff = polygon.difference(circle)
	quarter_disk = shapely_to_poly(cutoff)
	quarter_disk.rotate(180)
	quarter_disk.translate((radius, radius))

	return quarter_disk

def join_polygons(polygon1,polygon2,format_shapely=False):
    """
    Inputs are:
        polygon1, polygon
        polygon2, polygon
    joining two polygons. Works better if there is overlap.
    Returns polygon = polygon1 U polygon2
    """
    if format_shapely == False:
    	shapely_polygon1 = poly_to_shapely(polygon1)
    	shapely_polygon2 = poly_to_shapely(polygon2)
    	joined_poly = shapely_polygon1.union(shapely_polygon2)
    	out = shapely_to_poly(joined_poly)

    else:
    	shapely_polygon1 = polygon1
    	shapely_polygon2 = polygon2

    	joined_poly = shapely_polygon1.union(shapely_polygon2)
    	out = joined_poly


    return out

def buffer_polygon(polygon,amount):

	shapely_polygon = poly_to_shapely(polygon)
	return shapely_to_poly(shapely_polygon.buffer(amount))

def xor_polygons(polygon1,polygon2,format_shapely=False):
    """
    Inputs are:
        polygon1, polygon
        polygon2, polygon
    joining two polygons. Works better if there is overlap.
    Returns polygon = polygon1 U polygon2
    """
    if format_shapely == False:
    	shapely_polygon1 = poly_to_shapely(polygon1)
    	shapely_polygon2 = poly_to_shapely(polygon2)
    	xor_poly = shapely_polygon1.difference(shapely_polygon2)
    	out = shapely_to_poly(xor_poly)

    else:
    	shapely_polygon1 = polygon1
    	shapely_polygon2 = polygon2

    	xor_poly = shapely_polygon1.difference(shapely_polygon2)
    	out = xor_poly


    return out

def correct_for_multipol(pol):
    """
    Inputs are:
        pol, Suspected Multipolygon
    Takes the main polygon of a multipolygon.

    Typically used to solve the problem of non-overlapping polygons being substracted.

    """
    pol_type = pol.geom_type
    if pol_type == 'MultiPolygon':
        area = np.zeros(len(pol.geoms))
        for k, p in enumerate(pol.geoms):
            area[k] = p.area
        max_area_id = np.argmax(area)
        pol = pol.geoms[max_area_id]
    return pol


def angle(vec):
	return np.arctan2(vec[1],vec[0])

def line_polygon(start, end, line_width):
	e=np.array(end)
	s=np.array(start)
	ang = angle(e-s)
	vec = float(line_width)/2.*np.array([-np.sin(ang),np.cos(ang)])
	return cad.core.Boundary(np.array([start+vec,end+vec,end-vec,start-vec]))

def perpendicular_line(a,b,length,line_width):
	a=np.array(a)
	b=np.array(b)
	ang = angle(b-a)
	vec = float(length)*np.array([-np.sin(ang),np.cos(ang)])
	start = (b+a)/2
	end = start + vec
	return line_polygon(start, end, line_width)

def double_line_polygon(start, end, line_width,seperation):
	e=np.array(end)
	s=np.array(start)
	ang = angle(e-s)
	vec = np.array([-np.sin(ang),np.cos(ang)])
	line_1 = cad.core.Boundary(np.array([start+(seperation/2.+line_width)*vec,end+(seperation/2.+line_width)*vec,end+(seperation/2.)*vec,start+(seperation/2.)*vec]))
	line_2 = cad.core.Boundary(np.array([start-(seperation/2.+line_width)*vec,end-(seperation/2.+line_width)*vec,end-(seperation/2.)*vec,start-(seperation/2.)*vec]))
	
	return [line_1,line_2]

def arc_polygon(center,radius, line_width, final_angle = 0,initial_angle = 0, number_of_points = 199):

    if final_angle == initial_angle:
        final_angle += 360.0
        
    angles = np.linspace(initial_angle, final_angle, number_of_points).T * np.pi/180.

    points=np.vstack((np.cos(angles), np.sin(angles))).T * (radius+line_width/2.) + np.array(center)

    points2 = np.vstack((np.cos(angles), np.sin(angles))).T * (radius-line_width/2.) + np.array(center)
    points=np.vstack((points, points2[::-1]))
    
    return cad.core.Boundary(np.array(points))

def double_arc_polygon(center,radius, line_width,seperation, final_angle = 0,initial_angle = 0, number_of_points = 199):

    arc_1 = arc_polygon(center,radius-seperation/2.-line_width/2., line_width, final_angle,initial_angle, number_of_points)
    arc_2 = arc_polygon(center,radius+seperation/2.+line_width/2., line_width, final_angle,initial_angle, number_of_points)
    return [arc_1,arc_2]

def probe_pad(position, orientation,layer = 1, taper_start_width = 100, taper_end_width = 4, taper_length = 100, line_length = 20, line_width = None):
	if line_width == None:
		line_width = taper_end_width
	points = [[-line_width/2.,0],\
	[-line_width/2.,line_length],\
	[-taper_end_width/2.,line_length],\
	[-taper_start_width/2.,line_length+taper_length],\
	[taper_start_width/2.,line_length+taper_length],\
	[taper_end_width/2.,line_length],\
	[line_width/2.,line_length],\
	[line_width/2.,0]]
	shape = cad.core.Boundary(np.array(points),layer)

	if orientation == 'up':
		pass
	elif orientation == 'right':
		shape.rotate(90.)
	elif orientation == 'left':
		shape.rotate(-90.)
	elif orientation== 'down':
		shape.rotate(180.)
	else:
		ValueError("First argument should be either 'up', 'right', 'left' or 'down'")

	shape.translate(position)	

	return shape


def symmetric_trapezoid(bottom_width, top_width, height, layer=1):

    trapezoid = cad.core.Boundary(
        [(-0.5*bottom_width, 0),
         (-0.5*top_width, height),
         (0.5*top_width, height),
         (0.5*bottom_width, 0),
         (-0.5*bottom_width, 0),
         ], layer=layer)

    return trapezoid
if __name__ == '__main__':
 	probe_bad([20,20],'down').show()
