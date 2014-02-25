'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Wraps an image object and adds searching capabilities
'''
import ctypes, os
_IMAGE_DLL = ctypes.WinDLL(os.path.dirname(__file__) + '/img_murphy.dll')

from PIL import Image, ImageChops

class Image2(object):
    '''
    An Image2 object holds a PIL image and provides image search capabilities.
    The image where searches are performed is passed in the constructor and a
    copy of it is stored internally (to ensure immutability)
    '''
    def __init__(self, image=None, file_name=None, color_mask=None,
      tolerance=None, hint=None):
        if image and file_name:
            raise ValueError("Use either file name or image, not both")
        
        if image:
            self._image = image.copy()
        elif file_name:
            self._image = Image.open(file_name)
        else:
            raise ValueError("Use file_name or image")
            
        self._color_mask = color_mask
        self._image_ptr = None
        self._mask_ptr = None
        self._tolerance = tolerance
        self._search_hint = hint
        self._search_hint_image = None
        self.file_name = file_name
        
    
    @property
    def image(self):
        '''
        Returns a copy of the underlying wrapped image
        '''
        return self._image.copy()
        
        
    @property
    def color_mask(self):
        '''
        Returns the color mask of this image
        '''
        return self._color_mask
        

    @property
    def size(self):
        '''
        Returns a tuple with the size of the image as (width, height)
        '''
        return self._image.size
        
        
    def _find_by_hint(self, image, tolerance):
        '''
        Searches by using a small subarea instead of the whole thing, it is
        much faster but requires extra caution as the hint must be 'unique'
        and carefully considered.
        '''
        if image._search_hint_image is None:                           # pylint: disable=W0212,C0301
            hint = Image2(image=image._image.crop(image._search_hint), # pylint: disable=W0212,C0301
                          color_mask=image._color_mask,                # pylint: disable=W0212,C0301
                          tolerance=image._tolerance)                  # pylint: disable=W0212,C0301
            image._search_hint_image = hint # pylint: disable=W0212
        
        found, x_coord, y_coord = self.find(image._search_hint_image,  # pylint: disable=W0212,C0301
                                            tolerance)
        x_coord -= image._search_hint[0] # pylint: disable=W0212
        y_coord -= image._search_hint[1] # pylint: disable=W0212
        
        return self.test(image, x_coord, y_coord, tolerance)

        
    def find(self, image, tolerance=None):
        '''
        Finds the given image inside this image, returns the best match, x and
        y coordinates.
        The tolerance to be used is the one in the passed image, can be
        overriden by specifying a different tolerance, if no tolerance is
        specified then a perfect match is expected
        '''
        if tolerance is None:
            tolerance = image._tolerance # pylint: disable=W0212
        if tolerance is None:
            tolerance = 0.99999

        if image._search_hint:  # pylint: disable=W0212
            return self._find_by_hint(image, tolerance)
            
        search_for_ptr = image._get_image_ptr()   # pylint: disable=W0212
        search_mask = image._get_mask_ptr()       # pylint: disable=W0212
        for_width, for_height = image._image.size # pylint: disable=W0212

        search_in_ptr = self._get_image_ptr()
        in_width, in_height = self._image.size
            
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
                                
        pixel_count = image._image.size[0] * image._image.size[1] # pylint: disable=W0212,C0301
        similarity = float(score) / float(pixel_count)
            
        return (similarity >= tolerance, best_x.value, best_y.value)
    
        
    def find_best_match(self, image):
        '''
        Finds the given image inside this image, returns the best match score,
        x and y coordinates
        '''
        search_for_ptr = image._get_image_ptr()   # pylint: disable=W0212
        search_mask = image._get_mask_ptr()       # pylint: disable=W0212
        for_width, for_height = image._image.size # pylint: disable=W0212

        search_in_ptr = self._get_image_ptr()
        in_width, in_height = self._image.size
            
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
                                
        pixel_count = image._image.size[0] * image._image.size[1] # pylint: disable=W0212,C0301
            
        return (score, best_x.value, best_y.value)


    def find_all(self, image, tolerance=None):
        '''
        Finds all the occurrences of the given image inside this image, returns
        an array of rects for each match
        '''
        pil_image = self._image.copy()
        results = []
        while True:
            search_in = Image2(image=pil_image)
            found, x_coord, y_coord = search_in.find(image, tolerance)
            if found:
                results.append((x_coord,
                                y_coord,
                                x_coord + image._image.size[0],  # pylint: disable=W0212,C0301
                                y_coord + image._image.size[1])) # pylint: disable=W0212,C0301
                pil_image.paste((0, 0, 0, 0), results[-1])
            else:
                break
                
        return results
        

    def test(self, image, coord_x, coord_y, tolerance=None):
        '''
        Tests if the given image is located at the given coordinates, the
        tolerance used is the one in image, but can be overriden
        '''
        
        if tolerance is None:
            tolerance = image._tolerance
        if tolerance is None:
            tolerance = 0.99999
            
        search_for_ptr = image._get_image_ptr()   # pylint: disable=W0212
        search_mask = image._get_mask_ptr()       # pylint: disable=W0212
        for_width, for_height = image._image.size # pylint: disable=W0212

        search_in_ptr = self._get_image_ptr()
        in_width, in_height = self._image.size

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
                               
        pixel_count = image._image.size[0] * image._image.size[1] # pylint: disable=W0212,C0301
        similarity = float(score) / float(pixel_count)
        
        return (similarity >= tolerance, best_x.value, best_y.value)

    
    def difference(self, image, exclude_rects=None):
        '''
        Returns the bounding box rect that differs between this and the given
        image. Note that both images must have the same size, if images are
        equal it returns None
        '''
        if exclude_rects:
            img1 = self.image
            img2 = image.image
            black = (0, 0, 0, 0)
            for rect in exclude_rects:
                img1.paste(black, (rect[0], rect[1], rect[2]+1, rect[3]+1))
                img2.paste(black, (rect[0], rect[1], rect[2]+1, rect[3]+1))

            return Image2(image=img1).difference(Image2(image=img2))
        
        if self == image:
            return None
            
        diff = ImageChops.difference(self._image, image._image) # pylint: disable=W0212,C0301
        area = diff.getbbox()
        if area:
            return (area[0], area[1], area[2]-1, area[3]-1)
        else:
            return None
        
        
    def __eq__(self, other):
        if self._image.size != other._image.size: # pylint: disable=W0212
            return False
        else:
            return self.test(other, 0, 0)[0]

            
    def __ne__(self, other):
        return not self == other
        

    def _get_image_ptr(self):
        '''
        Returns a catched copy if the raw data converted to grayscale
        '''
        if not self._image_ptr:
            self._image_ptr = self._image.convert('L').tostring('raw')
        return self._image_ptr

        
    def _get_mask_ptr(self):
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
            
        raw = self._image.convert('RGBX').tostring('raw')
        total_pixels = self._image.size[0] * self._image.size[1] * 4
        
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
        
        
        
    
    