"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
"""

import pywinauto
import time

def close_it(cls_name='tooltips_class32'):
    wins = pywinauto.findwindows.find_windows(class_name=cls_name)
    for win in wins:
        pywinauto.controls.HwndWrapper.HwndWrapper(win).Close()
        print "Killed one!"

def close_tooltips():
    close_it()
    close_it('CiceroUIWndFrame')
    close_it('ClockTooltipWindow')

while True:
    close_tooltips()
    time.sleep(0.1)
    
