"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Some generic utilities without final destination yet, will be moved somewehere
else once major refactoring is done
"""
from model_extraction.image2 import Image2
from PIL import Image, ImageChops

import logging
from model_extraction.ui.utils import TASKBAR_HEIGHT
LOGGER = logging.getLogger('root.' + __name__)


def is_image_in_array(an_image, images):
    '''
    Searches if the given image is inside the given array, returns the position
    if it is found, -1 otherwise
    '''
    for j in range(len(images)):
        if an_image.test(images[j], 0, 0)[0]:
            return j
    return -1


def get_rect_by_low_pass_filter(image):
    grayscaled = image.convert("L")
    grayscaled.paste(0, (0, 0, image.size[0], 30))
    raw = grayscaled.tostring("raw")
    result = ""
    for r in raw:
        if ord(r) > 80:
            result += r
        else:
            result += chr(0)
    
    filtered = Image.fromstring("L", grayscaled.size, result, "raw")
    return filtered.getbbox()

    
def solve_active_window_rect(world, screen_image):
    '''
    Returns the enclosing rect of the active window, this is not the same as
    the direct call of GetWindowRect because in some cases, the window produces
    a shade around it, most of the time we want to ignore the shade area so
    the enclosing screenshot will not contain information of what is under it
    '''
    rect = world.machine.helper.get_active_window_rect()
    #FIXME: parametrize
    use_qt_refinement = True
    is_desktop = False
    if rect is None:
        LOGGER.info("No window rect at all, most likely privilege elevation "
                    "dialog")
        rect = get_rect_by_low_pass_filter(screen_image)
        is_desktop = 'Screen' 
    elif rect[0] < 0 or rect[1] < 0:
        if screen_image.size[0] + 16 == (rect[2] - rect[0]):
            #window is maximized
            LOGGER.debug("Maximized window (%s), taking desktop (%s)" % 
                                        (str(rect), str(screen_image.size)))
        else:
            LOGGER.debug("No valid window rect (%s), taking desktop (%s)" %
                                        (str(rect), str(screen_image.size)))
            is_desktop = True
        rect = (0, 0, screen_image.size[0],
                screen_image.size[1] - TASKBAR_HEIGHT)
    elif rect[3] == screen_image.size[1]:
        LOGGER.debug("Whole desktop, trimming taskbar")
        rect = (0, 0, screen_image.size[0],
                screen_image.size[1] - TASKBAR_HEIGHT)
        is_desktop = True
    elif use_qt_refinement:
        LOGGER.debug("Valid rect, trimming qt shade")
        rect = refine_window_rect(screen_image, rect)
    LOGGER.debug("Solved window rect is %s" % str(rect))
    return is_desktop, rect

    
def refine_window_rect(image, coords):
    '''
    Refines the window rect in the given image, it tries to remove any shade
    the window may produce returning the resulting rect.
    If it fails to detect any shade it will return the received rect so it is
    relatively safe to call it for windows without shade
    FIXME: the possible border colors are hardcoded, needs better
    parametrization
    '''
    coords = [coords[0], coords[1], coords[2], coords[3]]
    LOGGER.debug("Will refine for rect %s in image size %s" % (str(coords),
                                                              str(image.size)))
    #Wopsy, there are border cases at bottom of the screen
    #FIXME: check all boundaries and trim accordingly
    if coords[0] < 0:
        coords[0] = 1
    if coords[1] < 0:
        coords[1] = 1
    if coords[2] >= image.size[0]:
        coords[2] = image.size[0] -1
    if coords[3] >= image.size[1]:
        coords[3] = image.size[1] -1
        
    left_middle = coords[0] + ((coords[2] - coords[0])/2)
    top_middle = coords[1] + ((coords[3] - coords[1])/2)
    
    qt_border_colors = [(77, 77, 77), (79, 79, 79)]
    
    new_top, new_bottom = -1, -1
    for i in range(coords[1], coords[3], 1):
        pixel = image.getpixel((left_middle, i))
        if pixel in qt_border_colors:
            new_top = i
            break
    for i in range(coords[3], coords[1], -1):
        pixel = image.getpixel((left_middle, i))
        if pixel in qt_border_colors:
            new_bottom = i + 1
            break
    new_left, new_right = -1, -1
    for i in range(coords[0], coords[2], 1):
        pixel = image.getpixel((i, top_middle))
        if pixel in qt_border_colors:
            new_left = i
            break
    for i in range(coords[2], coords[0], -1):
        pixel = image.getpixel((i, top_middle))
        if pixel in qt_border_colors:
            new_right = i + 1
            break

    old_area = ((coords[2] - coords[0]) *
                (coords[3] - coords[1]))
    new_area = (new_right - new_left) * (new_bottom - new_top)
    #sanity check that trimming did not went nuts
    if -1 in [new_left, new_top, new_right, new_bottom]:
        LOGGER.debug("Ignoring trimming as the rect is invalid: %s" % str(
                     [new_left, new_top, new_right, new_bottom]))
    elif (old_area * 0.75) > new_area:
        LOGGER.debug(("Ignoring trimming, old area surface is %s new area "
                      "surface is %s") % (old_area, new_area))
    else:
        coords[0] = new_left
        coords[1] = new_top
        coords[2] = new_right
        coords[3] = new_bottom

    return coords

    
def find_vertical_division(image1, image2, bbox):
    diff = ImageChops.difference(image1.image, image2.image)
    
    empty_pixel = (0, 0, 0)
    division_right = -1
    division_left = -1
    candidate = None
    for x_coord in range(bbox[2], bbox[0] - 1, -1):
        line_is_white = True
        for y_coord in range(bbox[1], bbox[3] + 1): #borders are inclusive
            pixel = diff.getpixel((x_coord, y_coord))
            if pixel != empty_pixel:
                line_is_white = False
        if line_is_white:
            if division_right == -1:
                division_right = x_coord
                division_left = x_coord
            else:
                division_left = x_coord
            if candidate is None:
                candidate = (division_left, division_right)
            else:
                if candidate[1] - candidate[0] < division_right - division_left:
                    candidate = (division_left, division_right)
        else:
            division_left, division_right = -1, -1

    #it should be at least X pixels thick
    if candidate:
        if (candidate[1] - candidate[0] < 3 or
          candidate[0] == bbox[0] or
          candidate[1] == bbox[2]):
            return None
    return candidate
    
    
def find_horizontal_division(image1, image2, bbox):
    diff = ImageChops.difference(image1.image, image2.image)
    
    #division cannot start in the borders, otherwise is not really the bounding
    #box of the changes
    
    empty_pixel = (0, 0, 0)
    division_bottom = -1
    division_top = -1
    candidate = None
    for y_coord in range(bbox[3], bbox[1] - 1, -1):
        line_is_white = True
        for x_coord in range(bbox[0], bbox[2] + 1): #borders are inclusive
            pixel = diff.getpixel((x_coord, y_coord))
            if pixel != empty_pixel:
                line_is_white = False
        if line_is_white:
            if division_bottom == -1:
                division_bottom = y_coord
                division_top = y_coord
            else:
                division_top = y_coord
            if candidate is None:
                candidate = (division_top, division_bottom)
            else:
                if candidate[1] - candidate[0] < division_bottom - division_top:
                    candidate = (division_top, division_bottom)
        else:
            division_top, division_bottom = -1, -1

    #it should be at least X pixels thick
    if candidate:
        if (candidate[1] - candidate[0] < 3 or
          candidate[0] == bbox[1] or
          candidate[1] == bbox[3]):
            return None
            
    return candidate
    
    
def find_inner_bbox(image1, image2, bbox):
    '''
    Tries to separate the changes inside bbox, returns an array with either
    1 or 2 bboxes
    '''
    result = []
    division = find_vertical_division(image1, image2, bbox)
    if division:
        print "found vertical division as %s" % (str(division))
        a_box = [bbox[0], bbox[1], bbox[2]+1, bbox[3]+1]
        img1 = Image.new("RGB", image1.size)
        img1.paste(image1.image.crop(a_box), (bbox[0], bbox[1]))
        img2 = Image.new("RGB", image2.size)
        img2.paste(image2.image.crop(a_box), (bbox[0], bbox[1]))
        
        img3 = img1.copy()
        img3.paste((0, 0, 0), [division[1], 0, img1.size[0], img1.size[1]])
        img4 = img2.copy()
        img4.paste((0, 0, 0), [division[1], 0, img2.size[0], img2.size[1]])
        bbox1 = Image2(image=img3).difference(Image2(image=img4))
        if bbox1:
            result.append(bbox1)
            
        img3 = img1.copy()
        img3.paste((0, 0, 0), [0, 0, division[0] + 1, img1.size[1]])
        img4 = img2.copy()
        img4.paste((0, 0, 0), [0, 0, division[0] + 1, img2.size[1]])        
        bbox2 = Image2(image=img3).difference(Image2(image=img4))
        if bbox2:
            result.append(bbox2)
        
        if len(result) == 0:
            result.append(bbox)
            
        return result
        
    division = find_horizontal_division(image1, image2, bbox)
    if division:
        print "found horizontal division"
        a_box = [bbox[0], bbox[1], bbox[2]+1, bbox[3]+1]
        img1 = Image.new("RGB", image1.size)
        img1.paste(image1.image.crop(a_box), (bbox[0], bbox[1]))
        img2 = Image.new("RGB", image2.size)
        img2.paste(image2.image.crop(a_box), (bbox[0], bbox[1]))
        
        img3 = img1.copy()
        img3.paste((0, 0, 0), [0, division[1], img1.size[0], img1.size[1]])
        img4 = img2.copy()
        img4.paste((0, 0, 0), [0, division[1], img2.size[0], img2.size[1]])
        bbox1 = Image2(image=img3).difference(Image2(image=img4))
        if bbox1:
            result.append(bbox1)
            
        img3 = img1.copy()
        img3.paste((0, 0, 0), [0, 0, img1.size[0], division[0] + 1])
        img4 = img2.copy()
        img4.paste((0, 0, 0), [0, 0, img2.size[0], division[0] + 1])        
        bbox2 = Image2(image=img3).difference(Image2(image=img4))
        if bbox2:
            result.append(bbox2)
        
        if len(result) == 0:
            result.append(bbox)
            
        return result

    return [bbox]
    
    
def crop_border_differences_new(img1, img2):
    '''
    Given 2 images of same size, remove differences that can be found in their
    borders, this is an attempt to remove differences when comparing an active
    window against an inactive window whose title and borders are rendered
    differently due to the active / inactive state.
    '''
    diff = img1.difference(img2)
    crop_1 = img1.image.crop((diff[0], diff[1], diff[2] + 1, diff[3] + 1))
    crop_2 = img2.image.crop((diff[0], diff[1], diff[2] + 1, diff[3] + 1))
    diff_area = (diff[2] + 1 - diff[0]) * (diff[3] + 1 - diff[1])
    
    diff_image = ImageChops.difference(crop_1, crop_2)
    #diff_image.save("Diff.bmp")
    width, height = diff_image.size[0], diff_image.size[1]
    image_pixels = diff_image.convert('L').tostring('raw')
    
    left, right = find_continuous_hline(image_pixels, int(width * 0.2),
                                        int(height * 0.2), width)
    top, bottom = find_continuous_vline(image_pixels, int(width * 0.2),
                                        int(height * 0.2), width, height)
    candidate1 = (left + diff[0], top + diff[1],
                  right + diff[0], bottom + diff[1])
    area1 = (right - left) * (bottom - top)
    
    left, right = find_continuous_hline(image_pixels, int(width * 0.8),
                                        int(height * 0.8), width)
    top, bottom = find_continuous_vline(image_pixels, int(width * 0.8),
                                        int(height * 0.8), width, height)
    candidate2 = (left + diff[0], top + diff[1],
                  right + diff[0], bottom + diff[1])
    area2 = (right - left) * (bottom - top)
    
    #title bar could be used as a hint too, at least an estimate
    
    if area1 < diff_area and area1 >= area2:
        return candidate1
    elif area2 < diff_area and area2 >= area1:
        return candidate2
    else:
        return diff


def crop_border_differences(img1, img2):
    '''
    Given 2 images of same size, remove differences that can be found in their
    borders, this is an attempt to remove differences when comparing an active
    window against an inactive window whose title and borders are rendered
    differently due to the active / inactive state.
    '''
    diff = img1.difference(img2)
    #FIXME: diff may be None when the border does not change, the situation is unexpected and the error not understandable...
    crop_1 = img1.image.crop((diff[0], diff[1], diff[2] + 1, diff[3] + 1))
    crop_2 = img2.image.crop((diff[0], diff[1], diff[2] + 1, diff[3] + 1))
    diff_area = (diff[2] + 1 - diff[0]) * (diff[3] + 1 - diff[1])
    
    diff_image = ImageChops.difference(crop_1, crop_2)
    #diff_image.save("Diff.bmp")
    width, height = diff_image.size[0], diff_image.size[1]
    image_pixels = diff_image.convert('L').tostring('raw')
    
    x1, x2 = find_continuous_hline(image_pixels, int(width * 0.2), int(height * 0.2), width, height)
    y1, y2 = find_continuous_vline(image_pixels, int(width * 0.2), int(height * 0.2), width, height)
    candidate1 = (x1 + diff[0], y1 + diff[1], x2 + diff[0], y2 + diff[1])
    area1 = (x2 - x1) * (y2 - y1)
    
    x1, x2 = find_continuous_hline(image_pixels, int(width * 0.8), int(height * 0.8), width, height)
    y1, y2 = find_continuous_vline(image_pixels, int(width * 0.8), int(height * 0.8), width, height)
    candidate2 = (x1 + diff[0], y1 + diff[1], x2 + diff[0], y2 + diff[1])
    area2 = (x2 - x1) * (y2 - y1)
    
    #title bar could be used as a hint too, at least an estimate
    
    if area1 < diff_area and area1 >= area2:
        return candidate1
    elif area2 < diff_area and area2 >= area1:
        return candidate2
    else:
        return diff
    
def find_continuous_hline_new(image_pixels, x_pos, y_pos, width):
    '''
    Finds a horizontal line at the given point, the line is expected to be of
    the same color, it does so by scanning left and right from the given
    coordinates.
    Returns a tuple (x0, x1) where the line starts and ends, x1 is inclusive
    so x1 + 1 is of different color than x1
    Width and height are the image width and height, while image_pixels is a
    raw 1-dimension array with pixel colors 
    '''
    pos = x_pos + (y_pos * width)
    value = image_pixels[pos]
    x_starts, x_ends = pos, pos
    for x_current in range(pos - 1, pos - (pos % width) - 1, -1):
        if image_pixels[x_current] != value:
            x_starts = x_current + 1
            break
        
    for x_current in range(pos + 1, pos + (width - (pos % width))):
        if image_pixels[x_current] != value:
            x_starts = x_current - 1
            break
        
    return x_starts % width, x_ends % width


def find_continuous_vline_new(image_pixels, x_pos, y_pos, width, height):
    '''
    Finds a vertical line at the given point, the line is expected to be of the
    same color, it does so by scanning up and down from the given coordinates
    Returns a tuple (y0, y1) where the line starts and ends, y1 is inclusive
    so y1 + 1 is of different color than y1
    Width and height are the image width and height, while image_pixels is a
    raw 1-dimension array with pixel colors 
    '''
    pos = x_pos + (y_pos * width)
    value = image_pixels[pos]
    y_starts = pos
    for current_y in range(pos - width, 0, -width):
        if image_pixels[current_y] != value:
            y_starts = current_y + width
            break
        
    y_ends = pos
    for current_y in range(pos + width, width * height, width):
        if image_pixels[current_y] != value:
            y_ends = current_y - width
            break
        
    return y_starts / width, y_ends / width


def find_continuous_hline(image_pixels, x, y, width, height):
    pos = x + (y * width)
    value = image_pixels[pos]
    for i in range(pos - 1, pos - (pos % width) - 1, -1):
        if image_pixels[i] != value:
            i += 1
            break
    x1 = i
    for i in range(pos + 1, pos + (width - (pos % width))):
        if image_pixels[i] != value:
            i -= 1
            break
    x2 = i
    return x1 % width, x2 % width

def find_continuous_vline(image_pixels, x, y, width, height):
    pos = x + (y * width)
    value = image_pixels[pos]
    for i in range(pos - width, 0, -width):
        if image_pixels[i] != value:
            i += width
            break
    y1 = i
    for i in range(pos + width, width * height,width):
        if image_pixels[i] != value:
            i -= width
            break
    y2 = i
    return y1 / width, y2 / width


def test():
    '''
    Simple unit test
    '''
    img1 = Image2(file_name='self_test/img/active_window.bmp')
    img2 = Image2(file_name='self_test/img/inactive_window.bmp')
    diff = crop_border_differences(img1, img2)
    crop_1 = img1.image.crop((diff[0], diff[1], diff[2] + 1, diff[3] + 1))
    crop_1.save('crop1.bmp')
    crop_2 = img2.image.crop((diff[0], diff[1], diff[2] + 1, diff[3] + 1))
    crop_2.save('crop2.bmp')
        
if __name__ == '__main__':
    test()
    