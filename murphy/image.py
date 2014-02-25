'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Low level search images function

Searches operates over ImageHolder, which internally catches some processed
information, to build one just pass a PIL Image to it

Two API's are provided:
find_image, searches an image within another image
test_image, tests if the given image is within another image at the given
coordinates

Both API's support 'ignorable areas', when a color mask is specified that
specific color will be ignored when comparing / searching. See ImageHolder
constructor

Higher level functions can be found at smart_image, they can search multiple
images at once (as if a specific object were defined by a series of images
instead of one), also catching 'last seen position' and other optimizations

FIXME: parametrize if failed wait should write debugging images
FIXME: parametrize load and save of search memory (search hints)
FIXME: document effectiveness, strengths and weaknesses
'''
from PIL import Image
import os, ctypes, logging
from datetime import datetime

LOGGER = logging.getLogger('root.' + __name__)
_SEARCH_COUNTER = 0
IMAGE_RESULTS_CACHE = dict()

#True will save every search as a snapshot
_SAVE_SEARCHES = False
_SAVE_FAILED_SEARCHES = False

#FIXME: this needs platform specific logic, dll would be .so and probably
#under an os/ path or something like that
try:
    _IMAGE_DLL = ctypes.WinDLL('%s/img_murphy.dll' % os.path.dirname(__file__))
except:
    try:
        _IMAGE_DLL = ctypes.WinDLL(os.path.join(os.path.dirname(__file__),
                                    '..',
                                    'accessories',
                                    'img_murphy.dll'))
    except:
        _IMAGE_DLL = ctypes.cdll.LoadLibrary('./img_murphy.so')
        

class ImageHolder():
    '''
    Utility class that holds an image and catches some interal data for
    efficiency
    '''
    
    def __init__(self, image, color_mask=None):
        '''
        Constructs an ImageHolder for the given image or file name
        Example:

        >>> to_search = ImageHolder("self_test\\Open File - Security Warning.bmp")

        Or
        >>> img = Image.open("self_test\\Open File - Security Warning.bmp")
        >>> to_search = ImageHolder(img)
        '''
        #FIXME: find a better way, this is rather bad / breakable
        if type(image) is str or type(image) is unicode:
            image = Image.open(image)
        self.image = image
        self._ptr = None
        self._color_mask = color_mask
        self._mask_ptr = None
        if image is None:
            raise Exception("Cannot create an image holder for none image")

    def get_ptr(self):
        '''
        Returns a catched copy if the raw data converted to grayscale
        '''
        if not self._ptr:
            self._ptr = _get_exportable_array_ptr(self.image)
        return self._ptr

    def get_mask_color(self):
        '''
        Returns the color used as ignorable
        '''
        return self._color_mask

    def get_mask_ptr(self):
        '''
        Returns the mask bitmap if there's one, a mask bitmap is a grayscale
        mask that states which pixels should be ignored (nonzero) and which
        pixels should be considered (zeros) when checking image matches
        '''
        #FIXME: there must be an easier way with PIL primitives for doing this.
        if self._color_mask is None:
            return None
        if self._mask_ptr:
            return self._mask_ptr
            
        raw = self.image.convert('RGBX').tostring('raw')
        total_pixels = self.image.size[0] * self.image.size[1] * 4
        
        mask_red = self._color_mask >> 24
        mask_green = (self._color_mask >> 16) & 0xff
        mask_blue = (self._color_mask >> 8) & 0xff
        
        bitmask = []
        px_to_ignore = chr(0xff)
        px_to_check = chr(0x00)
        for index in range(0, total_pixels, 4):
            red = ord(raw[index])
            green = ord(raw[index+1])
            blue = ord(raw[index+2])
            if red == mask_red and green == mask_green and blue == mask_blue:
                bitmask.append(px_to_ignore)
            else:
                bitmask.append(px_to_check)

        self._mask_ptr = "".join(bitmask)
        return self._mask_ptr
        
    def crop(self, box):
        '''
        Convenience method for getting a crop of the image it holds, it is
        just a shorthand for holder.image.crop((1,1,20,20))
        '''
        return self.image.crop(box)
    
    @property
    def size(self):
        '''
        Convenience method for getting the size of the image it holds, it is
        just a shorthand for holder.image.size
        '''
        return self.image.size

    @property
    def pixel_count(self):
        '''
        Returns the number of pixels in the image
        '''
        return self.image.size[0] * self.image.size[1]

def _get_exportable_array_ptr(img):
    '''
    Gets a raw data buffer to the pixels in grayscale
    '''
    return img.convert('L').tostring('raw')

def find_image(search_for, search_in):
    '''
    Searches for the given image inside of another image and returns
    a comparison score with the x and y coordinates of the best match.
    The score is the number of matching pixels (the comparison is tolerant and
    not absolute, so the best possible score is img_widht * img_height)
    
    >>> to_search = ImageHolder("self_test\\Test_2.bmp")
    >>> search_in = ImageHolder("self_test\\Test_1.bmp")
    >>> find_image(to_search, search_in)
    (5476, 129, 78)
    '''
    started_at = datetime.now()
    search_for_ptr = search_for.get_ptr()
    search_mask = search_for.get_mask_ptr()
    for_width, for_height = search_for.image.size

    search_in_ptr = search_in.get_ptr()
    in_width, in_height = search_in.image.size
        
    best_x = (ctypes.c_int)(0)
    best_y = (ctypes.c_int)(0)
    score = _IMAGE_DLL.find(ctypes.c_char_p(search_for_ptr),
                            for_width,
                            for_height,
                            ctypes.c_char_p(search_in_ptr),
                            in_width,
                            in_height,
                            ctypes.byref(best_x),
                            ctypes.byref(best_y),
                            ctypes.c_char_p(search_mask))
                            
    ended_at = datetime.now()
    search_took = (ended_at - started_at).seconds
    LOGGER.debug("Find image took %s seconds" % (search_took))
    return (score, best_x.value, best_y.value)


def test_image(search_for, search_in, coord_x, coord_y):
    '''
    Computes a comparison score in the given coordinates
    The function is much faster than actually searching in the screen and
    is intended for quick checks when it is expected that something may
    be in the last coordinates it was previously.
    It is provided for convenience but should rarely be used directy as the
    other functions like wait_for_image_in_screen contains smart logic that
    uses this function
    
    >>> to_search = ImageHolder("self_test\\Test_2.bmp")
    >>> search_in = ImageHolder("self_test\\Test_1.bmp")
    >>> test_image(to_search, search_in, 129, 78)
    (5476, 129, 78)
    '''
    search_for_ptr = search_for.get_ptr()
    search_mask = search_for.get_mask_ptr()
    for_width, for_height = search_for.image.size

    search_in_ptr = search_in.get_ptr()
    in_width, in_height = search_in.image.size

    best_x = (ctypes.c_int)(-coord_x)
    best_y = (ctypes.c_int)(-coord_y)
    score = _IMAGE_DLL.find(ctypes.c_char_p(search_for_ptr),
                           for_width,
                           for_height,
                           ctypes.c_char_p(search_in_ptr),
                           in_width,
                           in_height,
                           ctypes.pointer(best_x),
                           ctypes.pointer(best_y),
                           ctypes.c_char_p(search_mask))
    return (score, best_x.value, best_y.value)
