'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Provides a user simulation thru a vnc connection
This is in early development so some stuff will quite change as when i figure
a good way to deal with the mix of inheritance, composition and so
'''

from murphy.user_simulation import windows_user
from murphy.user_simulation.vnc.vncdotool.vnc_wrapper import VncConnectionProxy

class User(windows_user.WindowsUser):
    '''
    Wraps to an out of process implementation of vncdotool 
    '''
    def __init__(self, host, port, user, password):
        super(User, self).__init__()
        for _ in range(9):
            try:
                self._vnc_proxy = VncConnectionProxy(host, port, user, password)
                self._vnc_proxy.connect()
                return
            except Exception, ex: #pylint: disable=W0703
                print "Connection attempt failed (%s), retrying" % str(ex)
        self._vnc_proxy = VncConnectionProxy(host, port, user, password)
        self._vnc_proxy.connect()
                
        
    @property
    def keyboard(self):
        return self._vnc_proxy.keyboard
        
    @property
    def mouse(self):
        return self._vnc_proxy.mouse
        
    def grab_screen(self):
        return self._vnc_proxy.screen.grab()

    def screen(self):
        return self.grab_screen()
        
    def disconnect(self):
        '''
        Disconnects from the device, it is needed for proper cleanup and
        terminating the local process, dont forget to call!
        '''
        self._vnc_proxy.disconnect()