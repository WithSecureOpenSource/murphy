'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Abstract world class, override as appropriate
'''

class World(object):
    '''
    The world as a whole and it's 3 main characteristics for crawling:
    create (init)
    reset (back to initial state)
    dispose
    '''
    def __init__(self):
        #directory where to save related files
        self.output_dir = None
        #array of log file names collected during crawling
        self.event_logs = []
        
    def reset(self):
        '''
        Resets the world to an initial state, dispose any non needed resources
        '''
        pass

    def dispose(self):
        '''
        Call when we're done with it and wont use this world anymore
        '''
        pass
