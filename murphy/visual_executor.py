'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

 that executes verbs by using the bitmap matching engine, the
module is not intended to be called directly, only indirectly thru
the executor module
'''

from murphy import image, smart_image, errors
import logging, types, datetime, time, os
LOGGER = logging.getLogger('root.' + __name__)

COMPARISON_PRECISION = 0.99
#seconds will wait before checking interfering windows
CHECK_INTERFERING_FREQUENCY = 5

def _load_image(file_name, color_mask=None):
    '''
    Loads the given file and returns an ImageHolder for it
    '''
    return image.ImageHolder(file_name, color_mask)

def _load_snapshots(view, folder):
    '''
    Loads all the snapshots for the given view if they are not loaded yet
    '''
    there = view['self'].HERE
    img = there['snapshots'][0]
    if type(img) is str or type(img) is unicode:
        for i in range(len(there['snapshots'])):
            a_file = os.path.join(folder, there['snapshots'][i])
            if 'snapshots mask' in there:
                img = _load_image(a_file, there['snapshots mask'][i])
            else:
                img = _load_image(a_file)
            there['snapshots'][i] = img

def _get_view_snapshots(view, folder):
    '''
    Convenience method that returns the associated snapshots to the given
    view and ensures to loadthem if they're not loaded yet
    '''
    _load_snapshots(view, folder)
    return view['self'].HERE['snapshots']


class VisualExecutor():
    '''
    Executor implementation that deals with screen bitmap search & match
    '''
    def __init__(self, views, default_timeout, img_folder, worker):
        #user_simulation, abort_check_function):
        self._views = views
        self._timeout = default_timeout
        self._images_path = img_folder
        self._worker = worker
        
        self._mouse = self._worker.input.mouse
        self._keyboard = worker.input.keyboard
        if not img_folder is None:
            memory_file = os.path.join(img_folder, '..', 'memory.json')
        else:
            memory_file = None
        self._searches = smart_image.SmartSearch(COMPARISON_PRECISION,
                                                 memory_file,
                                                 worker.input.screen)
        #self._counter = 0

    @property
    def images_path(self):
        '''
        Returns the path where images are loaded from
        '''
        return self._images_path
    
    
    def view_uses_driver(self, view_name):
        '''
        Returns True if the given view can use the VisualExecutor
        '''
        if 'snapshots' in self._views[view_name]['self'].HERE:
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
        if isinstance(how, types.DictType):
            if 'visual' in how:
                return True
        return False


    def is_in_view(self, view_name, check_interfering_fn):
        '''
        Validates if the current view is active or not
        '''
        view = self._views[view_name]
        #FIXME: check if snapshot / method available for identification
        snapshots = _get_view_snapshots(view, self._images_path)
        
        acceptable_score = None
        if 'precision' in view['self'].HERE:
            acceptable_score = view['self'].HERE['precision']
        
        #optimized for positive case
        result = self._searches.find_image(snapshots,
                                           view_name,
                                           acceptable_score)
        
        #if result.result:
        #    self._counter += 1
        #    img = self._worker.input.screen()
        #    img.save("Screen %s.bmp" % self._counter)
        #    snapshots[0].image.save("Screen %s recognized as.bmp" % self._counter)
            
        if result.result == False:
            if check_interfering_fn:
                check_interfering_fn()
                result = self._searches.find_image(snapshots,
                                                   view_name,
                                                   acceptable_score)

        return result.result


    def execute_verb(self, view_name, verb_name, check_interfering_views_fn, tags):
        '''
        Called by executor when the visual driver is enabled, to execute
        a visual verb means click on it
        '''
        #search_id = view_name + "." + verb_name
        search_id = view_name
        started_at = datetime.datetime.now()
        snapshots = _get_view_snapshots(self._views[view_name],
                                        self._images_path)
        how = self._views[view_name]['verbs'][verb_name]['how']

        acceptable_score = None
        if 'precision' in self._views[view_name]['self'].HERE:
            acceptable_score = self._views[view_name]['self'].HERE['precision']
            
        while True:
            search = self._searches.wait_image(snapshots,
                                               search_id,
                                               CHECK_INTERFERING_FREQUENCY,
                                               self._worker.execution.aborted,
                                               acceptable_score)
            if search.result:
                break
            if self._worker.execution.aborted():
                raise errors.UserCancelled("User cancelled")
                
            check_interfering_views_fn()
            ellapsed = (datetime.datetime.now() - started_at).seconds
            if ellapsed > self._timeout:
                #FIXME: generate best guess, could be as an extra call to
                #wait_for_image with extra param
                raise errors.MurphyConfused("Can't find '%s' in the screen" % view_name)
            else:
                time.sleep(1.0)

        width = how['visual'][2] - how['visual'][0]
        height = how['visual'][3] - how['visual'][1]
        if 'type' in how and how['type'] == 'text input':
            if not 'uses' in how:
                raise errors.MurphyConfused("Text input element needs the " +
                                            "'uses' clause for the data to enter")
            #FIXME: this should be optional / configurable...
            self._mouse.click(search.x_pos + how['visual'][0] + (width/2),
                              search.y_pos + how['visual'][1] + (height/2))
            value = self._worker.consume_parameter(how['uses'])
            self._keyboard.enters(value)
        else:
            if how.get('type', '') == 'link':
                self._mouse.move(search.x_pos + 1 + how['visual'][0],
                                  search.y_pos + 1 + how['visual'][1])
                self._mouse.click(search.x_pos + how['visual'][0],
                                  search.y_pos + how['visual'][1])
            else:
                self._mouse.move(search.x_pos + 1 + how['visual'][0] + (width/2),
                                  search.y_pos + 1 + how['visual'][1] + (height/2))
                self._mouse.click(search.x_pos + how['visual'][0] + (width/2),
                                  search.y_pos + how['visual'][1] + (height/2))
                if 'type' in how and how['type'] == 'desktop icon':
                    time.sleep(0.1)
                    self._keyboard.enters("{enter}")


    def load_search_memory(self):
        '''
        Loads a cache of comparison matches
        '''
        self._searches.load_memory()


    def save_search_memory(self):
        '''
        Saves a cache of comparison matches
        '''
        self._searches.save_memory()
