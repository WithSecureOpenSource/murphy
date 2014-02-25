'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Wraps around what it is a user interface element, it can be anything that is
visible.
'''
from model_extraction.image2 import Image2

class UIElement(object):
    '''
    Encapsulates identification functionality for what it is a user interface
    element, it can be anything that can be seen on a screen
    The element is defined by an image or array of images (Image2) and can
    contain ignorable / mask areas, it is not neccessary that all the images
    are of the same size.
    When there are more than one possible instance of a given element in screen
    use the index and container to uniquely identify it.
    Index is calculated as the closest to the coordinate 0, 0 will be index=0,
    the rest are sorted by order of appearance from natural order (left to
    right, top to bottom)
    Container can be anoter ui element, for example a window, if specified then
    first the container is searched, then the given ui element is searched
    inside the container, providing a parent / child relationship, this
    relationship can be as deeep as needed, so a container can be inside
    another container inside another container, etc.
    
    Simple usage sample of UIElement combined with user automation:
    >>> from model_extraction import ui_element, image2
    >>> from model_extraction.user_simulation import vnc_user
    >>>
    >>> im = image2.Image2(file_name='start_menu.bmp', color_mask=0xed1c2400)
    >>> elem = ui_element.UIElement(images=[im])
    >>> user = vnc_user.VncUser('10.133.34.5', 5903, None, None)
    >>> user.click(elem, max_wait=30)
    '''

    def __init__(self, images, index=0, container=None):
        self._images = images
        self._index = index
        self._container = container


    @property
    def images(self):
        '''
        Returns an array of the images (Image2) that defines this ui element
        We dont want accidental modifications as it supposed to be immutable
        '''
        return self._images[:]
        
        
    def find_in(self, image):
        '''
        Searches this ui element in the given image, returns a 4-tuple with
        the enclosing rectangle coordinates or None if not found
        '''
        matches = self.find_all(image)
        if self._index < len(matches):
            return matches[self._index]
        else:
            return None

        
    def find_all(self, image):
        '''
        Searches all occurrences of this ui element without considering the
        index. Returns an array of 4-tuples with each element enclosing
        rectangle coordinates, or an empty array
        '''
        if self._container:
            sub_area = self._container.find_in(image)
            image = Image2(image.image.crop(sub_area))
        
        matches = []
        for template in self._images:
            rects = image.find_all(template)
            matches.extend(rects)
        
        image_width = image.size[0]
        matches.sort(key=lambda rect: (rect[1] * image_width) + rect[0])
        return matches
        
        
    def is_at(self, image, location):
        '''
        Returns true if any of the templates is found in the given absolute
        location (x, y tuple), false otherwise
        '''
        for template in self._images:
            if image.test(template, location[0], location[1])[0]:
                return True
        return False
        
    