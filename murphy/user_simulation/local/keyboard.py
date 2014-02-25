'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Module that encapsulates user keyboard inputs
For now it only supports us layout
'''
from ctypes import c_ulong, windll, pointer, sizeof
from murphy.user_simulation.local.input import Input, InputUnion, KeyBdInput


KEYEVENTF_EXTENDEDKEY = 1
KEYEVENTF_KEYUP = 2
KEYEVENTF_SCANCODE = 8

US_SCAN_CODES = {'a': 0x1e, 'b': 0x30, 'c': 0x2e, 'd': 0x20, 'e': 0x12,
                 'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
                 'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
                 'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1f, 't': 0x14,
                 'u': 0x16, 'v': 0x2f, 'w': 0x11, 'x': 0x2d, 'y': 0x15,
                 'z': 0x2c, '-': 0x0c, '+': 0x4e, '\n': 0x1c, '1': 0x02,
                 '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06, '6': 0x07,
                 '7': 0x08, '8': 0x09, '9': 0x0a, '0': 0x0b, ' ': 0x39,
                 '{': 0x7d, '}': 0x5d, '.': 0x34, '/': 0x35,
                 'right': 0x4d, 'down': 0x50, 'enter': 0x1c,
                 'shift': 0x2a, 'left shift': 0x2a,
                 'escape': 0x01, 'esc': 0x01,
                 'control': 0x1d, 'ctrl': 0x1d, 'home': 0x6e,
                 'alt': 0x38, 'tab': 0x0f, 'windows': 0x5b}

US_EXTENDED_SCAN_CODES = ['windows', 'home']
US_COMBINED_SCAN_CODES = {'_': '{+left shift}-{-left shift}',
                          '@': '{+left shift}2{-left shift}'
                         }

class Keyboard(object):
    '''
    Class that models the keyboard simulation, parameters are normally the
    character (not the scan code) to press or special keys by their name, for
    example
    keyboard.type("A")
    keyboard.type("tab")
    keyboard.down("control")
    keyboard.type("c")
    keyboard.up("control")
    
    The special method 'enters' accept a special sublanguage, see the method
    help
    
    There's a helper method enters_in_field that appends the control + a to
    clear existing content before actually entr the user input
    '''
    def __init__(self):
        self._scancodes = US_SCAN_CODES
        self._extended_scancodes = US_EXTENDED_SCAN_CODES
        self._combined_scancodes = US_COMBINED_SCAN_CODES
        
    def _get_scancode(self, key):
        '''
        Returns the scancode of the given key
        '''
        key = key.lower()
        if not key in self._scancodes:
            raise ValueError('Key not found in the scancode table: %s' % key)
        return self._scancodes[key]
            
    def down(self, key, override=None):
        '''
        Holds down the given key
        '''
        if key != key.lower() and len(key) == 1:
            use_shift = True
            self.down('left shift')
        else:
            use_shift = False

        key_code = self._get_scancode(key)
        
        if override:
            key_code = override

        if key in self._extended_scancodes:
            is_extended = KEYEVENTF_EXTENDEDKEY
        else:
            is_extended = 0
            
        input_arr = Input * 1
        extra = c_ulong(0)
        ii_ = InputUnion()
        ii_.keyb_inp = KeyBdInput(0,
                                  key_code,
                                  is_extended + KEYEVENTF_SCANCODE,
                                  0,
                                  pointer(extra))
        inputs = input_arr( ( 1, ii_ ) )
        windll.user32.SendInput(1, pointer(inputs), sizeof(inputs[0]))
    
        if use_shift:
            self.up('left shift')
        
        
    def up(self, key, override=None):
        '''
        Releases the given key
        '''
        key_code = self._get_scancode(key)
        
        if override:
            key_code = override

        if key in self._extended_scancodes:
            is_extended = KEYEVENTF_EXTENDEDKEY
        else:
            is_extended = 0
        input_arr = Input * 1
        extra = c_ulong(0)
        ii_ = InputUnion()
        ii_.keyb_inp = KeyBdInput(0,
                                  key_code,
                                  is_extended + 
                                    KEYEVENTF_KEYUP + 
                                    KEYEVENTF_SCANCODE,
                                  0,
                                  pointer(extra))

        inputs = input_arr(( 1, ii_ ))
        windll.user32.SendInput(1, pointer(inputs), sizeof(inputs[0]))
        
        
    def type(self, key):
        '''
        Types the given key, same as down(key) followed by up(key)
        '''
        if key in self._combined_scancodes:
            self.enters(self._combined_scancodes[key])
        else:
            self.down(key)
            self.up(key)


    def enters(self, text):
        '''
        Method accepts letters and special keys but special keys
        have to be bracked, for example:
        keyboard.enters('12B{tab}3{+left shift}a{-left shift}')
        keyboard.enters('{+windows}m{-windows}')
        + holds down a key
        - releases a key
        for typing brackets brack them as:
        keyboard.type('{{}bracked{}}')
        '''
        
        bracked_key = False
        enclosed = ''
        
        #miniparser, no need to overcomplicate it more than this
        while len(text) > 0:
            char = text[0]
            text = text[1:]
            if char == '{':
                if bracked_key == False:
                    bracked_key = True
                else:
                    enclosed += char
            elif char == '}':
                if bracked_key == True:
                    if len(enclosed) > 0:
                        if enclosed[0] == '+':
                            self.down(enclosed[1:])
                        elif enclosed[0] == '-':
                            self.up(enclosed[1:])
                        else:
                            self.type(enclosed)
                        enclosed = ''
                        bracked_key = False
                    else:
                        enclosed += char
                else:
                    enclosed += char
            else:
                if bracked_key == True:
                    enclosed += char
                else:
                    self.type(char)
                    
        if bracked_key == True:
            raise ValueError('Unbalanced brackets in the input: %s' % text)
            
    def enters_in_field(self, text):
        '''
        Adds a cltr+a (select all) to the input so any existing value is
        replaced with the given one
        '''
        self.enters('{+control}a{-control}' + text)