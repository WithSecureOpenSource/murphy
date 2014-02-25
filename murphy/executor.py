'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Executor of verbs and basic 'execution' functionality
Supports different execution engines, for example visual, pywinauto, etc
Currently supports only python methods and visual executor
'''
from murphy.errors import (MurphyConfused, UndefinedView, UndefinedVerb,
                           UnimplementedVerb, UserCancelled)
from murphy.visual_executor import VisualExecutor
from murphy.method_executor import MethodExecutor
from murphy.navigator_executor import NavigatorExecutor
from murphy.path_tested import TestedPath, StepState
from murphy import utils

import time, datetime, logging, traceback, os, copy

LOGGER = logging.getLogger('root.' + __name__)
DRIVERS = ['METHOD', 'VISUAL', 'NAVIGATOR']
    
class Executor():
    '''
    An executor is an abstraction of how to execute the basic actions
    in murphy:
    Check if a view passes it's identity check (is_in_view)
    Execute a verb (execute_verb)
    Handle unexpected views (add_interfering_view)
    Reports visited views and executed verbs (get_visits)
    '''
    def __init__(self, default_timeout, img_folder, worker):
        #TODO: driver & execution order should be overridable
        self._worker = worker
        self._traversed = TestedPath()
        self._timeout = default_timeout
        self._interfering_views = dict()
        self._in_interfering_views = False
        self._drivers = dict()
        self._drivers['METHOD'] = MethodExecutor(self._worker.get_views(),
                                                 self._timeout)
        self._drivers['VISUAL'] = VisualExecutor(self._worker.get_views(),
                                                 default_timeout,
                                                 img_folder,
                                                 worker)
        self._drivers['NAVIGATOR'] = NavigatorExecutor(self._worker.get_views(),
                                                       self,
                                                       self._worker.navigator)
        self._predictor = dict()
        self._predicting = []
        if not img_folder is None:
            self._predictor_file = os.path.join(img_folder, '..', 'predictor.json')
            if os.path.isfile(self._predictor_file):
                self._predictor = utils.load_json_object(self._predictor_file)
        else:
            self._predictor_file = None
            
    def add_interefing_views(self, view_name, verb_name):
        '''
        Adds a special handling for the given view, if the given view becomes
        active (by it's own check) the given verb will be executed, it is mainly
        inteded for unexpected events or popups that can be safely ignored
        '''
        self._validate_view_definition(view_name)
        self._validate_verb_definition(view_name, verb_name)
        self._interfering_views[view_name] = verb_name


    def is_in_view(self, view_name, check_interfering = True):
        '''
        Checks if the given view is active (in other words that it's own
        identity check passes)
        It can optionally check if there is an interfering view that may
        confuse the view validation
        '''
        self._validate_view_definition(view_name)
        if check_interfering:
            check_fn = self._check_interfering_views
        else:
            check_fn = None
        
        for driver_name in DRIVERS:
            if driver_name in self._drivers:
                driver = self._drivers[driver_name]
                if driver.view_uses_driver(view_name):
                    return driver.is_in_view(view_name, check_fn)

        raise Exception("View %s does not implement identity" % view_name)
        
    def set_active_view(self, view_name):
        '''
        When a script sets the context into a view this method calls and
        validates that the given view is indeed recognized by it's own
        identity
        '''
        #FIXME: this needs some retry...
        #if not self.is_in_view(view_name):
        #    raise errors.MurphyConfused(("The view %s is not recognized as " +
        #                                 "being active") % view_name)
        step = StepState(view_name, None, TestedPath.PASS, None)
        self._traversed.add_step(step)
                
    def execute_verb(self, view_name, verb_name):
        '''
        Executes the given verb of the given view
        '''
        self._validate_view_definition(view_name)
        self._validate_verb_definition(view_name, verb_name)

        view = self._worker.get_views()[view_name]
        verb = view['verbs'][verb_name]
        params_used = ''
        if 'uses' in verb:
            params_used += 'with params: '
            params = verb['uses']
            available = copy.deepcopy(self._worker.parameters)
            if not type(params) is list:
                params = [params]
            for param in params:
                params_used += "%s=%s " % (param, available[param].pop(0))
        LOGGER.debug("about to execute %s.%s %s" % (view_name,
                                                    verb_name,
                                                    params_used))

        tags = None
        if 'tags' in self._worker.properties:
            if not self._worker.properties['tags'] is None:
                tags = self._worker.properties['tags']
                
        executed = False
        for driver_name in DRIVERS:
            if driver_name in self._drivers:
                driver = self._drivers[driver_name]
                if driver.verb_uses_driver(view_name, verb_name):
                    try:
                        driver.execute_verb(view_name,
                                            verb_name,
                                            self._check_interfering_views,
                                            tags)
                    except MurphyConfused, confusion:
                        step = StepState(view_name, verb_name,
                                         TestedPath.FAIL, str(confusion))
                        self._traversed.add_step(step)
                        LOGGER.warning(str(confusion))
                        self._take_error_snapshot(view_name, verb_name)
                        raise
                    except Exception, unexpected:
                        step = StepState(view_name, verb_name,
                                         TestedPath.ERROR, str(unexpected))
                        self._traversed.add_step(step)
                        LOGGER.error("%s\n%s" % (str(unexpected),
                                     traceback.format_exc()))
                        self._take_error_snapshot(view_name, verb_name)
                        raise
                    executed = True
                    break
        
        if not executed:
            raise Exception("View '%s' does not implement identity" % view_name)
        
        step = StepState(view_name, verb_name, TestedPath.PASS, params_used)
        self._traversed.add_step(step)
            
        #Fade in/out are near 1 second
        #FIXME: remove when predictor is in place
        time.sleep(0.4)
        target = verb['goes to']
        timeout = None
        if 'timeout' in verb:
            timeout = verb['timeout']
        self._validate_destination(target, timeout, view_name)



    @property
    def visual_executor(self):
        '''
        Returns the visual executor object if there is one
        '''
        return self._drivers['VISUAL']

    @property
    def navigator_executor(self):
        '''
        Returns the navigator executor responsible for superview nagivation
        '''
        return self._drivers['NAVIGATOR']
    
    def _validate_view_definition(self, view_name):
        '''
        Validates that the given view is both defined and implemented,
        raise exception if is not
        '''
        if not view_name in self._worker.get_views():
            raise UndefinedView("View '%s' is not defined" % str(view_name))
    
    def _validate_verb_definition(self, view_name, verb_name):
        '''
        Validates that the given verb is defined and implemented,
        raises exception if is not
        '''
        view = self._worker.get_views()[view_name]
        if not verb_name in view['verbs']:
            raise UndefinedVerb(("Verb '%s' in '%s' is not defined yet!"
                                        ) % (verb_name, view_name))
        verb = view['verbs'][verb_name]
        if not 'how' in verb:
            raise UnimplementedVerb(("Verb '%s' in '%s' not fully " +
                                            "implemented, lacks 'how'!"
                                           ) % (verb_name, view_name))
        if not 'goes to' in verb:
            raise UnimplementedVerb(("Verb '%s' in '%s' not fully " +
                                            "implemented, lacks 'goes to'!"
                                           ) % (verb_name, view_name))

                             
    def _check_interfering_views(self):
        '''
        Checks if any of the 'ignorable' views occurs and executes the
        configured action as appropriate
        '''
        LOGGER.debug("Checking interfering views")
        if self._in_interfering_views:
            LOGGER.debug("Checking interfering views, preventing recursion")
            return #avoids recursion
            
        self._in_interfering_views = True
        for view, verb in self._interfering_views.items():
            if self._worker.execution.aborted():
                raise UserCancelled("User cancelled")
            if self.is_in_view(view, False):
                LOGGER.info("Interfering view %s found, acting upon..." % view)
                self.execute_verb(view, verb)
                #FIXME: if dest is nonvalidable ('') bad things happen...
                self._in_interfering_views = False
                return
        self._in_interfering_views = False

    def _validate_destination(self, view_name, timeout, comming_from):
        '''
        Validates that the given view is fine according to it's own identity
        check, considers the '' view as a special unverifiable case.
        Must be called only from execute_verb.
        FIXME: this is wrong, retry must exist for and in visual executor
        but not in method or other executions
        '''
        if view_name == '':
            return

        LOGGER.debug("checking if im in %s" % view_name)
        self._validate_view_definition(view_name)
        if timeout is None:
            timeout = self._timeout
            
        started_at = datetime.datetime.now()

        while True:
            if self._worker.execution.aborted():
                raise UserCancelled("User cancelled")
            try:
                if self.is_in_view(view_name, True):
                    step = StepState(view_name, None, TestedPath.PASS, None)
                    self._traversed.add_step(step)
                    break
            except Exception, unexpected:
                step = StepState(view_name, None, TestedPath.ERROR,
                                 str(unexpected))
                self._traversed.add_step(step)
                LOGGER.error("%s\n%s" % (str(unexpected),
                             traceback.format_exc()))
                raise
            
            ellapsed = (datetime.datetime.now() - started_at).seconds
            if ellapsed > timeout: #fixme: parametrize and propagate
                unexpected = "Cannot recognize view %s" % view_name
                step = StepState(view_name, None, TestedPath.FAIL, unexpected)
                self._traversed.add_step(step)
                LOGGER.warning(unexpected)
                self._take_error_snapshot(view_name)
                raise MurphyConfused(unexpected)

            if ellapsed % 30 == 0:
                LOGGER.info("Giving some breath time (10 seconds)")
                time.sleep(10)
            else:
                time.sleep(1.0)


    def _take_error_snapshot(self, view_name, verb_name=None):
        if verb_name is None:
            error_snapshot = "Failed to find %s in screen.bmp" % view_name
        else:
            error_snapshot = "Failed in view %s verb %s.bmp" % (view_name, verb_name)
        
        if 'error snapshot' in self._worker.properties:
            error_snapshot = self._worker.properties['error snapshot']
        self._worker.input.screen().save(error_snapshot, "BMP")
            
    def reset_trips(self):
        '''
        Clears the path's travelled so far, typical use is when the
        application is being used interactively
        '''
        self._traversed = TestedPath()
    
    def get_visits(self):
        '''
        Returns an array of StepState describing each visited view and
        invoked verb, the array returned is a copy not meant to be altered
        '''
        return self._traversed.get_visits()

    def save_predictions(self):
        '''
        Save predictive timmings for next executions
        '''
        if not self._predictor is None:
            utils.save_json_object(self._predictor, self._predictor_file)
