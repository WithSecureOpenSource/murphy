'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

A node in a ui graph represents a parametrized view of a state, it is usually
(but not always) represented with a dialog (or a state of a dialog)

In general the parametrization of a dialog is the ui elements it contains and
that either the user can interact with, or that they can change, for example
a label that displays some value that may change (think a date time for example)
or a button / checkbox / etc.
Most parametrized values of a dialog would be represented as edges of it  

'''

import json, uuid, StringIO

from model_extraction import graph
from model_extraction.ui.utils import dump_array
from model_extraction.ui.ui_element import UIElement
from model_extraction.image2 import Image2
from model_extraction.ui.edge import Edge
from model_extraction.geometry import expand_rect

import logging
LOGGER = logging.getLogger('root.' + __name__)


class Node(graph.Node):
    '''
    Wraps around a graph node, adds ui information to it like parametrized
    and reference screenshots
    '''
    
    def __init__(self, name, directory, images_directory):
        super(Node, self).__init__(name)
        self.file_name = None
        self.directory = directory
        self.images_dir = images_directory
        self.title = ''
        self.windowless = False
        self.desktop_icon = False
        self.custom = {}
        
        images_in = directory + '/' + images_directory
        self.screenshots = []
        self.reference_images = []

        self._ui_element = None
        self.enter_hook = None
        
        #Fixed position tells it will always appears in the same spot, such
        #cases can optimize the search a lot
        self.fixed_position = True
        self.last_location = None

        
    @property
    def ui_element(self):
        '''
        Returns an ui element representation of this node / state as many things
        can be conviniently done thru it 
        '''
        if self._ui_element is None:
            self._ui_element = UIElement(self.screenshots)
        return self._ui_element


    def find_in(self, screen):
        '''
        Optimized search that considers if objects appears in the same position
        always, returns the location where it is found or None if not found
        '''
        if self.fixed_position == True and not self.last_location is None:
            LOGGER.debug("Optimized check, last position was %s" % str(
                                                            self.last_location))
            found = self.ui_element.is_at(screen, self.last_location)
            if found:
                return self.last_location
            else:
                return None
        else:
            found = self.ui_element.find_in(screen)
        
        if found:
            self.last_location = found

        return found
            
    
    def is_in(self, world):
        '''
        Checks if this node is recognizable at this moment in the screen,
        returns either True or False
        '''
        LOGGER.debug("Checking if i'm in %s" % self.name)

        if ((len(self.edges) == 1 and self.edges[0].ui_type == 'desktop icon')
          or self.desktop_icon == True):
            rect = world.machine.helper.get_active_window_rect()
            if rect and rect[0] > 0 and rect[1] > 0:
                LOGGER.debug("Not there, desktop icons are detectable when "
                             "there are no active windows")
                return False

        screen = Image2(image=world.machine.automation.grab_screen())
        found = self.find_in(screen)
        
        if found:
            LOGGER.debug("Found")
            return True
        else:
            LOGGER.debug("Not found")
            return False
    
        
    def create_edge(self, name, head=None):
        '''
        Creates an Edge with this node as it's tail and the given one as
        it's head.
        The name of the edge cannot be the same as other edges of this
        node.
        '''
        edge = Edge(self, name, head, self.directory + '/' + self.images_dir)
        self.edges.append(edge)
        return edge
        

    def parametrize(self, ignorable_areas):
        '''
        For the given node we need to mark as dynamic the changing areas
        and ensure recognition of it will go smooth
        FIXME: should check sanity validate on tab images
        '''
        if self.file_name is None:
            raise Exception("Node file name must be set before parametrize!")

        if len(self.reference_images) == 0:
            raise Exception("No reference images available to parametrize")
            
        dialog = self.reference_images[0].image
        color = (237, 28, 36, 0)
        for edge in self.edges:
            if edge.location:
                elem_rect = expand_rect(edge.location, (1, 1))
                dialog.paste(color, elem_rect)
            
        LOGGER.debug("Parametrizing with %s ignorable areas" % 
                     len(ignorable_areas))
        for area in ignorable_areas:
            elem_rect = expand_rect(area, (1, 1))
            dialog.paste(color, elem_rect)
            
        dialog = Image2(image=dialog,
                        color_mask=0xed1c2400,
                        tolerance=self.graph.image_tolerance)
        self.screenshots.append(dialog)


    def parametrize2(self, ignorable_areas):
        '''
        For the given node we need to mark as dynamic the changing areas
        and ensure recognition of it will go smooth
        FIXME: should check sanity validate on tab images
        '''
        if self.file_name is None:
            raise Exception("Node file name must be set before parametrize!")

        if len(self.reference_images) == 0:
            raise Exception("No reference images available to parametrize")

        if self.desktop_icon:
            LOGGER.info("Desktop icon types are not parametrizable")
            return
        
        dialog = self.reference_images[0].image
        parametrized_dialog = dialog.copy()
        color = (237, 28, 36, 0)
        for edge in self.edges:
            if edge.location:
                elem_rect = expand_rect(edge.location, (1, 1))
                parametrized_dialog.paste(color, elem_rect)
                image = dialog.crop(edge.location)
                edge.screenshots.append(Image2(image))
            
        LOGGER.debug("Parametrizing with %s ignorable areas" % 
                     len(ignorable_areas))
        for area in ignorable_areas:
            elem_rect = expand_rect(area, (1, 1))
            parametrized_dialog.paste(color, elem_rect)
            
        parametrized_dialog = Image2(image=parametrized_dialog,
                                     color_mask=0xed1c2400,
                                     tolerance=0.99)
        self.screenshots.append(parametrized_dialog)
        
    
    def _get_screenshot_file_name(self, screenshot):
        '''
        Returns the file name to use for the given screenshots, provides default
        value when not set
        '''
        file_name = screenshot.file_name
        if file_name is None:
            index = self.screenshots.index(screenshot)
            file_name = '%s.%s.bmp' % (self.file_name, str(index))
        return file_name

        
    def _screenshots_to_json(self):
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
        images_dir = self.directory + '/' + self.images_dir
        for screenshot in self.screenshots:
            image = screenshot.image
            file_name = self._get_screenshot_file_name(screenshot)
            image.save("%s/%s" % (images_dir, file_name))


    def _get_reference_image_file_name(self, image):
        '''
        Returns the file name to use for the given screenshots, provides default
        value when not set
        '''
        file_name = image.file_name
        if file_name is None:
            index = self.reference_images.index(image)
            file_name = '%s.%s.ref.bmp' % (self.file_name, str(index))
        return file_name

        
    def _reference_images_to_json(self):
        '''
        Returns the screenshots as a json array with file name and mask
        '''
        ret_array = []
        for screenshot in self.reference_images:
            ret_array.append({'image': None,
                        'file': self._get_reference_image_file_name(screenshot),
                              'mask': screenshot.color_mask})
        return ret_array
    
    
    def save_reference_images(self):
        '''
        Saves node screenshots, provides default or overrided file names for it
        '''
        images_dir = self.directory + '/' + self.images_dir
        for screenshot in self.reference_images:
            image = screenshot.image
            file_name = self._get_reference_image_file_name(screenshot)
            image.save("%s/%s" % (images_dir, file_name))

        
    def save(self):
        '''
        Saves this node as a json file
        '''
        content = {'HERE': 
                    {'desc': self.name,
                     'screenshots': self._screenshots_to_json(),
                     'reference screenshots': self._reference_images_to_json(),
                     'custom': self.custom,
                     'title': self.title}}

        index = 0
        #FIXME: edge method should return it's json form
        for edge in self.edges:
            destination = None
            if edge.head:
                destination = edge.head.name
            verb = {'desc': edge.name,
                    'goes to': destination,
                    'how': None}
                    
            if edge.method_source_code is None:
                verb['how'] = {'screenshots': edge.screenshots_to_json(),
                               'type': edge.ui_type,
                               'visual': edge.location,
                               'custom': edge.custom}
            else:
                verb['how'] = (edge.method_source_code[0],
                               edge.method_source_code[1])

            content['V_ELEM_%s' % str(index).zfill(2)] = verb
            edge.save_screenshots()
            index += 1

            if len(edge.logs) > 0:
                #save as separate file
                log_name = "log-%s.json" % str(uuid.uuid1())
                edge.logs['filename'] = log_name
                encoded = json.dumps(edge.logs, sort_keys=True, indent=4)
                with open(self.directory + "/" + log_name, "w") as the_file:
                    the_file.write(encoded)
                verb['logs'] = log_name
            
        encoded = json.dumps(content, sort_keys=True, indent=4)
        json_file_name = "%s/%s.json" % (self.directory, self.file_name)
        with open(json_file_name, "w") as the_file:
            the_file.write(encoded)
        
        self.save_screenshots()
        self.save_reference_images()
        
    
    def save_as_python(self):
        '''
        Saves this node as a python murphy friendly file
        '''
        py_file_name = "%s/%s.py" % (self.directory, self.file_name)
            
        output = StringIO.StringIO()
        output.write("'''\n"
                     "Automatically generated from a model extractor\n"
                     "'''\n\n"
                     "#Needed due to mismatch with json...\n"
                     "true = True\n"
                     "false = False\n\n") 
        
        output.write("HERE = {'desc': '%s',\n" % self.name)
        output.write("        'snapshots': ")
        dump_array(output, self._screenshots_to_json(), 'file', True)
        output.write(",\n")
        output.write("        'snapshots mask': ")
        dump_array(output, self._screenshots_to_json(), 'mask', False)
        output.write(",\n")
        output.write("        'reference snapshots': ")
        dump_array(output, self._reference_images_to_json(), 'file', True)
        
        encoded = json.dumps(self.custom)
        output.write(",\n        'custom': %s" % encoded)
        
        output.write("}\n\n\n")
        output.write("WORKER = None")
        output.write("\n\n\n")
                
        index = 0
        for edge in self.edges:
            if edge.location:
                name = "ELEM_%s" % str(index).zfill(2)
                output.write("%s = {'visual': %s,\n" % (name,
                                                        str(edge.location)))
                output.write("           'snapshots': ")
                dump_array(output, edge.screenshots_to_json(), 'file', True)
                if edge.ui_type == 'text':
                    output.write(",\n           'uses': 'value for %s.%s'" %
                                                         (self.name, edge.name))
                    output.write(",\n           'type': 'text input'}\n\n")
                else:
                    output.write(",\n           'type': '%s'}\n\n" % 
                                                                   edge.ui_type)
            if edge.method_source_code:
                output.write(edge.method_source_code[1])
                output.write("\n\n")
            index += 1

        output.write("\n")
        index = 0
        for edge in self.edges:
            output.write("V_ELEM_%s = {'desc': '%s'" % (str(index).zfill(2),
                                                        str(edge.name)))
            destination = edge.head
            spacing = ' ' * 13
            if destination:
                destination = destination.name
                output.write(",\n%s'goes to': '%s'" % (spacing, destination))

            if edge.method_source_code:
                output.write(",\n%s'how': %s" % (spacing,
                                                 edge.method_source_code[0]))
            elif edge.location:
                output.write(",\n%s'how': ELEM_%s" % (spacing,
                                                      str(index).zfill(2)))
            
            if edge.ui_type == 'text':
                output.write(",\n%s'uses': 'value for %s.%s'" % (spacing,
                                                                 self.name,
                                                                 edge.name))
            
            if self.name == 'node_00' and edge.method_source_code is None:
                output.write(",\n%s'how': launch_application" % spacing)

            encoded = json.dumps(edge.custom)
            output.write(",\n%s'custom': %s" % (spacing, encoded))
     
            if len(edge.logs) > 0:
                log_name = json.dumps(edge.logs['filename'])
                output.write(",\n%s'logs': %s" % (spacing, log_name))
                
            output.write("}\n\n")
            index += 1
        
        with open(py_file_name, "w") as the_file:
            the_file.write(output.getvalue())


    def import_from_file(self, file_name, images_dir):
        '''
        Imports this node from a file, images_dir does not replace the node
        directory or images_dir
        '''
        with open(file_name, "rb") as the_file:
            json_node = json.load(the_file)
        self.name = json_node['HERE']['desc']
        use_name = file_name
        if use_name.find('.') != -1:
            use_name = use_name.split('.')[0]
        self.file_name = use_name.split("/")[-1].split("\\")[-1]
        for reference in json_node['HERE']['reference screenshots']:
            an_image = Image2(file_name="%s/%s" % (images_dir,
                                                   reference['file']),
                              color_mask=reference.get('mask'))
            an_image.file_name = None
            self.reference_images.append(an_image)
        for screenshot in json_node['HERE']['screenshots']:
            an_image = Image2(file_name="%s/%s" % (images_dir,
                                                   screenshot['file']),
                              color_mask=screenshot.get('mask'))
            an_image.file_name = None
            self.screenshots.append(an_image)
        self.title = json_node['HERE'].get('title', '')

        keys = list(json_node.keys())
        keys.remove('HERE')
        keys.sort()    
        for i in range(len(keys)):
            elem = json_node[keys[i]]
            edge = self.create_edge(elem['desc'])
            #FIXME: implement edge.head set
            edge.location = elem['how']['visual']
            edge.ui_type = elem['how']['type']
            for screenshot in elem['how']['screenshots']:
                an_image = Image2(file_name="%s/%s" % (images_dir,
                                                       screenshot['file']),
                                  color_mask=screenshot.get('mask'))
                an_image.file_name = None
                edge.screenshots.append(an_image)