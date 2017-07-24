import gdsCAD as cad
import shapely
import numpy as np
import collections



def make_rounded_edges(rectangle, radius, dict_corners):
	
	'''
	Rectangle: is a gdscad object (rectangle)
	layer : layer to place the object in
	list_corners: [BL,BR,TR,TL] order is important
	Note that the length of the corner list cannot exceed the corners
	of the object. If the length is smaller, the first n corners will be 
	rounded and smoothed
	This function returns an object with rounded corners
	'''

	original_layer = rectangle.layer
	corners = rectangle.bounding_box
	


	if (len(dict_corners) >(len(rectangle.points) - 1) ):
		raise ValueError('corner list is not equal to \
			number of corners')


	corner_coord = rectangle.points
	
	rectangle_shapely = poly_to_shapely(rectangle)
	rounded_rect = rectangle_shapely
	for key, value in dict_corners.iteritems():
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

def shapely_to_poly(shapely_Polygon):
	'''
	converts a shapely polygon to a gdsCAD Boundary.
	'''
	pol_type = shapely_Polygon.geom_type
	if pol_type != 'Polygon':
		raise ValueError('Shapely to Polygon > Input is not a polygon!')
	else:
		points = np.array(shapely_Polygon.exterior.coords.xy)
		reshaped_points = np.transpose(points)
		polygon = cad.core.Boundary(reshaped_points)

	return polygon

def poly_to_shapely(polygon):
	'''
	converts a polygon or Boundary to a shapely polygon
	'''
	points = polygon.points
	shapely_polygon = shapely.geometry.Polygon(points)

	return shapely_polygon

def join_polygons(polygon1,
                  polygon2,format_shapely=False):
    '''
    Inputs are:
        polygon1, polygon
        polygon2, polygon
    joining two polygons. Works better if there is overlap.
    Returns polygon = polygon1 U polygon2
    '''
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

def correct_for_multipol(pol):
    '''
    Inputs are:
        pol, Suspected Multipolygon
    Takes the main polygon of a multipolygon.
    Typically used to solve the problem of non-overlapping polygons being substracted.
    '''
    pol_type = pol.geom_type
    if pol_type == 'MultiPolygon':
        area = np.zeros(len(pol.geoms))
        for k, p in enumerate(pol.geoms):
            area[k] = p.area
        max_area_id = np.argmax(area)
        pol = pol.geoms[max_area_id]
    return pol


# width = 10
# height = 10

# pad = cad.shapes.Rectangle((0,0),(width,height))
# pad.layer=1

# # corner_coord = pad.points
# # d= np.flipud(corner_coord)

# # rot=0
# # rectangle_shapely = poly_to_shapely(pad)

# # mask_gdscad =mask_disk(0.7,layer=2).rotate(rot).translate(d[0]-0.0000001)

# # mask_shapely = poly_to_shapely(mask_gdscad)

# # rounded_rect = rectangle_shapely.difference(mask_shapely)

# # out = shapely_to_poly(rounded_rect)

# corners ={}
# corners['BL'] = 0
# corners['BR'] = 1
# corners['TR'] = 2
# corners['TL'] = 3
# # #
# out = make_rounded_edges(pad, radius=0.4,dict_corners=corners)#,'TL'])


# #
# cell.add(out)
# # cell.add(mask_gdscad)
# layout = cad.core.Layout('LIBRARY')
# layout.add(cell)
# layout.show()

# # print co.bounding_box
# ----------------------------------------------------------------------
# height = 0
# top_width = 5
# fork_height = height+ 20
# fork_depth = 2
# base_width = 20
# top_width = 10


# # box=shapes.Rectangle((-l,-l), (l,l), layer=2)
# # trapezoid = core.Boundary( [(-0.5*base_width,0),
# # 										(0.5*base_width,0),
# # 										(0.5*top_width,height),
# # 										(-0.5*top_width,height),
# # 										(-0.5*base_width,0)])
# fork = cad.core.Boundary([(-0.5*top_width,height),
# 							(0.5*top_width,height),
# 							(0.5*top_width,fork_height),
# 							(0.5*top_width - top_width/3.,fork_height),
# 							(0.5*top_width - top_width/3.,fork_height-fork_depth),
# 							(0.5*top_width - 2*top_width/3.,fork_height-fork_depth),
# 							(0.5*top_width - 2*top_width/3.,fork_height),
# 							(-0.5*top_width ,fork_height),
# 							(-0.5*top_width,0)])


# corners = collections.OrderedDict()
# corners['BLO'] = 0
# corners['BR1'] = 1
# corners['TR2'] = 2
# corners['TL3'] = 3
# corners['BR4O'] = 4
# corners['BL5O'] = 5
# corners['TR6'] = 6
# corners['TL7'] = 7

# print corners
# # #
# out = make_rounded_edges(fork, radius=0.3,dict_corners=corners)#,'TL'])
# out.points[0] = [-10,0]
# out.points[-1] = [-10,0]
# print out.points
# cell=cad.core.Cell('Tna')

# cell.add(out)
# # cell.add(mask_gdscad)
# layout = cad.core.Layout('LIBRARY')
# layout.add(cell)
# layout.show()

