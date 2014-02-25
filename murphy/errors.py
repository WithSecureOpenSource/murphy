"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Error definitions for possible situations
"""

class MurphyConfused(Exception):
    '''
    This exception is raised when the execution of actions fails due to some
    unexpected error, the errors that raise this exception are supposed to be
    from the modeled application, for example failed to execute a verb, other
    types of errors triggers normal exceptions
    '''
    pass

class UndefinedView(Exception):
    '''
    This exception is raised when an attempt is made to go to an view that
    is not yet defined
    '''
    pass
    
class UndefinedVerb(Exception):
    '''
    This exception is raised when an attempt is made to invoke a verb that
    is not yet defined
    '''
    pass
    
class UnimplementedVerb(Exception):
    '''
    This exception is raised when an attempt is made to invoke a verb that
    is defined but not yet implemented
    '''
    pass
    
class NoRouteFound(Exception):
    '''
    This exception is raised when no path between points can be found
    '''
    pass
    
class UserCancelled(Exception):
    '''
    This exception is raised when the user requests the cancellation of the
    current execution
    '''
    pass
    