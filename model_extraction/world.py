'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Abstract world class, override as appropriate
'''

class World(object):
    
    def __init__(self):
        pass
        
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
