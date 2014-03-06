'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Represents an edge of a ui graph
An edge in this context is what a user can do in a given state, for example
an ok button, a dropdown box, etc

An edge does not (but usually will) have a visual representation, it is in
itself something that triggers a transition into a different state
'''

from model_extraction import graph
from model_extraction.image2 import Image2
from model_extraction.geometry import center_of_rect

import logging
LOGGER = logging.getLogger('root.' + __name__)

class Edge(graph.Edge):

    def __init__(self, tail, name, head=None, images_directory=None):
        super(Edge, self).__init__(tail, name, head)
        self.screenshots = []
        self.location = None
        self.absolute_location = None
        self.visits = 0
        self.ui_type = None
        self.method = None
        self.method_source_code = None
        self.custom = {}
        self.logs = {}


    def clone(self):
        new_edge = self.tail.create_edge(self.name)
        new_edge.screenshots = self.screenshots[:]
        new_edge.location = self.location
        new_edge.absolute_location = self.absolute_location
        new_edge.ui_type = self.ui_type
        new_edge.method = self.method
        new_edge.method_source_code = self.method_source_code
        new_edge.custom =  self.custom.copy()
        return new_edge
    
        
    def _get_screenshot_file_name(self, screenshot):
        '''
        Returns the file name to use for the given screenshots, provides default
        value when not set
        '''
        file_name = screenshot.file_name
        if file_name is None:
            index = self.screenshots.index(screenshot)
            file_name = '%s.edge.%s.%s.bmp' % (self.tail.file_name,
                                               self.name,
                                               str(index))
        return file_name
    
        
    def screenshots_to_json(self):
        '''
        Returns the screenshots as a json array with file name and mask
        '''
        ret_array = []
        for screenshot in self.screenshots:
            ret_array.append({'image': None,
                              'file': self._get_screenshot_file_name(screenshot),
                              'mask': screenshot.color_mask})
        return ret_array
    
    
    def save_screenshots(self):
        '''
        Saves node screenshots, provides default or overrided file names for it
        '''
        images_dir = self.tail.directory + '/' + self.tail.images_dir
        for screenshot in self.screenshots:
            image = screenshot.image
            file_name = self._get_screenshot_file_name(screenshot)
            image.save("%s/%s" % (images_dir, file_name))
            
                
    def perform(self, world):
        LOGGER.info("Performing %s" % str(self))
        screen = world.machine.automation.grab_screen()
        world.last_screen = screen.copy()
        
        if self.method:
            self.method(world) # pylint: disable=E1102
        else:
            #found = self.tail.ui_element.find_in(Image2(image=screen))
            found = self.tail.find_in(Image2(image=screen))
            if found:
                #links usually need to be clicked close to the left
                #top coord (if left aligned) but some buttons needs
                #the center as they shade in the borders
                if self.ui_type == 'link':
                    x_coord = found[0] + self.location[0] + 4
                    y_coord = found[1] + self.location[1] + 4
                else:
                    center_x, center_y = center_of_rect(self.location)
                    x_coord = found[0] + center_x
                    y_coord = found[1] + center_y
                #Some quite seldom and random issues when clicking!?
                world.machine.automation.mouse.move(x_coord - 1, y_coord - 1)
                world.machine.automation.mouse.click(x_coord, y_coord)
                if self.ui_type == 'desktop icon':
                    world.machine.automation.mouse.click()
                elif self.ui_type == 'text' and 'test value' in self.custom:
                    world.machine.automation.keyboard.enters(
                                          self.custom['test value'][0]['value'])
            else:
                screen.save("Current screen.bmp")
                raise Exception("Parent node (%s) not found in screen!" %
                                                                 self.tail.name)
                
        #FIXME: for recording purposes this is needed, for playback purposes
        #the destination should be checked by waiting...
        world.machine.automation.mouse.move(1, 1)
        world.machine.wait_idling()
        if self.head:
            destination_reached = False
            # FIXME: this is not entirely correct, some long transitions may
            # happen for example during installations or parts of the
            # applications were it looks like stuck for a while
            for i in range(3):
                destination_reached = self.head.is_in(world)
                if destination_reached:
                    break
                LOGGER.info("Expected destination not in screen yet, "
                            "waiting (%s)" % i)
                world.machine.wait_idling()
                
            if destination_reached == False:
                LOGGER.info("Expected destination not in screen, could be a "
                            "type of return to caller scenario")
            elif self.head.enter_hook:
                self.head.enter_hook(world)