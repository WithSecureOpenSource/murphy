'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Utility class to scrap ui elements from windows

Encapsulates all the logic for collecting widgets / controls over the active
window, this implementation does it by analyzing the screen with keyboard,
mouse hovers, image searches and other ui techniques so it is broadly usable
as it is agnostic about the underlying development tool.

It is relatively simple to replace this class with a similar class that uses
instead low level automation calls if desired / needed, or even hibrid
approaches

As for this implementation there are some important concepts:
Some ui elements are detected without extra definitions, for example buttons
or other ui elements that are focusable and have ui hints when the mouse hovers
over them

Other elements like checkboxes and radio buttons are identified by providing
template images to recognize them

Others are recognized by searching a bounding box that contains them like links

VERY messy module that needs serious refactoring, also the interface for a
scraper class needs clear definition
'''
import os, logging, time

#from user_simulation.local_user import LocalUser

from model_extraction.image2 import Image2
from model_extraction.ui.ui_element import UIElement
from model_extraction import automation_helpers
from model_extraction.geometry import (point_inside_rects,
                                       get_corner_points, 
                                       get_bounding_box, 
                                       center_of_rect, 
                                       exclude_subareas, 
                                       merge_overlapping_areas, move_rect,
                                       is_rect_inside, expand_rect)

from model_extraction.ui.utils import TASKBAR_HEIGHT
from model_extraction.automation_helpers import solve_active_window_rect
LOGGER = logging.getLogger('root.' + __name__)


def send_tab_expecting_change(send_tab, grab_screen, current_screen):
    '''
    Sends a tab key to change control focus, wait few seconds for any ui
    change to synchronize it, will give up after 5 seconds (because sometimes
    focus is not properly handled in applications)
    Returns an Image2 of the new screen
    '''
    send_tab()
    for _ in range(5):
        new_screen = Image2(grab_screen())
        if new_screen != current_screen:
            break
        time.sleep(1)

    return new_screen

def get_tab_changing_areas(grab_screen, send_tab):
    '''
    Returns an array of images produced by cycling with tab over a window
    Put the mouse out of the way before calling this

    cases:
        cycles thru controls, looping ok
        there's only 1 control with focus already
        there's only 1 control, focus not set (2 screenshots)
        one of the controls will 'capture' and wont let the focus go out
    '''
    last_screen = Image2(grab_screen())
    images = [last_screen]
    tail = 0
    repeated = 0
    while True:
        last_screen = send_tab_expecting_change(send_tab,
                                                grab_screen,
                                                last_screen)
        images.append(last_screen)
        #consecutive match?
        if images[tail] == images[-1]:
            tail += 1
            repeated += 1
            if repeated > 2:
                break
        else:
            tail = 0
            repeated = 0
            #search if it starts repeating somewhere not in 1st screenshot
            for position in range(len(images) - 1):
                if images[position] == images[-1]:
                    tail = position + 1
                    repeated = 1
                    break

        if len(images) > 30:
            LOGGER.warning("Stopped tab cycling after 30 different "
                           "screenshots...")
            break

    for _ in range(repeated):
        images.pop()
        
    #remove repeated images in the tail if there are some
    while len(images) > 1 and images[-1] == images[-2]:
        images.pop()

    for _ in range(repeated-1):
        send_tab(backwards=True)
    
    LOGGER.debug("Got %s tab images" % len(images))        
    return images
       

def get_ui_changes(images, exclude_rects=None):
    '''
    Given the array of images returns the bounding box of the changing area
    between images[i] + images[i+1], and wraps around with
    images[-1] + images[0]
    '''
    #extract the bounding box of the changes in the images
    changed_areas = []
    for i in range(len(images)-1):
        coords = images[i].difference(images[i+1], exclude_rects)
        if not coords is None:
            changed_areas.append(coords)

    coords = images[-1].difference(images[0], exclude_rects)
    if not coords is None:
        changed_areas.append(coords)

    return changed_areas


def find_bounding_box(image, x_coord, y_coord, min_hspace=3, min_vspace=3,
                      min_width=4, min_height=8):
    '''
    Tries to find a bounding box for the given coordinates, it does so by
    trying to draw an imaginary box that grows in the x_direction and
    y_direction, the borders of such a box should only contain a solid
    background color, it is not suitable for use when there is a background
    texture.
    The min_width and min_height limits how small can either be the enclosing
    rectangle, is meant to use as for avoid enclosing single pixels or noise
    in the image.
    The image parameter must be a PIL.Image type
    '''
    #left = x_coord - min_hspace
    #top = y_coord - min_vspace
    #right = x_coord + min_hspace
    #bottom = y_coord + min_vspace
    left = x_coord
    top = y_coord
    right = x_coord + 1
    bottom = y_coord + 1
    
    top_rect_found = False
    right_rect_found = False
    bottom_rect_found = False
    left_rect_found = False
    borders_found = 0
    
    while borders_found < 4:
        borders_found = 0
        bg_color = image.getpixel((left, top))
        #explore top rect
        top_rect_found = True
        for current_x in range(left + 1, right):
            if bg_color != image.getpixel((current_x, top)):
                top_rect_found = False
                break

        right_rect_found = True
        for current_y in range(top, bottom):
            if bg_color != image.getpixel((right, current_y)):
                right_rect_found = False
                break
                
        bottom_rect_found = True
        for current_x in range(left, right):
            if bg_color != image.getpixel((current_x, bottom)):
                bottom_rect_found = False
                break
    
        left_rect_found = True
        for current_y in range(top + 1, bottom):
            if bg_color != image.getpixel((left, current_y)):
                left_rect_found = False
                break

        if not top_rect_found:
            top -= 1
            if top < 0:
                print "Top rect at -1"
                return False, (-1, -1, -1, -1)
        else:
            borders_found += 1
            
        if not right_rect_found:
            right += 1
            if right >= image.size[0]:
                print "Right rect over width"
                return False, (-1, -1, -1, -1)
        else:
            borders_found += 1
                
        if not bottom_rect_found:
            bottom += 1
            if bottom >= image.size[1]:
                print "Bottom rect over height"
                return False, (-1, -1, -1, -1)
        else:
            borders_found += 1
                
        if not left_rect_found:
            left -= 1
            if left < 0:
                print "Left rect at -1"
                return False, (-1, -1, -1, -1)
        else:
            borders_found += 1

        if borders_found == 4:
            #then rect should be able to grow min_hspace and min_vspace in all
            #directions
            new_left, new_right = left, right
            for _ in range(min_hspace):
                new_left -= 1
                new_right += 1
                for current_y in range(top, bottom):
                    if new_left >= 0:
                        if bg_color != image.getpixel((new_left, current_y)):
                            borders_found -= 1
                            left = new_left
                            break
                    if new_right < image.size[0]:
                        if bg_color != image.getpixel((new_right, current_y)):
                            borders_found -= 1
                            right = new_right
                            break
                if borders_found != 4:
                    break

            new_top, new_bottom = top, bottom
            for _ in range(min_vspace):
                new_top -= 1
                new_bottom += 1
                for current_x in range(left, right):
                    if new_top >= 0:
                        if bg_color != image.getpixel((current_x, new_top)):
                            borders_found -= 1
                            top = new_top
                            break
                    if new_bottom < image.size[1]:
                        if bg_color != image.getpixel((current_x, new_bottom)):
                            borders_found -= 1
                            bottom = new_bottom
                            break
                if borders_found != 4:
                    break

    #should shrink it now.
    white_line, new_top = True, bottom
    for y_pos in range(top + 1, bottom):
        for x_pos in range(left, right):
            if bg_color != image.getpixel((x_pos, y_pos)):
                white_line = False
                new_top = y_pos - 1
        if not white_line:
            break
    top = new_top
    
    white_line, new_left = True, right
    for x_pos in range(left + 1, right):
        for y_pos in range(top, bottom):
            if bg_color != image.getpixel((x_pos, y_pos)):
                white_line = False
                new_left = x_pos - 1
        if not white_line:
            break
    left = new_left

    white_line, new_bottom = True, top
    for y_pos in range(bottom - 1, top, -1):
        for x_pos in range(left, right):
            if bg_color != image.getpixel((x_pos, y_pos)):
                white_line = False
                new_bottom = y_pos + 1
        if not white_line:
            break
    bottom = new_bottom

    white_line, new_right = True, left
    for x_pos in range(right - 1, left, -1):
        for y_pos in range(top, bottom):
            if bg_color != image.getpixel((x_pos, y_pos)):
                white_line = False
                new_right = x_pos + 1
        if not white_line:
            break
    right = new_right
    
    if right - left < min_width or bottom - top < min_height:
        return False, (-1, -1, -1, -1)
    else:
        return True, (left, top, right, bottom)


def find_element_text(rect, image, right_whites=5):
    '''
    Searches for text that follows the given rect, for example it could be a
    radio button and it's acompanying text.
    Right whites specifies the minimum amount of clear pixels expected for
    detecting when the text finishes, setting this value too low can confuse
    the detection of the end of the text with a normal space
    The image parameter must be of Image2 type
    '''
    left, top, right, bottom = rect[0], rect[1], rect[2], rect[3]
    image = image.image
    bg_color = image.getpixel((left - 1, top - 1))
    white_lines = 0
    text_right = -1
    for right_limit in range(right + 10, image.size[0]):
        is_white = True
        for bottom_limit in range(top, bottom):
            if image.getpixel((right_limit, bottom_limit)) != bg_color:
                is_white = False
                break
        if is_white:
            white_lines += 1
            if white_lines > right_whites:
                text_right = right_limit
                break
        else:
            white_lines = 0
        
    if text_right == -1:
        return False, -1, -1, -1, -1
        
    return True, left, top - 3, text_right + 3, bottom + 2


def add_text_to_elements(rects, image):
    '''
    Returns a rect that includes the given rect and it's acompanying text at
    the right of it
    '''
    including_text = []
    for rect in rects:
        found, left, top, right, bottom = find_element_text(rect,
                                                            image,
                                                            right_whites=5)
        if found:
            including_text.append(get_bounding_box([rect,
                                                    (left,
                                                     top,
                                                     right,
                                                     bottom)]))
    return including_text
    

def is_container(element, elements):
    '''
    An element is considered container if it has at least 2 elements inside it,
    If there's only one then it is most likely a bug in the trimming of it
    At the moment there is some misdetection in certain conditions when a dialog
    has a 'default' control and the focus moves away to othe controls or
    containers
    '''
    inclusions = 0
    rect = [element['coords']]
    for candidate in elements:
        if candidate != element:
            if is_rect_inside(candidate['coords'], rect):
                inclusions += 1
                
    return inclusions > 1


def remove_containers(elements):
    '''
    Given a list of elements remove those that 'smells' like container
    misdetection
    '''
    filtered = []
    for element in elements:
        if is_container(element, elements) == False:
            filtered.append(element)
            
    return filtered
    
    
    
class Scraper(object):
    '''
    UserAutomation must have the extended methods
    '''
    
    def __init__(self, user_simulation=None, crop_taskbar=True):
        if not user_simulation:
            from murphy.user_simulation.local.local_user import User
            self._user_automation = User()
        else:
            self._user_automation = user_simulation

        path = os.path.dirname(__file__) + '/img'
        radio_images = [Image2(file_name=path + '/radio1.bmp',
                               color_mask=0xed1c2400),
                        Image2(file_name=path + '/radio2.bmp',
                               color_mask=0xed1c2400)]
        self._radio = UIElement(radio_images)
        
        check_images = [Image2(file_name=path + '/check1.bmp',
                               color_mask=0xed1c2400),
                        Image2(file_name=path + '/check2.bmp',
                               color_mask=0xed1c2400)]
        self._checkboxes = UIElement(check_images)
        self._crop_taskbar = crop_taskbar
    
        self._internal_counter = 0
    
    
    def _grab_screen(self):
        '''
        Convenient method for grabbing the screen while cropping the taskbar
        too
        '''
        screen = self._user_automation.grab_screen()
        if self._crop_taskbar:
            return screen.crop((0, 0, screen.size[0], screen.size[1] - 41))
        else:
            return screen.image
    
    
    def _send_tab(self, backwards=False):
        '''
        Shorthand for sending a tab
        '''
        if not backwards:
            self._user_automation.keyboard.enters("{tab}")
        else:
            self._user_automation.keyboard.enters("{+shift}{tab}{-shift}")
        
        
    def _find_elements_by_mousehover(self, tab_screens=None, ui_changes=None):
        '''
        Find elements in the active window using the tab key and mouse hovering
        techniques.
        '''
        self._user_automation.mouse.move(1, 1)
        if tab_screens is None:
            tab_screens = get_tab_changing_areas(self._grab_screen,
                                                 self._send_tab)
        if ui_changes is None:
            ui_changes = get_ui_changes(tab_screens)
        start_screen = Image2(self._grab_screen())
        
        extracted_areas = []
        
        points = get_corner_points(ui_changes, 3, 3)

        for point in points:
            if not point_inside_rects((point[0], point[1]), extracted_areas):
                self._user_automation.mouse.move(point[0], point[1])
                current_screen = Image2(self._grab_screen())
                if current_screen != start_screen:
                    changed_area = current_screen.difference(start_screen)
                    if not changed_area in extracted_areas:
                        if point_inside_rects((point[0], point[1]),
                                              [changed_area]):
                            extracted_areas.append(changed_area)

        return extracted_areas


    def get_elements(self, hints=None, window_origin=None):
        '''
        Returns a list of UI elements that this class can identify from the
        currently active window.
        The return of this implementation is an array of dictionaries where
        each dictionary describes the control type and it's bounding box
        '''
        if hints is None:
            hints = {}
        if window_origin is None:
            window_origin = (0, 0)
            
        if hints.get('outfocus method', False):
            result = self.get_elements_by_app_outfocus(hints, window_origin)
            if result != False:
                return result
            else:
                LOGGER.warning('Unable to properly use the outfocus hint, '
                               'reverting to standard behaviour for this node.')
        
        self._user_automation.mouse.move(1, 1)
            
        screen = self._grab_screen()
        screen_height = screen.size[1]
        screen = Image2(screen)
        
        tab_screens = get_tab_changing_areas(self._grab_screen,
                                             self._send_tab)
        
        if len(tab_screens) == 1:
            LOGGER.info('Only one image obtained when cycling with tab, adding'
                        ' alt trick.')
            self._user_automation.keyboard.enters('{alt}')
            #we're searching for very small clue here... just one _
            new_screen = Image2(self._grab_screen(), tolerance=1.0)
            tab_screens.append(new_screen)
            
        candidates = []
        processed = []
        for i in range(len(tab_screens)-1):
            coords = tab_screens[i].difference(tab_screens[i+1])
            if coords:
                LOGGER.debug("Changes from %s to %s are: %s" % (i,
                                                                i + 1,
                                                                str(coords)))
                division = automation_helpers.find_inner_bbox(tab_screens[i],
                                                              tab_screens[i+1],
                                                              coords)
                    
                LOGGER.debug("Splitting found %s bboxes (%s)" % (len(division),
                                                                 str(division)))
                for rect in division:
                    if not rect in candidates:
                        LOGGER.debug("Adding: %s" % str(rect))
                        candidates.append(rect)
                        #hover, if image differs take diff coords, use biggest
                        # of two use mouse pointer clue for type
                        #ARGGGGGG cursor blinking... deactivated at os level for
                        #now
                        
                        #the focus may be at this point anywhere and on 1st
                        #case is where it is left from tab navigation, for
                        #cases like menu we have to highlight current menu item
                        center = center_of_rect(rect)
                        self._user_automation.mouse.move(center[0], center[1])
                        self._user_automation.mouse.move(center[0]+1,
                                                         center[1]+1)
                        cursor = self._user_automation.get_current_cursor()
                        screen1 = Image2(self._grab_screen())
                        self._user_automation.mouse.move(1, screen_height)
                        screen2 = Image2(self._grab_screen())
                        diff = screen1.difference(screen2)
                            
                        if diff: #produced a change in UI, must be button
                            LOGGER.debug(("Will compute biggest rect out of "
                                          "%s %s") % (str(rect), str(diff)))
                            biggest_rect = get_bounding_box([rect, diff])
                            if not biggest_rect in processed:
                                processed.append(biggest_rect)
                                LOGGER.debug("Added: %s" % str(biggest_rect))
                        else:
                            #no UI change, can be a link, text or misfired
                            #recognition, exceptional case is one button alone
                            #in dialog
                            if ((cursor != 'normal' and not rect in processed) or
                              (len(tab_screens) == 2 and not rect in processed)):
                                processed.append(rect)
                                LOGGER.debug("Added: %s" % str(rect))
        
        LOGGER.debug("There are %s elements to consider from tab + hovering" %
                     len(processed))
        
        checkboxes = self._checkboxes.find_all(screen)
        LOGGER.debug("Found %s checkboxes" % len(checkboxes))
        checkboxes = add_text_to_elements(checkboxes, screen)

        radios = self._radio.find_all(screen)
        LOGGER.debug("Found %s radios" % len(checkboxes))
        radios = add_text_to_elements(radios, screen)

        checkboxes = merge_overlapping_areas(checkboxes, processed)
        radios = merge_overlapping_areas(radios, processed)
        
        areas = exclude_subareas(processed, checkboxes + radios)
        
        points = hints.get('points of interest', [])
        LOGGER.debug("Points of interest are: %s" % str(points))
        for point in points:
            point_x = window_origin[0] + point[0]
            point_y = window_origin[1] + point[1]
            found, bbox = find_bounding_box(screen.image, point_x, point_y)
            if found:
                LOGGER.debug("Found %s from point of interest" % str(bbox))
                areas.append(bbox)
            else:
                LOGGER.debug("Nothing found from point of interest at %s %s" %
                             (point_x, point_y))
        
        result = []
        for area in areas:
            center_x, center_y = center_of_rect(area)
            self._user_automation.mouse.move(center_x, center_y)
            self._user_automation.mouse.move(center_x + 1, center_y + 1)
            cursor = self._user_automation.get_current_cursor()
            element = {'coords': (area[0], area[1], area[2], area[3]),
                       'type': cursor}
            result.append(element)
            
        for area in checkboxes:
            element = {'coords': (area[0], area[1], area[2], area[3]),
                       'type': 'checkbox'}
            result.append(element)

        for area in radios:
            element = {'coords': (area[0], area[1], area[2], area[3]),
                       'type': 'radio'}
            result.append(element)

        result = remove_containers(result)
        return result
    
    
    def get_elements_by_hover_points(self, window_origin, hover_points):
        '''
        Simple recognition based on hovering the mouse thru the given
        list of points, the points should be close to the center of the
        elements and the elements must highlight on mouseover to work properly
        Points are relative to the window, not absolute screen coords
        '''
        self._user_automation.mouse.move(1, 1)
        screen = Image2(self._grab_screen())
        result = []
        for point in hover_points:
            hover_x = window_origin[0] + point[0]
            hover_y = window_origin[1] + point[1]
            self._user_automation.mouse.move(hover_x, hover_y)
            self._user_automation.mouse.move(hover_x + 1, hover_y + 1)
            screen_when_hover = Image2(self._grab_screen())
            coords = screen.difference(screen_when_hover)
            if coords:
                cursor = self._user_automation.get_current_cursor()
                element = {'coords': coords, 'type': cursor}
                result.append(element)
        
        return result
        

    def get_elements_by_app_outfocus(self, hints=None, window_origin=None):
        '''
        Alternate algorithm, tries to find the elements by setting the focus
        in the desktop and then back to the application while analyzing the
        difference on the screen, when the application loses the focus the
        normal behaviour in windows is that the active control is not shown
        with the focus
        This technique has some caveats, for example the border of the
        application needs to be ignored, also the default button will also
        be rendered differently giving in some cases 2 areas with changes
        '''
        self._user_automation.mouse.move(1, 1)
        if hints is None:
            hints = {}
        if window_origin is None:
            window_origin = (0, 0)
        rects = []
        repeated = 0
        attempts = 0
        while True:
            screen = Image2(self._grab_screen())
            width = screen.size[0]
            self._user_automation.mouse.click(width / 2, screen.size[1] + 5)
            time.sleep(0.1)
            screen2 = Image2(self._grab_screen())
            self._user_automation.keyboard.enters("{+alt}{tab}{+shift}"
                                                  "{tab}{-shift}{-alt}")
            time.sleep(1)
            
            #coords = screen.difference(screen2)
            coords = automation_helpers.crop_border_differences(screen, screen2)
            crop1 = screen.image.crop((coords[0],
                                       coords[1],
                                       coords[2] + 1,
                                       coords[3] + 1))
            crop2 = screen2.image.crop((coords[0],
                                        coords[1],
                                        coords[2] + 1,
                                        coords[3] + 1))
            coords2 = Image2(image=crop1).difference(Image2(image=crop2))
            if coords2:
                coords = (coords[0] + coords2[0],
                          coords[1] + coords2[1],
                          coords[0] + coords2[2],
                          coords[1] + coords2[3])
            divisions = automation_helpers.find_inner_bbox(screen,
                                                           screen2,
                                                           coords)
            LOGGER.debug("Splitting found %s bboxes (%s)" % (len(divisions),
                                                             str(divisions)))
            repeated_in_divisions = 0
            for rect in divisions:
                print "resulting coords %s" % str(rect)
                if rect in rects:
                    repeated_in_divisions += 1
                else:
                    rects.append(rect)
            if repeated_in_divisions == len(divisions):
                repeated += 1
                if repeated == 2:
                    break
            self._user_automation.keyboard.enters("{tab}")
            time.sleep(0.1)
            attempts += 1
            if attempts - len(rects) > 5:
                #something is wrong, is possible that is unable to detect 
                #horizontal division at all
                return False
        
        result = []
        for rect in rects:
            self._user_automation.mouse.move(1, 1)
            time.sleep(0.2)
            before_cursor = self._user_automation.get_current_cursor()
            before_screen = Image2(self._grab_screen())
            center_x, center_y = center_of_rect(rect)
            self._user_automation.mouse.move(center_x, center_y)
            self._user_automation.mouse.move(center_x + 1, center_y + 1)
            time.sleep(0.2)
            after_screen = Image2(self._grab_screen())
            after_cursor = self._user_automation.get_current_cursor()

            ui_changes = before_screen != after_screen
            cursor_changes = before_cursor != after_cursor
            everything = not hints.get('visual clue needed', True)
            if cursor_changes or ui_changes or everything:
                element = {'coords': (rect[0], rect[1], rect[2], rect[3]),
                           'type': after_cursor}
                result.append(element)

        return result
        

def scrap_state(node, world, scraper_hints, node_hints):
    '''
    Scraps the ui into the given node for the given world state
    '''
    node_index = node.graph.nodes.index(node)
    node.name = 'Node %s' % node_index
    node.file_name = 'node_%s' % str(node_index).zfill(2)

    screen_image = world.machine.automation.grab_screen()
    screen = Image2(image=screen_image)

    LOGGER.debug("Node hints for scrapper, node %s are %s" % (node_index,
                                                            str(scraper_hints)))
    is_desktop = False
    if scraper_hints.get('windowless', False):
        #rect is difference between world.last_screen and screen
        no_taskbar = world.last_screen
        no_taskbar = world.last_screen.crop((0,
                                             0,
                                             no_taskbar.size[0],
                                             no_taskbar.size[1] -
                                                  TASKBAR_HEIGHT))
        window_rect = Image2(image=no_taskbar).difference(screen)
        window_rect = automation_helpers.refine_window_rect(screen_image,
                                                            window_rect)
    else:
        is_desktop, window_rect = solve_active_window_rect(world, screen_image)
        
    window_image = Image2(image=screen_image.crop(window_rect))
    node.reference_images.append(window_image)
    
    node.last_location = window_rect
    #Don't scrap the desktop!
    print "Screen size %s, window_rect %s" % (str(screen_image.size),
                                              str(window_rect))
    
    if is_desktop == "Screen":
        LOGGER.info("Disabling outfocus method as window rect is the whole screen")
        scraper_hints['outfocus method'] = False
        is_desktop = False
        
    if not is_desktop:
        scraper = Scraper(world.machine.automation, crop_taskbar=True)
        if 'defined by hover points' in scraper_hints:
            LOGGER.debug("Node defined by hover points")
            elements = scraper.get_elements_by_hover_points((window_rect[0],
                                                             window_rect[1]),
                                       scraper_hints['defined by hover points'])
        else:
            elements = scraper.get_elements(scraper_hints,
                                            (window_rect[0], window_rect[1]))
    else:
        #FIXME: could search for new icons...
        elements = []
        
    LOGGER.debug("Found elements: %s" % str(elements))

    LOGGER.debug("Node hints for node %s are %s" % (node_index,
                                                    str(node_hints)))
    ignorable_areas = node_hints.get('ignorable', [])
    for element in elements:
        element_rect = move_rect(element['coords'],
                                 (window_rect[0], window_rect[1]))

        if not is_rect_inside(element_rect, ignorable_areas):
            edge_name = 'Element %s' % len(node.edges)
            edge = node.create_edge(edge_name)
            edge.location = element_rect
            edge.absolute_location = element['coords']
            edge.ui_type = element['type']
            elem_rect = expand_rect(element['coords'], (1, 1))
            screenshot = Image2(image=screen.image.crop(elem_rect))
            edge.screenshots.append(screenshot)
            if edge.ui_type == 'text':
                edge.head = node
        else:
            LOGGER.debug(("Ignoring element at %s as it is inside ignorable" +
                          " area") % str(element_rect))
