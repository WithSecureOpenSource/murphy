'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Needed imports from windows for simulating user input
'''

from ctypes import c_short, c_ushort, c_ulong, c_long
from ctypes import Union, Structure, POINTER

PUL = POINTER(c_ulong)

class KeyBdInput(Structure): # pylint: disable=R0903
    """Structure as defined in windows API"""
    _fields_ = [("wVk", c_ushort),
                ("wScan", c_ushort),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(Structure): # pylint: disable=R0903
    """Structure as defined in windows API"""
    _fields_ = [("uMsg", c_ulong),
                ("wParamL", c_short),
                ("wParamH", c_ushort)]

class MouseInput(Structure): # pylint: disable=R0903
    """Structure as defined in windows API"""
    _fields_ = [("dx", c_long),
                ("dy", c_long),
                ("mouseData", c_ulong),
                ("dwFlags", c_ulong),
                ("time",c_ulong),
                ("dwExtraInfo", PUL)]

class InputUnion(Union): # pylint: disable=R0903
    """Structure as defined in windows API"""
    _fields_ = [("keyb_inp", KeyBdInput),
                ("mouse_inp", MouseInput),
                ("hi", HardwareInput)]

class Input(Structure): # pylint: disable=R0903
    """Structure as defined in windows API"""
    _fields_ = [("type", c_ulong),
                ("ii", InputUnion)]

class POINT(Structure): # pylint: disable=R0903
    """Structure as defined in windows API"""
    _fields_ = [("x", c_ulong),
                ("y", c_ulong)]