'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

This module contains the Navigator class that contains logic for
'navigating' the application like get paths for going from one view
to another one
'''
from murphy import errors
from datetime import datetime

MAX_PATH_DEPTH = 30
MAX_SHORT_PATH_DEPTH = 15
MAX_ARC_REPETITION = 1

PATH_EVALUATIONS = 0

class Navigator():
    '''
    Class that navigates a graph, what is considered views and verbs in
    murphy are called nodes and links here as they represent a typical graph
    '''
    #continue traversing the graph
    ACTION_CONTINUE = 1
    #terminal reached, no deeper navigation, report for collect and continue
    #with next arcs
    ACTION_TERMINAL = 2
    #dont go any deeper on this path and discard it
    ACTION_DISCARD = 3
    
    def __init__(self, views):
        self._views = views
        self._max_depth_reached_times = 0
        self._started_at = None
        self._traverses = 0
        self._traverses_per_second = 100000
        
    def _list_arcs(self, node):
        '''
        Returns an iteration for the arcs
        '''
        for arc in node['verbs'].values():
            yield node, arc
    
    
    def is_arc_terminal(self, node, arc):
        '''
        An arc is terminal if it does not connect to anything or if it
        connects to a declared but undefined view
        '''
        if 'goes to' in arc:
            if arc['goes to'] in self._views:
                is_terminal = False
            else:
                is_terminal = True
        else:
            is_terminal = True
        return is_terminal

        
    def get_arc_destination(self, arc):
        '''
        Helper function for getting the destination
        '''
        if 'goes to' in arc and arc['goes to'] in self._views:
            return self._views[arc['goes to']]
        else:
            if not 'goes to' in arc:
                print "arc %s does not have goes to!" % str(arc)
            elif not arc['goes to'] in self._views:
                print "dest view %s not defined!" % arc['goes to']
            return None
        
        
    def _traverse_graph(self, node, evaluator, path=None, tuple_path=None):
        '''
        Traverses the tree, calls the evaluator for instructions on where
        to continue the current path or switch to another one
        '''
        if path is None:
            path = []
            tuple_path = []
            self._max_depth_reached_times = 0
            self._started_at = datetime.now()
            self._traverses = 0

        self._traverses += 1
        if self._traverses % self._traverses_per_second == 0:
            now = datetime.now()
            self._traverses_per_second = (float(self._traverses) / 
                        float((now - self._started_at).seconds + 0.0000001))
            print ("%d traversal calls so far, %f per second, %s path"
             " evaluated %s depth-discarded so far" % 
                                            (self._traverses,
                                             self._traverses_per_second,
                                             PATH_EVALUATIONS,
                                             self._max_depth_reached_times))
            self._traverses_per_second = int(self._traverses_per_second)
        
            
        if len(path) > MAX_PATH_DEPTH:
            self._max_depth_reached_times += 1
            return

        for node, arc in self._list_arcs(node):
            action = evaluator(path, node, arc, tuple_path)
            if action == Navigator.ACTION_CONTINUE:
                if self.is_arc_terminal(node, arc) == False:
                    dest = self.get_arc_destination(arc)
                    if not dest is None:
                        path.append((node, arc))
                        tuple_path.append((node['self'].HERE['desc'],
                                           arc['desc']))
                        self._traverse_graph(dest, evaluator, path, tuple_path)
                        tuple_path.pop()
                        path.pop()

    
    def _get_filtered_paths(self, start_view, filters):
        '''
        Uses the given chain of filters to evaluate user-supplied criterias.
        If at least one filter discards then the branch is aborted
        '''
        def evaluate(path, node, arc, tuple_path):
            for a_filter in filters:
                if a_filter.evaluate(path, node, arc, tuple_path) == \
                  Navigator.ACTION_DISCARD:
                    return Navigator.ACTION_DISCARD
            return Navigator.ACTION_CONTINUE
        
        start_view = self._views[start_view]
        self._traverse_graph(start_view, evaluate)
                    
        
    def get_paths_ext(self, places_to_visit, avoids=None, implemented=None,
      shortest=None, best_scored=False, business_rules=None,
      custom_filters=None):
        '''
        Given an array of nodes it will find all paths that connects them, the
        1st element is the starting point and each additional node or node-arc
        pair are intermediate places to visit, for example:
        get_paths_ext(['Device', ('Login', 'Login invalid user'), 'Enter Question Dialog']...
        '''
        results = [[]]
        
        if len(places_to_visit) < 2:
            raise ValueError('At least 2 nodes must be specified')
            
        start_view = places_to_visit[0]
        if type(start_view) is tuple:
            raise ValueError('Initial point to visit must be a view')
        
        #Build the filter chain
        collector = EvaluatorCollect(self._views, shortest, best_scored)
        filters = []
        if avoids:
            filters.append(EvaluatorAvoid(avoids))
        if shortest:
            shortest = EvaluatorShortest()
            filters.append(shortest)
        if implemented == True:
            filters.append(EvaluatorImplemented(self._views))
        if business_rules:
            filters.append(SimpleFilter(business_rules))
        
        if custom_filters:
            for a_filter in custom_filters:
                filters.append(a_filter)
            
            
        filters.append(collector)
        #FIXME: cleanup expected tail - view, can be simplified into one call
        for index in range(1, len(places_to_visit)):
            end_view = places_to_visit[index]
            add_arc = None
            expected_tail = None
            if type(end_view) is tuple:
                tail_node, tail_arc = end_view
                tail_node = self._views[tail_node]
                tail_arc = tail_node['verbs'][tail_arc]
                expected_tail = (tail_node, tail_arc)
                end_view = self.get_arc_destination(tail_arc)['self'].HERE['desc']
            
            if (end_view != start_view or
              places_to_visit[index-1] == places_to_visit[index]
              or (end_view == start_view and not expected_tail is None)):
                collector.set_end_view(end_view, expected_tail)
                if shortest:
                    shortest.set_results_array(collector.results)
                self._get_filtered_paths(start_view, filters)
                if len(collector.results) == 0:
                    raise errors.NoRouteFound(("No route found from %s to %s" %
                                              (start_view, end_view)))

                new_results = []
                for result in results:
                    for segment in collector.results:
                        new_results.append(result + segment)
                results = new_results
                collector.reset_results()
                
            if add_arc:
                node = self._views[end_view]
                arc = node['verbs'][add_arc]
                for result in results:
                    result.append((node, arc))
                start_view = self.get_arc_destination(arc)
                start_view = start_view['self'].HERE['desc']
            else:
                start_view = end_view
                
        
        for solution_index in range(len(results)):
            solution = results[solution_index]
            for index in range(len(solution)):
                node, arc = solution[index]
                solution[index] = (node['self'].HERE['desc'], arc['desc'])

        return results
    
    def get_superview_path(self, view_name, verb_name, tags=None):
        '''
        Returns the path of a superview verb
        FIXME: lacks data consideration in path!
        '''
        view = self._views[view_name]
        verb = view['verbs'][verb_name]
        path = [view['self'].HERE['superview of']]
        if type(verb['how']) is list:
            path += verb['how']
        
        destination = verb['goes to']
        if 'superview of' in self._views[destination]['self'].HERE:
            destination = self._views[destination]['self'].HERE['superview of']
            
        if path[-1] != destination:
            path += [destination]
        
        rules = []
        if not tags is None:
            rules.append(EvaluatorTags(tags))

        return self.get_paths_ext(path,
                                  implemented=True,
                                  shortest=True,
                                  custom_filters=rules)[0]

                                  
    def get_effective_path(self, path, tags=None):
        '''
        Returns the effective path of the given path, the effective path solves
        normal and superview paths returning the lowest level step by step path
        that is ultimately executed.
        This is needed in order to collect parameter informations, so
        superviews do not have to declare if the underlying path will use
        parameters
        The path is expected as an array of tuples, same output as
        get_paths_ext: [('node', 'arc'), ('node2','arc2')]
        Note that the method will only work for the fully implemented shortest
        path.
        '''
        #FIXME: implementation of superview is in navigator_executor so this
        #duplicated logic, should be properly encapsulated
        #TODO: make it multilevel aware, it could iteratively solve the path
        #until the returned path contains no more superviews (== last solution)
        result = []
        for node, arc in path:
            node_obj = self._views[node]
            arc_obj = node_obj['verbs'][arc]
            if not type(arc_obj['how']) is list:
                result.append((node, arc))
            else:
                subpath = [node_obj['self'].HERE['superview of']]
                subpath += arc_obj['how']
                destination = arc_obj['goes to']
                if 'superview of' in self._views[destination]['self'].HERE:
                    destination = self._views[destination]['self'].HERE['superview of']
                if subpath[-1] != destination:
                    subpath += [destination]
                    
                rules = []
                if not tags is None:
                    rules = [EvaluatorTags(tags)]
                 
                subpath = self.get_paths_ext(subpath, 
                                             implemented=True,
                                             shortest=True,
                                             custom_filters=rules)[0]
                result.extend(subpath)
                
        return result
        
    
    def convert_from_dot_to_tuple(self, path):
        '''
        temporarly convert fn, will be removed after transition
        '''
        result = []
        for step in path:
            if step.find('.') != -1:
                node, arc = step.split('.')
                result.append((node, arc))
            else:
                result.append(step)
                
        return result

    def convert_from_tuple_to_dot(self, path):
        '''
        temporarly convert fn, will be removed after transition
        '''
        result = []
        for step in path:
            if type(step) is str or type(step) is unicode:
                result.append(step)
            else:
                node, arc = step
                result.append(node + '.' + arc)
                
        return result

        
    def get_related_views(self, view_name):
        '''
        Returns a list of views that are reachable from view_name (including).
        '''
        pending_views = []
        processed_views = []
        
        while True:
            if view_name in self._views:
                view = self._views[view_name]
                for verb_name in view['verbs'].keys():
                    verb = view['verbs'][verb_name]
                    if 'goes to' in verb and verb['goes to'] != '':
                        target = verb['goes to']
                        if (not target in processed_views and
                          target != view_name):
                            pending_views.append(target)
            
            processed_views.append(view_name)
            if len(pending_views) > 0:
                view_name = pending_views.pop(0)
            else:
                break
        return processed_views

def compute_score(path):
    
    score = 0
    visits = dict()
    
    for node, arc in path:
        step = (node['self'].HERE['desc'], arc['desc'])
        if not step in visits:
            visits[step] = 1000
            score += 1000
        else:
            score -= 100
    
    return score
    
    
class SimpleFilter(object):
    '''
    Simple adapter to user supplied validation filter
    '''
    def __init__(self, validation_function, path_prefix=None):
        self._validation_function = validation_function
        self._path_prefix = path_prefix
        
    def evaluate(self, path, node, arc, tuple_path):
        '''
        As per filter contract it validates if the path is valid so far
        by calling the supplied validation function
        '''
        tuple_path.append((node['self'].HERE['desc'], arc['desc']))
        if self._path_prefix:
            evaluation = self._validation_function(self._path_prefix + tuple_path)
        else:
            evaluation = self._validation_function(tuple_path)
        tuple_path.pop()
        if evaluation == False:
            return Navigator.ACTION_DISCARD
        else:
            return Navigator.ACTION_CONTINUE


class EvaluatorTags(object):
    '''
    Adapter to exclude paths that contains nodes that should be avoided
    '''
    def __init__(self, tags):
        self._tags = tags
        
    def evaluate(self, path, node, arc, tuple_path):
        if 'tags' in arc:
            for tag, value in self._tags.items():
                if tag in arc['tags'] and arc['tags'][tag] != value:
                    return Navigator.ACTION_DISCARD
                    
        return Navigator.ACTION_CONTINUE
        
class EvaluatorAvoid(object):
    '''
    Adapter to exclude paths that contains nodes that should be avoided
    '''
    def __init__(self, avoid_points):
        self._avoids = avoid_points
        
    def evaluate(self, path, node, arc, tuple_path):
        '''
        Excludes the given path if any view has been requested to be avoided
        '''
        for elem in self._avoids:
            if type(elem) is str or type(elem) is unicode:
                if node['self'].HERE['desc'] == elem:
                    return Navigator.ACTION_DISCARD
            else:
                avoid_node, avoid_arc = elem
                if (node['self'].HERE['desc'] == avoid_node and
                  arc['desc'] == avoid_arc):
                    return Navigator.ACTION_DISCARD
                    
        return Navigator.ACTION_CONTINUE
        
        
class EvaluatorShortest(object):
    '''
    Adapter for filtering the shortest path, only one result is kept instead
    of all possible ones
    '''

    def __init__(self):
        self._results = None
    
    def set_results_array(self, results):
        self._results = results
    
    def evaluate(self, path, node, arc, tuple_path):
        '''
        Evaluates where this path is shortest so far
        '''
        if len(path) > MAX_SHORT_PATH_DEPTH:
            return Navigator.ACTION_DISCARD
        
        if len(self._results) == 0 or len(path) < len(self._results[0]):
            return Navigator.ACTION_CONTINUE
        else:
            return Navigator.ACTION_DISCARD

            
class EvaluatorImplemented(object):

    def __init__(self, views):
        self._views = views
    
    def evaluate(self, path, node, arc, tuple_path):
        if not node['self'].HERE['desc'] in self._views:
            return Navigator.ACTION_DISCARD
        if not arc['desc'] in node['verbs']:
            return Navigator.ACTION_DISCARD
        if not 'how' in arc:
            return Navigator.ACTION_DISCARD
        if not 'goes to' in arc:
            return Navigator.ACTION_DISCARD
        if not arc['goes to'] in self._views:
            return Navigator.ACTION_DISCARD
        
        return Navigator.ACTION_CONTINUE


class EvaluatorCollect(object):

    def __init__(self, views, shortest, best_scored):
        global PATH_EVALUATIONS
        self._results = []
        self._scores = []
        self._views = views
        self._shortest = shortest
        self._end_view = None
        self._expected_tail = None
        self._best_scored = best_scored
        PATH_EVALUATIONS = 0
    
    def reset_results(self):
        self._results = []
        self._scores = []

    @property
    def results(self):
        return self._results
    
    def set_end_view(self, end_view, expected_tail):
        self._end_view = end_view
        self._expected_tail = expected_tail

    def evaluate(self, path, node, arc, tuple_path):
        global PATH_EVALUATIONS
        
        if 'goes to' in arc and arc['goes to'] in self._views:
            dest = self._views[arc['goes to']]
        else:
            return Navigator.ACTION_DISCARD

        if path.count((node, arc)) == MAX_ARC_REPETITION:
            #this rules out using the same path twice, which is needed in some
            #cases, return Navigator.ACTION_DISCARD
            #FIXME: better formulation should allow x repetitions with same
            #application internal state
            return Navigator.ACTION_DISCARD
            
        collect = False
        
        if self._expected_tail:
            collect = (node, arc) == self._expected_tail
        else:
            collect = dest['self'].HERE['desc'] == self._end_view
        
        if collect:
            to_add = path + [(node, arc)]
            self._results.append(to_add)
            PATH_EVALUATIONS += 1
            
            if self._shortest == True:
                if len(self._results) > 1:
                    self._results.pop(0)
                return Navigator.ACTION_DISCARD

            if self._best_scored == True:
                self._scores.append(compute_score(self._results[-1]))
                if len(self._results) > 1:
                    if self._scores[0] > self._scores[1]:
                        self._results.pop()
                        self._scores.pop()
                    else:
                        self._results.pop(0)
                        self._scores.pop(0)
            return Navigator.ACTION_DISCARD
            
        return Navigator.ACTION_CONTINUE
