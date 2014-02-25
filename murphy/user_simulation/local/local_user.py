'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Basic implementation of a user simulation that runs on the client machine, i/e
locally where the test is being run
Implementation is windows specific and may be refactored in the future in
a /windows dir or so
'''
import ctypes

from murphy.user_simulation import user_automation
from murphy.user_simulation.local.mouse import Mouse
from murphy.user_simulation.local.keyboard import Keyboard
from murphy.user_simulation.local import screen_grab


class POINT(ctypes.Structure):  # pylint: disable=R0903
    '''Structure as defined in windows API'''
    _fields_ = [
        ('x', ctypes.c_long),
        ('y', ctypes.c_long),
    ]

    
class CURSORINFO(ctypes.Structure):  # pylint: disable=R0903
    '''Structure as defined in windows API'''
    _fields_ = [("cbSize", ctypes.c_ulong),
                ("flags", ctypes.c_ulong),
                ("hCursor", ctypes.c_void_p),
                ("ptScreenPos", POINT)]

                
class RECT(ctypes.Structure):  # pylint: disable=R0903
    '''Structure as defined in windows API'''
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]
                

IDC_ARROW = 32512
IDC_HAND = 32649
IDC_IBEAM = 32513

class User(user_automation.UserAutomation):
    '''
    Full implementation of a local user automation, including extended methods
    for model extraction tools, does not correctly work with all keyboard
    layouts
    '''
    def __init__(self):
        super(User, self).__init__()
        self._mouse = Mouse()
        self._keyboard = Keyboard()
        self._arrow_cursor = ctypes.windll.user32.LoadCursorA(None, IDC_ARROW)
        self._hand_cursor = ctypes.windll.user32.LoadCursorA(None, IDC_HAND)
        self._text_cursor = ctypes.windll.user32.LoadCursorA(None, IDC_IBEAM)
    
    @property
    def keyboard(self):
        return self._keyboard
        
        
    @property
    def mouse(self):
        return self._mouse
        
        
    def grab_screen(self):
        return screen_grab.grab()
        
    
    # You wont use the methods below will you? they are not intended for test
    # scripts but for test tools, if you do, be prepare they may disappear in
    # the future and moved to some extended classes somewhere else
   
    def get_current_cursor(self):
        '''
        Returns the current cursor as the user sees it in the screen
        '''
        cursor_info = CURSORINFO()
        print "cbsize is " + str(cursor_info.cbSize)
        cursor_info.cbSize = ctypes.sizeof(CURSORINFO)
        rval = ctypes.windll.user32.GetCursorInfo(ctypes.pointer(cursor_info))
        if rval == 0:
            return None
        else:
            if cursor_info.hCursor == self._arrow_cursor:
                return 'normal'
            elif cursor_info.hCursor == self._text_cursor:
                return 'text'
            elif cursor_info.hCursor == self._hand_cursor:
                return 'link'
            else:
                return 'other'
        
        
    def get_current_window_title(self):
        '''
        Returns the title of the active window
        '''
        buff = ctypes.create_string_buffer(1024)
        hwin = ctypes.windll.user32.GetForegroundWindow()
        ret_len = ctypes.windll.user32.GetWindowTextA(hwin,
                                                      buff,
                                                      ctypes.sizeof(buff))
        if ret_len == 0:
            return None
        else:
            return buff.value
            
    
    def get_active_window_rect(self):
        '''
        Returns a 4-tuple with the coordinates of the rectangle of the active
        window
        '''
        rect = RECT()
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        result = ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
        if result == 0:
            return None
        else:
            return (rect.left, rect.top, rect.right, rect.bottom)


def test():
    '''
    Simple unit test
    '''
    import time
    user = User()
    user.mouse.move(0, 0)
    time.sleep(2)
    user.mouse.move(1, 1)
    user.keyboard.enters('{+ctrl}{esc}{-ctrl}hi there')
    screen = user.grab_screen()
    print "Got screen %s" % str(screen)
    print user.get_current_cursor()

if __name__ == '__main__':
    test()
    