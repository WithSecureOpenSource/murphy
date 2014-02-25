'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Abstraction of what an end user can do from a test automation point of view.
Encapsulates keyboard, screen grab and mouse handling in an appropriate
abstraction, the underlying implementation can be either a local simulation
of keyboard, mouse and screen capture or it can be actually implemented thru
a vnc connection or other virtualization or remote desktop.

There are a set of extended methods that are to be used from tools like screen
scrapers and model extraction.
'''
import time, datetime

from model_extraction.image2 import Image2
from murphy.user_simulation import helpers

class UserAutomation(object):
    '''
    Base class that exposes the core interaction a user can do with a device.
    Derive and override with specialized implementations
    '''
    
    def __init__(self):
        pass
        
        
    @property
    def keyboard(self):
        '''
        Returns a keyboard object abstraction
        '''
        pass
        
        
    @property
    def mouse(self):
        '''
        Returns a mouse object abstraction
        '''
        pass
        
        
    def grab_screen(self):
        '''
        Returns a snapshot of the current screen as seen by the end user in
        a PIL Image object
        '''
        pass

    
    # High level functionality built from primitives
    
    def wait_stable_screen(self, seconds_of_stability=3):
        '''
        Waits for the screen to finish updates, this includes detecting
        applications that are doing some processing and have some sort of
        animated progress indicator and so.
        Will return once the screen has not changed for a small amount of time,
        if such time was not enough then it is most likely that the application
        is not responsive enough for the end user experience, like for example
        a long transition from one dialog to another.
        '''
        helpers.wait_stable_screen(self.grab_screen, seconds_of_stability)

    
    def wait(self, element, max_wait=60, retry_every=0.3):
        '''
        Waits for the given UI element to be visible, returns the bounding
        coordinates of the elements if found, raises ValueError if not.
        '''
        started_at = datetime.datetime.now()
        while True:
            screen = Image2(image=self.grab_screen())
            result = element.find_in(screen)
            if result:
                return result
            now = datetime.datetime.now()
            if (now - started_at).seconds > max_wait:
                raise ValueError("Element not found in screen")
            time.sleep(retry_every)
            
    
    def click(self, element, max_wait=0, retry_every=0.3):
        '''
        Clicks in the center of the given element, will check first if element
        is in screen and fail if it is not.
        Use click(element, max_wait=60) for wait and synchronized clicks.
        max_wait 0 will click if visible and fail if is not visible
        '''
        found = self.wait(element, max_wait, retry_every)
        if found:
            center_x  = found[0] + ((found[2] - found[0]) / 2)
            center_y  = found[1] + ((found[3] - found[1]) / 2)
            self.mouse.move(center_x, center_y)
            self.mouse.click()
        else:
            raise ValueError("Element not found in screen")
        
        
    # The following methods are optional and not meant to be used for normal
    # tests, they are conventient methods for test generation and model
    # extraction tools.
    # As they're NOT intended to be used from test scripts, they may very much
    # go away to a different class in the future, so dont use them, or fix your
    # code when they go away
        
    def get_current_cursor(self):
        '''
        Returns the current cursor as the user sees it in the screen values can
        be 'normal', 'text', 'link' or 'other'
        '''
        return None
        
        
    def get_current_window_title(self):
        '''
        Returns the title of the active window
        '''
        return ''
        
        
    def get_active_window_rect(self):
        '''
        Returns a 4-tuple with the coordinates of the rectangle of the active
        window
        '''
        return None
        
