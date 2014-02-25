'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Murphy, a humble attempt to do kind of model base testing
'''

from murphy.errors import MurphyConfused
from murphy.executor import Executor
from murphy.navigator import Navigator, EvaluatorTags
from murphy.graphs import Graphs
from murphy.utils import is_valid_module, list_verbs, load_json_object
import sys, time, os

import logging
from murphy.user_simulation.vnc.vnc_user import User as VncUser
from murphy.user_simulation.local.local_user import User as LocalUser
LOGGER = logging.getLogger('root.' + __name__)

#be sure it ends in backslash!
WORKING_FOLDER = 'c:\\murphy\\'
GLOBAL_TIMEOUT = 180

if not os.path.exists(WORKING_FOLDER):
    os.makedirs(WORKING_FOLDER)

class UserSimulation(object):
    '''
    Abstraction of the user simulation, it can at the moment simulate a
    local windows user or a vnc user
    FIXME: replace with user_simulation package
    '''
    def __init__(self, mouse=None, keyboard=None, screen=None):
        self.mouse = mouse
        self.keyboard = keyboard
        self.screen = screen

    @staticmethod
    def createLocalUserSimulation():
        '''
        Creates a user simulation for local execution
        '''
        local_user = UserSimulation()
        user = LocalUser()
        local_user.mouse = user.mouse
        local_user.keyboard = user.keyboard
        local_user.screen = user.grab_screen
        return local_user

    @staticmethod
    def createVncUserSimulation(host, port, user, password):
        '''
        Creates a simulated user that will act thru a vnc connection
        '''
        vnc_user = UserSimulation()
        vnc_connection = VncUser(host, port, user, password)
        vnc_user.mouse = vnc_connection.mouse
        vnc_user.keyboard = vnc_connection.keyboard
        vnc_user.screen = vnc_connection.screen.grab
        
        return vnc_user, vnc_connection


class Execution(object):
    '''
    Encapsulates the execution parameters, properties and state.
    Execution cancellation can be requested by invoking the abort method
    '''
    def __init__(self, parameters=None, properties=None):
        if parameters:
            self._parameters = parameters
        else:
            self._parameters = dict()
        if properties:
            self._properties = properties
        else:
            self._properties = dict()
        self._abort = False
    
    
    @property
    def parameters(self):
        '''
        Returns the parameters for this execution
        '''
        return self._parameters
        
        
    @property
    def properties(self):
        '''
        Returns the properties for this execution
        '''
        return self._properties
    
    
    def abort(self):
        '''
        Request to abort this execution
        '''
        self._abort = True
        
        
    def aborted(self):
        '''
        Returns True if this execution was requested to be aborted
        '''
        return self._abort
        
        
class Worker(object):
    '''
    The worker class represents an actual tester, it provides the basic
    methods for interacting with the modeled application.
    Before anything, you must construct a worker object and load the
    application definition, for example:
    
    >>> worker = Worker()
    >>> worker.load_application('self_test.app1',
    ... r'murphy\\self_test\\app1\\app1.json')
    >>> worker.In("Test View 1").Do("Go to view 2") # doctest: +ELLIPSIS
    <murphy.Worker instance at 0x...>
    '''

    #FIXME: worker initialization must contain all relevant construction
    #parameters: the json file & execution parameters
    def __init__(self, user_simulation=None, model=None, images_dir=None):
        self._views = dict()
        self._active_view = None
        self._executor = None
        self._navigator = None
        self._graphs = None
        self._parameters = dict()
        self._properties = dict()
        self._execution = Execution()
        if user_simulation is None:
            self._user_simulation = UserSimulation.createLocalUserSimulation()
        else:
            self._user_simulation = user_simulation
        
        #FIXME: will be removed once load_application is removed, parameter
        #will be mandatory
        if model:
            self._load_modules(model, images_dir)

    def _load_modules(self, model, images_dir):
        '''
        Loads the model and create the internal objects accordingly
        '''
        module_list = model['modules']
        package = model['namespace']
        if images_dir:
            images_folder = images_dir
        else:
            images_folder = model['images dir']
        
        for i in range(len(module_list)):
            name = package + "." + module_list[i]
            mod = __import__(name)
            mod = sys.modules[name]
            if is_valid_module(mod):
                if mod.HERE['desc'] in self._views:
                    raise Exception("More than one module contains the same " +
                                    "description: " + mod.HERE['desc'])
                module_dict = dict()
                module_dict['self'] = mod
                module_dict['verbs'] = list_verbs(mod)
                self._views[mod.HERE['desc']] = module_dict
                mod.worker = self
                mod.WORKER = self

        self._navigator = Navigator(self._views)
        #WARN: executor uses navigator so it must be created before
        #this needs a bit of refactoring
        self._executor = Executor(model['global timeout'],
                                  images_folder,
                                  self)
        self._executor.navigator_executor.set_context_setter(self.In)
        self._graphs = Graphs(self._views)

     
    #Deprecated: will be removed, use model parameter in constructor
    def load_application(self, package, file_name, img_folder=None):
        '''
        Loads a modeled application in the given package space.
        The file that describes the application is a simple json array that
        lists the modules that models each view of the application, for example
        ["view1", "view2", "view3", "view4"]
        The package parameter is the package space where it will be loaded,
        usually follows the directory structure relative from the murphy
        directory.
        Example:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app5',
        ... r'murphy\\self_test\\app5\\app5.json')
        '''
        model = load_json_object(file_name)
        module_list = model
        if type(module_list) is dict:
            module_list = module_list['modules']

        for i in range(len(module_list)):
            try:
                name = package + "." + module_list[i]
                mod = __import__(name)
                mod = sys.modules[name]
                if is_valid_module(mod):
                    if mod.HERE['desc'] in self._views:
                        raise Exception("More than one module contains the "
                                        "same description: " + mod.HERE['desc'])
                    module_dict = dict()
                    module_dict['self'] = mod
                    module_dict['verbs'] = list_verbs(mod)
                    self._views[mod.HERE['desc']] = module_dict
                    mod.worker = self
                    mod.WORKER = self
            except Exception:
                print "Unexpected error while loading module %s" % name
                raise
            
        self._navigator = Navigator(self._views)
        general_timeout = GLOBAL_TIMEOUT
        if type(model) is dict:
            if 'global timeout' in model:
                general_timeout = model['global timeout']
        self._executor = Executor(general_timeout,
                                  img_folder,
                                  self)
        self._executor.navigator_executor.set_context_setter(self.In)
        self._graphs = Graphs(self._views)

    def In(self, view_name):
        '''
        Tells the worker what the active view is and where the next verb is
        going to be executed, for example if a view is a window it is like
        telling a user 'you are now in the login dialog'
        Any verb invocation like Do, Then or GoTo uses the given view as the
        starting point.
        It is NOT neccessary to tell the active view for every command, once
        the initial view is set it will change internally accordingly to the
        verbs executed.
        Examples:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app1',
        ... r'murphy\\self_test\\app1\\app1.json')
        >>> worker.In("Test View 1").Do("Go to view 2") # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        >>> worker.Then("Go to view 1") # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        
        @return: murphy.worker.Worker
        '''
        LOGGER.info("Setting context to view %s" % view_name)
        #FIXME: setting the view should trigger identity validation in executor
        #also add the view as visited accordingly
        if not view_name in self._views:
            raise Exception("Requested view '%s' is not defined" % view_name)
        self._executor.set_active_view(view_name)
        self._active_view = view_name
        #raise Exception("testing")
        return self
        
    def Do(self, verb_name):
        '''
        Executes the given verb in the active view
        May throw an exception if:
        The active view is unknown
        The verb is not defined for the active view
        The verb is defined but not implemented
        Examples:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app1',
        ... r'murphy\\self_test\\app1\\app1.json')
        >>> worker.In("Test View 1").Do("Go to view 2") # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        >>> worker.Do("Go to view 1") # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        
        Returns the worker object for method chaining.
        '''
        LOGGER.info("Doing %s in %s" % (verb_name, self._active_view))
        if self._active_view is None:
            raise Exception(("Can't execute verb '%s' without a view (" +
                             "(In method should be called first)") % verb_name)
        self._executor.execute_verb(self._active_view, verb_name)
        old_view = self._active_view
        verbs = self._views[self._active_view]['verbs']
        self._active_view = verbs[verb_name]['goes to']
        LOGGER.info(("Done %s in %s, active view now " +
                     "is %s") % (verb_name, old_view, self._active_view))
        
        return self

    def Then(self, verb_name):
        '''
        Synonym of the Do method, usefull for better semantics while
        chaining methods, for example you can do:
        In("Installation").Do("Install").Then("Accept license").Then("Close")
        Returns the worker object for method chaining.
        '''
        return self.Do(verb_name)

    def GoTo(self, view):
        '''
        Navigates from the active view to the given view, the destination
        view does not have to be contiguous to the active view so there can
        be several views separating the active view from the target view.
        The path choosen is random and unpredictable.
        Examples:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app5',
        ... r'murphy\\self_test\\app5\\app5.json')
        >>> worker.In("Test View 1").GoTo("Test View 4") # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        
        Returns the worker object for method chaining.
        Throws exception if there is no route from the active view to the given
        view.
        @return: murphy.worker.Worker
        FIXME: is not properly solving taking model rules into consideration!
        '''
        LOGGER.info("Will go to %s from %s" % (view, self._active_view))
        rules = []
        if 'tags' in self._properties and not self._properties['tags'] is None:
            rules = [EvaluatorTags(self._properties['tags'])]
                    
        path = self._navigator.get_paths_ext([self._active_view, view],
                                             implemented=True,
                                             shortest=True,
                                             custom_filters=rules)[0]
                                             
        if len(path) > 0:
            LOGGER.info("Solved route is:")
            for view, verb in path:
                LOGGER.info("\t%s -> %s" % (view, verb))
                
        return self.Walk_ext(path)

    def IsIn(self, view_name):
        '''
        Attempts to identify if the given view is 'active', depending on the
        nature of the view can be for example if a dialog or popup is currently
        shown or an internal state is reached.
        Returns True if the given view self identifying method succeeds
        WARNING: this method has very reduced utility, it is mainly provided
        for convenience for very special cases, the method 'WhenIn' is the
        prefered way for dealing with cases like operating system popup
        dialogs or events.
        Given the nature of the method and depending on how the application has
        been modeled many different views could return True in the same
        situation, abuse of this method will most likely be a source of your
        headaches.
        '''
        return self._executor.is_in_view(view_name)

    def Wait(self, view_name):
        '''
        Waits for the given view, throws MurphyConfused if view does not become
        available after the configured view timeout
        FIXME: use project + view timeout!
        '''
        counter = 0
        while not self.IsIn(view_name):
            time.sleep(1)
            counter += 1
            if counter > 60:
                raise MurphyConfused('View %s did not become available' % 
                                     view_name)
                
    def WhenIn(self, view, verb):
        '''
        Adds a special handling for the given view, when this view becomes
        active the provided verb will be executed (in the context of the given
        view).
        Note that murphy only checks if the given view becomes active when
        some verb invocation fails, the intended use of this method is for
        registering popup windows that should be closed as they will interfere
        during the execution of the modeled application.
        An example of this is for example to instruct the worker to close
        a 'Security warning' that may popup at any moment.
        WARNING: in certain scenarios a modeled application that is running
        can be obscured by say an operating system or other application popup,
        while using this method will instruct murphy to close such popup that
        does not neccessarily mean that the modeled application will regain the
        'focus' or the window will become 'active'.
        '''
        self._executor.add_interefing_views(view, verb)

    #FIXME: deprecated, will be removed
    def Walk(self, path):
        '''
        Traverses the given path, the path is an array of strings, each
        string with the format view.verb
        Examples:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app5',
        ... r'murphy\\self_test\\app5\\app5.json')
        >>> path = ["Test View 1.Go to view 2", "Test View 2.Go to view 4"]
        >>> worker.Walk(path) # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        
        Returns the worker object for method chaining.
        '''
        print "walking..."
        if len(path) > 0:
            for k in path:
                view = k.split(".")[0]
                verb = k.split(".")[1]
                self.In(view).Do(verb)
        return self

    def Walk_ext(self, path):
        '''
        Traverses the given path, the path is an array of strings, each
        string with the format view.verb
        Examples:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app5',
        ... r'murphy\\self_test\\app5\\app5.json')
        >>> path = ["Test View 1.Go to view 2", "Test View 2.Go to view 4"]
        >>> worker.Walk(path) # doctest: +ELLIPSIS
        <murphy.Worker instance at 0x...>
        
        Returns the worker object for method chaining.
        '''
        if len(path) > 0:
            for view, verb in path:
                self.In(view).Do(verb)
        return self
        
    def run_script(self, content):
        '''
        Runs a simple script written in plain text, the support is rather
        crude but usefull for most cases.
        The first line in the script must be the 'In' that gives context for
        the execution, each following line is just the verb to be executed.
        Example:
        >>> worker = Worker()
        >>> worker.load_application('self_test.app5',
        ... r'murphy\\self_test\\app5\\app5.json')
        >>> script = "In Test View 1\\nGo to view 2\\nGo to view 4"
        >>> worker.run_script(script) # doctest: +ELLIPSIS
        Run Script took ...
        '''
        started_at = time.time()
        self._executor.visual_executor.load_search_memory()

        lines = content.split('\n')
        self.In(lines[0].strip()[3:].strip())
        for line in lines[1:]:
            todo = line.strip()
            if todo != "":
                if todo[:3].strip() == "In":
                    self.In(todo[3:].strip())
                else:
                    self.Do(todo)

        self._executor.visual_executor.save_search_memory()
        ended_at = time.time()
        print '%s took %0.3f ms' % ("Run Script", (ended_at-started_at)*1000.0)

    def get_views(self):
        '''
        Returns a dictionary containing all the views in the loaded
        application, this method is intended mostly for internal usage
        '''
        return self._views
        
    @property
    def execution(self):
        '''
        Returns the execution object that contains parameters, properties and
        the run state
        '''
        return self._execution
    
    @property
    def executor(self):
        '''
        Gets the executor instance for this worker
        '''
        return self._executor

    @property
    def navigator(self):
        '''
        Gets the navigator instance for this worker
        '''
        return self._navigator

    @property
    def graphs(self):
        '''
        Gets the graphs generator instance for this worker
        '''
        return self._graphs

    @property
    def input(self):
        '''
        Returns the primitives used for simulating user interaction.
        The returning object has the .mouse and .keyboard properties for
        automating it's actions
        '''
        return self._user_simulation
        
    @property
    def parameters(self):
        '''
        Returns the parameters dictionary, use consume_parameter for getting
        the next value to be used in the flow
        '''
        return self._parameters

    def consume_parameter(self, name):
        '''
        Consumes the next parameter in the queue
        '''
        return self._parameters[name].pop(0)

    @property
    def properties(self):
        '''
        Returns the worker properties, parameters are consumed but properties
        not
        '''
        return self._properties

    def get_superview_verb_parameters(self, view_name, verb_name):
        '''
        Returns an array of the parameters needed to execute this verb, to be
        used when the view is a superview, not a normal one
        '''
        path = self._navigator.get_superview_path(view_name,
                                                  verb_name,
                                                  self._properties['tags'])
        params = []
        for node, arc in path:
            this_params = self.get_verb_parameters(node, arc)
            params.extend(this_params)
        return params
        
    def get_verb_parameters(self, view_name, verb_name):
        '''
        Returns an array of the parameters needed to execute this verb
        '''
        params = []
        if not view_name in self._views:
            raise Exception("Requested view '%s' is not defined" % view_name)
        view = self._views[view_name]
        
        if 'verbs' in view:
            verbs = view['verbs']
            if not verb_name in verbs:
                raise Exception(("Requested verb '%s' in view '%s' is not " +
                                 "defined") % (view_name, verb_name))
            verb = verbs[verb_name]
            if 'superview of' in view['self'].HERE:
                if type(verb['how']) is list:
                    return self.get_superview_verb_parameters(view_name,
                                                              verb_name)

            if 'uses' in verb:
                if type(verb['uses']) is list:
                    params += verb['uses']
                else:
                    params.append(verb['uses'])
        else:
            print "view %s does not have verbs" % view_name
            
        return params
        