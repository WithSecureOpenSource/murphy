'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Generic geometric helpers
'''
def move_rect(rect, point):
    '''
    Returns a new rect that is displaced the given x, y points
    '''
    return (rect[0] - point[0],
            rect[1] - point[1],
            rect[2] - point[0],
            rect[3] - point[1])
    

def expand_rect(rect, point):
    '''
    Returns a new rect that is x, y pixels bigger
    '''
    return (rect[0],
            rect[1],
            rect[2] + point[0],
            rect[3] + point[1])


def center_of_rect(rect):
    '''
    Returns a 2-tuple with the center point of the given rect
    '''
    center_x = rect[0] + ((rect[2] - rect[0]) / 2)
    center_y = rect[1] + ((rect[3] - rect[1]) / 2)
    return (center_x, center_y)
    
    
def point_inside_rects(coords, rects):
    '''
    Returns True if the given point is inside one of the rects, False otherwise
    '''
    if rects is None or len(rects) == 0:
        return False

    for rect in rects:
        if (coords[0] >= rect[0] and coords[0] <= rect[2] and
          coords[1] >= rect[1] and coords[1] <= rect[3]):
            return True

    return False


def is_rect_inside(rect1, rect2):
    '''
    Returns true if and only if rect1 is completely inside any of the rects in
    rect2 array
    '''
    if (point_inside_rects((rect1[0], rect1[1]), rect2) and
      point_inside_rects((rect1[0], rect1[3]), rect2) and
      point_inside_rects((rect1[2], rect1[1]), rect2) and
      point_inside_rects((rect1[2], rect1[3]), rect2)):
        return True
    else:
        return False
    
    
def rect_overlaps(rect1, rect2):
    '''
    Returns True if there's a point that is contained in both rects, False
    otherwise
    '''
    if (point_inside_rects((rect2[0], rect2[1]), [rect1]) or
      point_inside_rects((rect2[0], rect2[3]), [rect1]) or
      point_inside_rects((rect2[2], rect2[1]), [rect1]) or
      point_inside_rects((rect2[2], rect2[3]), [rect1]) or
      point_inside_rects((rect1[0], rect1[1]), [rect2]) or
      point_inside_rects((rect1[0], rect1[3]), [rect2]) or
      point_inside_rects((rect1[2], rect1[1]), [rect2]) or
      point_inside_rects((rect1[2], rect1[3]), [rect2])):
        return True
    
    rect1, rect2 = rect2, rect1
    if (point_inside_rects((rect2[0], rect2[1]), [rect1]) or
      point_inside_rects((rect2[0], rect2[3]), [rect1]) or
      point_inside_rects((rect2[2], rect2[1]), [rect1]) or
      point_inside_rects((rect2[2], rect2[3]), [rect1]) or
      point_inside_rects((rect1[0], rect1[1]), [rect2]) or
      point_inside_rects((rect1[0], rect1[3]), [rect2]) or
      point_inside_rects((rect1[2], rect1[1]), [rect2]) or
      point_inside_rects((rect1[2], rect1[3]), [rect2])):
        return True
        
    return False



def get_corner_points(rects, x_inset=0, y_inset=0):
    '''
    Returns a list of non-repeated points containing all the corners of the
    given rects, x_inset and y_inset can be specifed as to offset the point
    sligthliy inside the rect
    '''
    corners = []
    
    for coords in rects:
        candidates = [[coords[0] + x_inset, coords[1] + y_inset],
                      [coords[2] - x_inset, coords[1] + y_inset],
                      [coords[0] + x_inset, coords[3] - y_inset],
                      [coords[2] - x_inset, coords[3] - y_inset]]
        for candidate in candidates:
            if not (candidate[0], candidate[1]) in corners:
                corners.append((candidate[0], candidate[1]))
                
    return corners
    

def get_bounding_box(rects):
    '''
    Returns a rect that includes all given rects, rects must be a 4-touple
    array
    '''
    left, top, right, bottom = rects[0]
    for rect in rects[1:]:
        if rect[0] < left:
            left = rect[0]
        if rect[1] < top:
            top = rect[1]
        if rect[2] > right:
            right = rect[2]
        if rect[3] > bottom:
            bottom = rect[3]
            
    return (left, top, right, bottom)
    
    
def exclude_subareas(rects1, rects2):
    '''
    Removes the areas in rects1 that are contained in areas of rects2
    '''
    rects1 = rects1[:]
    for index in range(len(rects1)-1, -1, -1):
        area = rects1[index]
        if is_rect_inside(area, rects2):
            rects1.pop(index)
    return rects1
    
    
def merge_overlapping_areas(rects1, rects2):
    '''
    Returns an array of all the rects in rect1, any rect that overlaps with a
    rect in rects2 is adjusted as the bounding box of the overlap
    '''
    result = []
    for rect in rects1:
        this_rect = rect
        for rect2 in rects2:
            if rect_overlaps(rect, rect2): # or is_rect_inside(rect, [rect2]):
                this_rect = get_bounding_box([rect, rect2])
        result.append(this_rect)
    return result

    
def intersection(rect1, rect2):
    if rect_overlaps(rect1, rect2):
        if rect1[0] > rect2[0]:
            left = rect1[0]
        else:
            left = rect2[0]
        if rect1[1] > rect2[1]:
            top = rect1[1]
        else:
            top = rect2[1]
        if rect2[2] < rect1[2]:
            right = rect2[2]
        else:
            right = rect1[2]
        if rect2[3] < rect1[3]:
            bottom = rect2[3]
        else:
            bottom = rect1[3]

        return [left, top, right, bottom]
    else:
        return None