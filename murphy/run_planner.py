'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from murphy.navigator import SimpleFilter, EvaluatorTags

def solve_plan(path_plan, worker, model, tags):
    '''
    FIXME: A segment limits future segments, there may end up with
    no solution in future segments if the preceeding segments limits it somehow
    '''
    initial_view = path_plan[0]['node']
    walked = []
    segments_so_far = 0
    heuristic = path_plan[0]['heuristics'][0]
    
    for plan in path_plan[1:]:
        node, arc = plan['node'], None
        if node.find(".") != -1:
            node, arc = node.split(".")

        if arc is None and node == initial_view and segments_so_far > 0:
            #ignoring as start and end are same view
            pass
        else:
            if arc:
                destination = (node, arc)
            else:
                destination = node
            walked = _solve_segment(walked,
                                    initial_view,
                                    destination,
                                    heuristic,
                                    worker,
                                    model,
                                    tags)
            segments_so_far += 1
            
        if arc:
            initial_view = worker.get_views()[node]
            initial_view = initial_view['verbs'][arc]['goes to']
        else:
            initial_view = node
        
        if 'heuristics' in plan:
            heuristic = plan['heuristics'][0]
        else:
            heuristic = None
        
    print "Final solved path is (%s):" % len(walked)
    for node, arc in walked:
        print '\t%s -> %s' % (node, arc)
    
    return walked

def get_params_needed(path, worker):

    #navigator = worker.navigator
    effective_path = path #navigator.get_effective_path(path, tags)
    to_collect = []
        
    for view, verb in effective_path:
        params = worker.get_verb_parameters(view, verb)
        this_arc = {'node': view, 'arc': verb, 'params': params}
        to_collect.append(this_arc)
    
    return to_collect
                
def _solve_segment(walked, starts, ends, method, worker, model, tags):
    '''
    Given the already traversed path 'walked', append the new segment
    The walked segment can be:
        shortest
        longest
        unvisited
        
    SimpleFilter
    
    get_paths_ext(self, places_to_visit, avoids=None, implemented=None,
    shortest=None, best_scored=False, business_rules=None, custom_filters=None):
  
    path_validation = self._model.rules.is_path_valid
    SimpleFilter(path_validation)
  
    '''
    navigator = worker.navigator
    path_validation = model.rules.is_path_valid
    rules = [SimpleFilter(path_validation, walked),
             EvaluatorTags(tags)]
    
    trip = [starts, ends]
    if method == 'shortest':
        solved_path = navigator.get_paths_ext(trip,
                                              implemented=True,
                                              shortest=True,
                                              custom_filters=rules)[0]
    elif method == 'longest':
        solved_path = navigator.get_paths_ext(trip,
                                              implemented=True,
                                              best_scored=True,
                                              custom_filters=rules)[0]
    elif method == 'unvisited':
        coverage = model.load_coverage()
        visited = []
        for run in coverage:
            for step in run:
                visited.append((step.view_name, step.verb_name))
        
        solutions = navigator.get_paths_ext(trip,
                                            implemented=True,
                                            custom_filters=rules)
        #from the solutions, pick the one that visits most unvisited
        #while is as short as possible
        best_solution = None
        best_score = None
        for solution in solutions:
            current_visits = visited[:]
            score = 0
            for step in solution:
                if not step in current_visits:
                    current_visits.append(step)
                    score += 1000
                else:
                    score -= 100
            if score > best_score:
                best_score = score
                best_solution = solution

        print "best score is %s" % best_score
        print "best solution is %s" % best_solution
        if best_solution is None:
            raise Exception("No solution found")
        return walked + best_solution
    else:
        raise Exception("Euristic %s not implemented yet" % method)

    return walked + solved_path
