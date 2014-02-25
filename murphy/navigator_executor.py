'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Module that executes verbs by invoking python methods, the module is not
intended to be called directly, only indirectly thru the executor module
'''
import types, logging
from murphy.navigator import EvaluatorTags

LOGGER = logging.getLogger('root.' + __name__)

class NavigatorExecutor():
    '''
    Executor implementation where verbs are an array of views / verbs to
    navigate
    '''
    def __init__(self, views, executor, navigator):
        self._views = views
        self._executor = executor
        self._navigator = navigator
        self._set_active_view = None

        
    def set_context_setter(self, set_active_view_fn):
        '''
        Ugly but needed, murphy tracks the active view and high level views
        need to restore the active view, so we basically need a pointer to the
        worker :/
        '''
        self._set_active_view = set_active_view_fn

        
    def view_uses_driver(self, view_name): #check synonym of?
        '''
        Returns True if the given view can use the NavigatorExecutor
        As the underlying view will be executed the validation is implicit
        '''
        return 'superview of' in self._views[view_name]['self'].HERE
    
    
    def verb_uses_driver(self, view_name, verb_name):
        '''
        Returns True if the given verb can use the VisualExecutor
        '''
        view = self._views[view_name]
        verb = view['verbs'][verb_name]
        how = verb['how']

        if isinstance(how, types.ListType):
            return True
        else:
            return False
    
    
    def is_in_view(self, view_name, check_interfering_fn): #should call the synonym class validation?
        '''
        The call happens always before in the shadow view of this superview
        So it is not possible to reach this point if the underlying node is not
        actually visible.
        While this is ok, it breaks the api as it can be programatically called
        so we delegate the validation even if it will be done more than once
        '''
        shadow_view = self._views[view_name]['self'].HERE['superview of']
        return self._executor.is_in_view(shadow_view, True)
        
        
    def execute_verb(self, view_name, verb_name, check_interfering_views_fn, tags):
        '''
        Called by executor when the navigator driver is enabled
        '''
        '''
        view = self._views[view_name]
        verb = view['verbs'][verb_name]
        path = [view['self'].HERE['superview of']]
        path += verb['how']
        
        destination = verb['goes to']
        if 'superview of' in self._views[destination]['self'].HERE:
            destination = self._views[destination]['self'].HERE['superview of']
            
        if path[-1] != destination:
            path += [destination]
        
        LOGGER.debug('Superview path requested for %s' % str(path))
        #FIXME: needs tags consideration!
        rules = []
        if not tags is None:
            rules.append(EvaluatorTags(tags))

        path = self._navigator.get_paths_ext(path,
                                             implemented=True,
                                             shortest=True,
                                             custom_filters=rules)
        '''
        path = self._navigator.get_superview_path(view_name, verb_name, tags)
        for view, verb in path: #[0]:
            self._executor.execute_verb(view, verb)
        #must restore context to ensure cotinuity
        self._set_active_view(view_name)