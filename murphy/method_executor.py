'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Module that executes verbs by invoking python methods, the module is not
intended to be called directly, only indirectly thru the executor module
'''
import types

class MethodExecutor():
    '''
    Executor implementation where verbs are python methods
    '''
    def __init__(self, views, default_timeout):
        self._views = views
        self._timeout = default_timeout

        
    def view_uses_driver(self, view_name):
        '''
        Returns True if the given view can use the VisualExecutor
        '''
        if 'validation' in self._views[view_name]['self'].HERE:
            return True
        else:
            return False
    
    
    def verb_uses_driver(self, view_name, verb_name):
        '''
        Returns True if the given verb can use the VisualExecutor
        '''
        view = self._views[view_name]
        verb = view['verbs'][verb_name]
        how = verb['how']

        if isinstance(how, types.FunctionType):
            return True
        else:
            return False
    
    
    def is_in_view(self, view_name, check_interfering_fn):
        '''
        Validates if the current view is active or not
        '''
        how = self._views[view_name]['self'].HERE['validation']
        return how.__call__()

        
    def execute_verb(self, view_name, verb_name, check_interfering_views_fn, tags):
        '''
        Called by executor when the method driver is enabled
        '''
        view = self._views[view_name]
        verb = view['verbs'][verb_name]
        how = verb['how']
        how.__call__()
        