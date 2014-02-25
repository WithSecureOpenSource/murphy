'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Module for simulating mouse and keyboard input
'''
import time
from ctypes import c_ulong, windll, pointer, sizeof
from murphy.user_simulation.local.input import Input, InputUnion, MouseInput

MOUSEEVENTF_LEFTDOWN = 2
MOUSEEVENTF_LEFTUP = 4
MOUSEEVENTF_RIGHTDOWN = 8
MOUSEEVENTF_RIGHTUP = 0x10
MOUSEEVENTF_MIDDLEDOWN = 0x20
MOUSEEVENTF_MIDDLEUP = 0x40

LEFT_BUTTON = 1
MIDDLE_BUTTON = 2
RIGHT_BUTTON = 3

class MouseButton(object):
    '''
    Encapsulates a mouse button functionality
    '''
    def __init__(self, which):
        if which == LEFT_BUTTON:
            self._mouse_down_value = MOUSEEVENTF_LEFTDOWN
            self._mouse_up_value = MOUSEEVENTF_LEFTUP
        elif which == MIDDLE_BUTTON:
            self._mouse_down_value = MOUSEEVENTF_MIDDLEDOWN
            self._mouse_up_value = MOUSEEVENTF_MIDDLEUP
        elif which == RIGHT_BUTTON:
            self._mouse_down_value = MOUSEEVENTF_RIGHTDOWN
            self._mouse_up_value = MOUSEEVENTF_RIGHTUP
    
    def down(self):
        '''
        Simulates pressing the mouse button
        '''
        input_arr = Input * 2
        extra = c_ulong(0)
        ii2_ = InputUnion()
        ii2_.mouse_inp = MouseInput(0,
                                    0,
                                    0,
                                    self._mouse_down_value,
                                    0,
                                    pointer(extra))
        inputs = input_arr(( 0, ii2_ ))
        windll.user32.SendInput(1, pointer(inputs), sizeof(inputs[0]))

    def up(self):
        '''
        Simulates releasing the mouse button
        '''
        input_arr = Input * 2
        extra = c_ulong(0)
        ii2_ = InputUnion()
        ii2_.mouse_inp = MouseInput(0, # pylint: disable=W0201
                                    0,
                                    0,
                                    self._mouse_up_value,
                                    0,
                                    pointer(extra))

        inputs = input_arr(( 0, ii2_ ))
        windll.user32.SendInput(1, pointer(inputs), sizeof(inputs[0]))
    
    def click(self):
        '''
        Simulates a user click (press and release)
        '''
        self.down()
        time.sleep(0.3)
        self.up()
        
        
class Mouse(object):
    '''
    Encapsulation of the local mouse
    '''
    def __init__(self):
        self._left_button = MouseButton(LEFT_BUTTON)
        self._middle_button = MouseButton(MIDDLE_BUTTON)
        self._right_button = MouseButton(RIGHT_BUTTON)
        
    def move(self, coord_x, coord_y):
        '''
        Moves the mouse to the given screen coordinates
        '''
        windll.user32.SetCursorPos(coord_x, coord_y)
    
    def click(self, coord_x, coord_y):
        '''
        Convenience method for setting the mouse position and clicking with
        the left button
        '''
        self.move(coord_x, coord_y)
        self.left.click()
        
    @property
    def left(self):
        '''
        Returns the left button object
        '''
        return self._left_button
       
    @property
    def middle(self):
        '''
        Returns the middle button object
        '''
        return self._middle_button

    @property
    def right(self):
        '''
        Returns the right button object
        '''
        return self._right_button

        


