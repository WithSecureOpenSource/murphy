'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

High level image search
'''

from murphy import image, utils
import logging, types, time, os
from datetime import datetime

LOGGER = logging.getLogger('root.' + __name__)

#FIXME: we need some sort of global __DEBUG__
_SAVE_SEARCHES = False
_CHECK_LAST_POSITION = True
BREATH_TIME = 0.5

class SmartSearch(object):
    '''
    Helper class to produce rich searches
    It is possible to optimize searches given an id, search an image
    out of a group of images, set the tolerance level and so.
    '''
    def __init__(self, acceptable_score, memory_file_name, image_function):
        self._acceptable_score = acceptable_score
        self._memory_file_name = memory_file_name
        self._get_source_image = image_function
        self._search_counter = 0
        self._results_cache = dict()
        self._last_full_search = dict()

        
    def load_memory(self):
        '''
        Loads the search cache from a file, if file name is None the method
        returns silently but will log a warning
        '''
        self._results_cache = dict()
        if self._memory_file_name is None:
            LOGGER.warning("Trying to load memory when no file was specified")
            return
        if os.path.isfile(self._memory_file_name) == False:
            LOGGER.warning("Memory file %s not found" % self._memory_file_name)
            return
        
        self._results_cache = utils.load_json_object(self._memory_file_name)

        
    def save_memory(self):
        '''
        Saves the search cache from a file, if file name is None the method
        returns silently but will log a warning
        '''
        if self._memory_file_name is None:
            LOGGER.warning("Trying to save memory when no file was specified")
            return
        utils.save_json_object(self._results_cache, self._memory_file_name)

        
    def wait_image(self, to_find, search_id, timeout, abort_check_function, acceptable_score=None):
        '''
        Tries to find the given image(s) up to the given seconds specified in
        timeout
        '''
        started_at = datetime.now()
        old_acceptable_score = self._acceptable_score
        if not acceptable_score is None:
            self._acceptable_score = acceptable_score
        while True:
            ret = self.find_image(to_find, search_id)
            if ret.result:
                self._acceptable_score = old_acceptable_score
                return ret

            if abort_check_function() == True:
                self._acceptable_score = old_acceptable_score
                return ret
                
            ellapsed = (datetime.now() - started_at).seconds
            #let it breath for a bit
            time.sleep(BREATH_TIME)
            if ellapsed > timeout:
                self._acceptable_score = old_acceptable_score
                return ret
        self._acceptable_score = old_acceptable_score
    
    def find_image(self, to_find, search_id, acceptable_score=None):
        '''
        Searches if the given image(s) can be found, returns
        a SearchResult object.
        The image is expected to be an ImageHolder or an array of them
        '''
        LOGGER.debug("Searching for %s", search_id)
        if type(to_find) != types.ListType:
            to_find = [to_find]

        search_in = image.ImageHolder(self._get_source_image())
        old_acceptable_score = self._acceptable_score
        if not acceptable_score is None:
            self._acceptable_score = acceptable_score
            
        #test if image is in the last coordinates where it was last spotted
        if _CHECK_LAST_POSITION:
            ret = self._is_in_last_position_it_was(to_find, search_id, search_in)
            if ret.result:
                LOGGER.debug("Found %s in it's last position" % search_id)
                self._acceptable_score = old_acceptable_score
                return ret
        
        #try search by hints, still faster than full search
        ret, false_positives = self._find_image_by_hint(to_find,
                                                        search_id,
                                                        search_in)
        if ret.result:
            self._results_cache[search_id] = (ret.index, ret.x_pos, ret.y_pos)
            self._acceptable_score = old_acceptable_score
            return ret

        if not search_id in self._last_full_search:
            self._last_full_search[search_id] = datetime.now()

        #do full search no more ofthen than once every 10 seconds if hinted
        #search can be used
        if (self._can_do_hinted_search(to_find) == True and
          (datetime.now() - self._last_full_search[search_id]).seconds < 10):
            self._acceptable_score = old_acceptable_score
            return ret
        
        best_score, best_index = 0, 0
        best_x, best_y = 0, 0
        
        for index in range(len(to_find)):
            to_search = to_find[index]
            self._search_counter += 1
            score, x_pos, y_pos = image.find_image(to_search, search_in)
            if self._is_score_acceptable(score, to_search.pixel_count):
                self._results_cache[search_id] = (index, x_pos, y_pos)
                LOGGER.debug("Found %s at %s %s" % (search_id, x_pos, y_pos))
                self._last_full_search[search_id] = datetime.now()
                self._acceptable_score = old_acceptable_score
                return SearchResult(True, score, (x_pos, y_pos), index)

            if score > best_score:
                best_score = score
                best_index = index
                best_x = x_pos
                best_y = y_pos

            #Saves each search for debugging purposes
            if _SAVE_SEARCHES:
                guess = search_in.crop((best_x,
                                        best_y,
                                        best_x + to_find[best_index].size[0],
                                        best_y + to_find[best_index].size[1]))
                guess.save("test %i best candidate %s.bmp" % (self._search_counter, best_score),
                               "BMP")
                to_search.image.save(("test %i to search.bmp" % 
                                      self._search_counter),
                                     "BMP")
                search_in.image.save("test %i screen.bmp" % self._search_counter,
                                  "BMP")

        LOGGER.debug("Can't find %s" % search_id)
        self._last_full_search[search_id] = datetime.now()
        self._acceptable_score = old_acceptable_score
        return SearchResult(False, best_score, (best_x, best_y), best_index)

        
    def _is_in_last_position_it_was(self, images, search_id, search_in):
        '''
        Checks if the given images are visible in the same position they were
        spotted last time
        '''
        started_at = datetime.now()
        if search_id in self._results_cache:
            index, x_pos, y_pos = self._results_cache[search_id]
            to_search = images[index]
            max_x = search_in.size[0] - to_search.size[0]
            max_y = search_in.size[1] - to_search.size[1]
            if x_pos >= max_x or y_pos >= max_y:
                self._results_cache.pop(search_id)
                LOGGER.debug("Polluted cache for search id %s with %s %s" % (search_id, x_pos, y_pos))
                return SearchResult(False, 0, (0, 0), 0)
            
            score, x_pos, y_pos = image.test_image(to_search,
                                                   search_in,
                                                   x_pos,
                                                   y_pos)
            took = ((datetime.now() - started_at).microseconds / 1000000.0)
            if self._is_score_acceptable(score, to_search.pixel_count):
                LOGGER.debug("Cache hit for %s took %s" % (search_id, took))
                return SearchResult(True, score, (x_pos, y_pos), index)
            else:
                LOGGER.debug("Cache miss for %s at %s %s %s used %s" % (search_id, x_pos, y_pos, score, took))
                if _SAVE_SEARCHES:
                    search_in.image.save("cache miss %i for %s.bmp" % (self._search_counter, search_id),
                               "BMP")
                    score_area = search_in.crop((x_pos,
                                                 y_pos, 
                                                 x_pos + to_search.size[0],
                                                 y_pos + to_search.size[1]))
                    score_area.save("cache miss area %i for %s.bmp" % (self._search_counter, search_id),
                               "BMP")
                    to_search.image.save("cache miss image %i for %s.bmp" % (self._search_counter, search_id),
                               "BMP")
                return SearchResult(False, score, (x_pos, y_pos), index)

        return SearchResult(False, 0, (0, 0), 0)
    
    
    def _is_score_acceptable(self, score, exact_score):
        '''
        Checks if the comparison score is acceptable
        '''
        perc = (float(score) / float(exact_score))
        LOGGER.debug("Comparison scored %f of %i" % (perc, exact_score))
        if perc > self._acceptable_score:
            return True
        else:
            return False

    def _can_do_hinted_search(self, to_find):
        if to_find[0].size[0] < 32 or to_find[0].size[1] < 32:
            return False
        else:
            return True
            
    def _find_image_by_hint(self, to_find, search_id, search_in):
        got_false_positives = False
        if self._can_do_hinted_search(to_find) == False:
            return SearchResult(False, 0, (0, 0), 0), got_false_positives
            
        for index in range(len(to_find)):
            to_search = to_find[index]
            cropped = image.ImageHolder(to_search.crop((0, 0, 32, 32)))
            score, x_pos, y_pos = image.find_image(cropped, search_in)
            if self._is_score_acceptable(score, cropped.pixel_count):
                LOGGER.debug("HINT Found %s at %s %s" % (search_id, x_pos, y_pos))
                score, x_pos, y_pos = image.test_image(to_search,
                                                       search_in,
                                                       x_pos,
                                                       y_pos)
                if self._is_score_acceptable(score, to_search.pixel_count):
                    LOGGER.debug("Found by hint %s at %s %s" % (search_id, x_pos, y_pos))
                    return SearchResult(True, score, (x_pos, y_pos), index), got_false_positives
                else:
                    LOGGER.debug("HINT false %s at %s %s" % (search_id, x_pos, y_pos))
                    got_false_positives = True
        
        return SearchResult(False, 0, [0, 0], 0), got_false_positives
        
    '''
    still need to port this one
    def _find_image_by_hint(search_for, search_id, search_in):
        """Searches for the given image by using a hint on the search"""
        global _SEARCH_COUNTER
        for i in range(len(search_for)):
            to_search = search_for[i]
            _SEARCH_COUNTER += 1
            id_num = search_id + "." + str(i)
            LOGGER.debug("testing hint %s test number %i" % (id_num,
                                                             _SEARCH_COUNTER))

            #test using a hint instead of full image search
            #FIXME: hint needs more cleverness as the left top corner is in
            #many cases ineffective
            hint = ImageHolder(to_search.crop((0, 0, 8, 8)))
            score, x_pos, y_pos = find_image(hint, search_in)
            if _is_score_acceptable(score, 64): #FIXME: test effectiveness
                score, x_pos, y_pos = test_image(to_search,
                                                 search_in,
                                                 x_pos,
                                                 y_pos)
                max_score = to_search.size[0] * to_search.size[1]
                if _is_score_acceptable(score, max_score):
                    IMAGE_RESULTS_CACHE[search_id] = (i, x_pos, y_pos)
                    return SearchResult(True, score, [x_pos, y_pos], i)
                    
        return SearchResult(False, 0, [0, 0], 0)

    '''    
        
class SearchResult(object):
    '''
    Encapsulates the results of a search into a readonly class
    '''
    
    def __init__(self, result, score, pos, index):
        self._result = result
        self._score = score
        self._x_pos = pos[0]
        self._y_pos = pos[1]
        self._index = index
        
    @property
    def result(self):
        '''
        Returns True / False if the search succeded
        '''
        return self._result
        
    @property
    def score(self):
        '''
        Returns the score of the comparison
        '''
        return self._score
    
    @property
    def x_pos(self):
        '''
        Returns the x coordinate of the search result
        '''
        return self._x_pos
        
    @property
    def y_pos(self):
        '''
        Returns the y coordinate of the search result
        '''
        return self._y_pos
        
    @property
    def index(self):
        '''
        Returns the index of the image that matched
        '''
        return self._index
