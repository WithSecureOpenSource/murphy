"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Screen grab utility, PIL grab module has a bug in it that does not capture
properly since it does not use the CAPTUREBLT bit
""" 
from ctypes import c_short, c_int, c_uint32, c_long, c_ulong, Structure
from ctypes import windll, memset, pointer, byref, sizeof
from ctypes import create_string_buffer
from PIL import Image

HORZRES = 8
VERTRES = 10
SRCCOPY = 0xCC0020
DIB_RGB_COLORS = 0
BI_RGB = 0
CAPTUREBLT = 0x40000000

class BITMAPINFOHEADER(Structure): # pylint: disable=R0903
    """As defined in windows API"""
    _fields_ = [
        ('biSize', c_uint32),
        ('biWidth', c_int),
        ('biHeight', c_int),
        ('biPlanes', c_short),
        ('biBitCount', c_short),
        ('biCompression', c_uint32),
        ('biSizeImage', c_uint32),
        ('biXPelsPerMeter', c_long),
        ('biYPelsPerMeter', c_long),
        ('biClrUsed', c_uint32),
        ('biClrImportant', c_uint32)
    ]
    __slots__ = [f[0] for f in _fields_]


class BITMAPINFO(Structure): # pylint: disable=R0903
    """As defined in windows API"""
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', c_ulong * 3)
    ]

def grab():
    """Grabs the content of the screen and returns an Image object"""
    gdi32 = windll.gdi32
    user32 = windll.user32
    
    screen_dc = user32.GetDC(0)
    if not screen_dc:
        raise Exception("Failed to get screen dc")
    
    mem_dc = gdi32.CreateCompatibleDC(screen_dc)
    if not mem_dc:
        user32.ReleaseDC(0, screen_dc)
        raise Exception("Failed to create compatible dc")
    
    width = gdi32.GetDeviceCaps(screen_dc, HORZRES)
    height = gdi32.GetDeviceCaps(screen_dc, VERTRES)
    bitmap = gdi32.CreateCompatibleBitmap(screen_dc, width, height)
    if not bitmap:
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(0, screen_dc)
        raise Exception("Failed to create bitmap")


    #sel_obj_ret = 
    gdi32.SelectObject(mem_dc, bitmap)
    bitblt_ret = gdi32.BitBlt(mem_dc, 0, 0, width, height, screen_dc, 0, 0,
                              CAPTUREBLT + SRCCOPY)
    if not bitblt_ret:
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(0, screen_dc)
        raise Exception("Bitblt operation failed")        
        
    bmi = BITMAPINFO()
    memset(byref(bmi), 0x00, sizeof(bmi))
    bmi.bmiHeader.biSize         = sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth        = width
    bmi.bmiHeader.biHeight       = height
    bmi.bmiHeader.biBitCount     = 32
    bmi.bmiHeader.biPlanes       = 1
    bmi.bmiHeader.biCompression  = BI_RGB
    bmi.bmiHeader.biSizeImage    = 4 * width * height

    pb_bits = create_string_buffer(width * height * 4)

    get_dib_ret = gdi32.GetDIBits(mem_dc, bitmap, 0, height,
                           byref(pb_bits),
                           pointer(bmi),
                           DIB_RGB_COLORS)

    if get_dib_ret != height:
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(0, screen_dc)
        raise Exception("GetDIBits operation failed")
        
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(mem_dc)
    user32.ReleaseDC(0, screen_dc)

    img = Image.fromstring("RGB", (width, height), pb_bits, 'raw', 'BGRX', 0,
                           -1)
    return img#.transpose(Image.FLIP_TOP_BOTTOM)

#Example usage:
#img = grab()
#img.save("test1.bmp", "BMP")
