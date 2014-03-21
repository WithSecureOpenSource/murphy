'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details
'''
import os, shutil
from model_extraction.world import World

class VmWorld(World):
    '''
    Encapsulates a virtual machine as a world for crawling
    '''

    def __init__(self, allocator):
        super(VmWorld, self).__init__()
        self._allocator = allocator
        self._machine = None
        #Used during scraping to keep track of last known screen, it is the
        #last image before performing an edge, each edge to be performed saves
        #the current screenshot here
        self.last_screen = None
        self._live_broadcast = None

    @property
    def live_broadcast(self):
        return self._live_broadcast

    @live_broadcast.setter
    def live_broadcast(self, filename):
        self._live_broadcast = filename

    def reset(self):
        '''
        Initializes or reinitializes the virtual machine to the starting state
        '''
        if self._machine:
            self.dispose()

        if self._live_broadcast:
            if os.path.isfile(self._live_broadcast):
                try:
                    os.remove(self._live_broadcast)
                except Exception, ex:
                    print "problem cleaning broadcasted image: %s" % str(ex)

        output = self.output_dir + '/misc'
        if os.path.exists(output) == False:
            os.makedirs(output)
        self._machine = self._allocator()
        self._machine.output_dir = output
        self._machine.live_broadcast = self._live_broadcast
        self._machine.prepare()

    def dispose(self):
        '''
        Deallocates the virtual machine if it was allocated
        '''
        if self._machine:
            log = self._machine.deallocate()
            if log:
                self.event_logs.append(log)
            self._machine = None

    @property
    def machine(self):
        '''
        Returns the current virtual machine wrapper object, do not cache this
        value as it is regenerated when the world is reset
        '''
        return self._machine
