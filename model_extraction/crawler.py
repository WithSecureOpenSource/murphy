'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Generic crawler that explores a world

A world encapsulates what is going to be explored, each different state of the
world is mapped into a node, each action that can be performed in the current
state of the world becomes an edge of the node

A world can represent for example a machine (mostly a virtual one) where an
application is going to be run, an algorithm or anything

For exploring, the initial node must be provided with at least one edge, in
most cases this would be a clean virtual machine with a 'Launch application'
edge.

Base logic:

    if world current state is unidentified:
        create a node that represents it
        current edge head becomes the new node
    else
        current edge head becomes the node identifiable with current world
        pick one uninvestigated edge of the current node and explore it
        (if not reachable from current node, reset the world)

    if there's no uninvestigated edge left
        we're done

'''

import json, datetime, logging

LOGGER = logging.getLogger('root.' + __name__)

def _find_predecessor(history):
    '''
    Returns the node used to enter the last node in the history array
    '''
    if len(history) == 0:
        return None

    tail = history[-1]
    start_search = False
    for node in reversed(history):
        if not node is tail:
            start_search = True
        if start_search == True and not node is tail:
            return node
    return None


def _find_predecessor_in_edge_array(history):
    '''
    Same as find_predecessor but it receives an array of edges
    '''
    if len(history) == 0:
        return None

    tail = history[-1].tail
    start_search = False
    for edge in reversed(history):
        if not edge.tail is tail:
            start_search = True
        if start_search == True and not edge.tail is tail:
            return edge
    return None


def _log_unexpected_destination(edge, actual_node, current_path):
    '''
    Log troubleshooting info when an unexpected node is reached
    '''
    if actual_node:
        LOGGER.warn("It was expeted to reach node %s but instead node %s "
                    "was reached", edge.head.name, actual_node.name)
    else:
        LOGGER.warn("It was expeted to reach node %s but instead an "
                    "unidentified node was reached", edge.head.name)

    history = ""
    for an_edge in current_path:
        history += '\t"%s" -> "%s" -> "%s"\n' % (an_edge.tail.name,
                                                 an_edge.name,
                                                 an_edge.head)
    LOGGER.warn("Path walked was: \n%s", history)
    for a_path in edge.known_paths:
        history = ""
        for an_edge in a_path:
            history += '\t"%s" -> "%s" -> "%s"\n' % (an_edge.tail.name,
                                                     an_edge.name,
                                                     an_edge.head)
        LOGGER.warn("Known path of edge %s: \n%s", edge.name, history)

def log_invalid_paths(edge):
    '''
    Print to log all the known invalid paths for debugging purposes
    '''
    LOGGER.debug("Invalid known paths:")
    for a_path in edge.known_invalid_paths:
        for a_step in a_path:
            LOGGER.debug("\t%s.%s => %s", a_step.tail.name,
                                          a_step.name,
                                          a_step.head.name)

def log_invalid_path(a_path):
    '''
    Print to log the given invalid paths for debugging purposes
    '''
    LOGGER.debug("Invalid path:")
    for a_step in a_path:
        LOGGER.debug("\t%s.%s => %s", a_step.tail.name,
                                      a_step.name,
                                      a_step.head.name)

def _qualified_edge_name(edge, base_names):
    '''
    Store original names and derive destinations based on the original
    names, otherwise an edge name will end up like cancel__welcome__eula
    but instead we want cancel__welcome and cancel__eula
    '''
    base_name = base_names.get(edge.name, edge.name)
    if edge.head:
        qualified_name = ("%s__%s" % (base_name, edge.head.name)).capitalize()
    else:
        qualified_name = edge.name
    base_names[qualified_name] = base_name
    return qualified_name

class Crawler(object):
    '''
    Current limitations:
        it will do a 'light pass' trying to visit every node and trigger every
        edge, however it wont be exhaustive as to for example try same edge but
        coming from different paths
    '''

    def __init__(self, world, graph):
        self._world = world
        self._graph = graph
        self.ignorable_edges = [] #2-tuple of node-edge indexes to ignore
        self.timeline = []

    def where_am_i(self):
        '''
        Returns the node that identifies the current world state if there is
        one, None otherwise
        '''
        for node in self._graph.nodes:
            if node.is_in(self._world):
                return node
        return None

    def create_node(self, current_path):
        '''
        Shorthand for creating a node that represents the current state of the
        world
        '''
        node = self._graph.create_node(name=None, world=self._world)
        if len(current_path) > 0:
            for edge in node.edges:
                edge.add_known_path(current_path)
        LOGGER.info("Node created for state %s", str(node))
        return node

    def _filter_edges(self, edges):
        '''
        Returns True if the last edge in the edges array should be ignored,
        False otherwise
        This function is used for filtering out which edges should, for some
        reason, be ignored and not performed while crawling
        '''
        edge = edges[-1]

        node_index = self._graph.nodes.index(edge.tail)
        edge_index = self._graph.nodes[node_index].edges.index(edge)

        if edges in edge.known_invalid_paths:
            print "Invalid path rejected."
            return True

        if (node_index, edge_index) in self.ignorable_edges:
            LOGGER.debug("will ignore edge %s", str((node_index, edge_index)))
            return True
        else:
            return False

    def _notify_update(self, node):
        '''
        If there's a listener for update notification then it will be called
        Used for progress reporting
        '''
        update_notify = getattr(self._graph, 'on_update', None)
        if update_notify:
            update_notify(node)

    def _dump_path(self, path):
        '''
        Debug print a path
        '''
        for edge in path:
            print "\t%s->%s" % (edge.tail.name, edge.name)

    def save_timeline(self, where):
        '''
        Saves the timeline of actions for further processing
        '''
        events = []
        for event in self.timeline:
            if 'arrival' in event:
                arrives = event['arrival'].strftime("%H:%M:%S.%f")
                arrives_at = event['at'].name
            else:
                arrives = "Unknown"
                arrives_at = "Unknown"
            if 'departure' in event:
                departs = event['departure'].strftime("%H:%M:%S.%f")
                departs_from = event['from'].name
            else:
                departs = "Unknown"
                departs_from = "Unknown"
            events.append({'arrival': arrives, 'at': arrives_at,
                           'departure': departs, 'from': departs_from})

        with open(where + '/timeline.json', 'wb') as the_file:
            json.dump(events, the_file)


    def _get_path_to_unexplored_edge(self, current_node):
        '''
        Returns a path (array of edges) to an unexplored edge
        Returns an empty array if no path is found
        '''
        unexplored_edges = []
        for node_index in range(len(self._graph.nodes)):
            for edge_index in range(len(self._graph.nodes[node_index].edges)):
                edge = self._graph.nodes[node_index].edges[edge_index]
                if edge.head is None:
                    if not (node_index, edge_index) in self.ignorable_edges:
                        unexplored_edges.append(edge)

        needs_reset = False
        path = current_node.path_to(None, self._filter_edges)
        if len(path) == 0:
            needs_reset = True
        for candidate_edge in path:
            if candidate_edge.tail is self._graph.nodes[0]:
                needs_reset = True
                break
        #no path from current node, try from start
        if needs_reset:
            path = self._graph.nodes[0].path_to(None, self._filter_edges)

        if len(path) == 0 and len(unexplored_edges) > 0:
            #if there are known paths to them it should use it, as the breadth
            #first can miss paths with the blacklisting logic
            #the fact that the edge exists means that there is a route to it
            path = (unexplored_edges[0].shortest_known_path() +
                    [unexplored_edges[0]])
            LOGGER.info("No more paths solved by breadthfirst, returning "
                        "known one to %s->%s",
                        unexplored_edges[0].tail.name,
                        unexplored_edges[0].name)
            if len(path) == 0:
                raise RuntimeError("Known path to node is not know, "
                                   "internal inconsistency error")
            else:
                self._dump_path(path)

        return path

    def _traverse_path(self, path, history, current_path):
        '''
        Perform each edge in the given path (an array of edges), verifies that
        each edge head is reached.
        Adds the given path to the edge list of known invalid paths
        Returns True if successfully traversed all the path, if something
        unexpected happened it returns the last performed edge and current
        node
        '''
        for edge in path[:-1]:
            event = {'departure': datetime.datetime.now(),
                     'from': edge}
            self.timeline.append(event)
            edge.perform(self._world)
            history.append(edge.head)
            if edge.head.is_in(self._world):
                current_path.append(edge)
                edge.add_known_path(current_path)
            else:
                # paranoia: if current path is a known path to this edge
                # then is an undeterministic behaviour, abort
                actual_node = self.where_am_i()
                if current_path in edge.known_paths:
                    _log_unexpected_destination(edge,
                                                actual_node,
                                                current_path)
                    raise Exception("Unexpected / undetermined node")
                LOGGER.debug("Edge %s has invalid path %s",
                             edge,
                             str(current_path))
                LOGGER.debug("Current state after invalid path is %s",
                             str(actual_node))
                log_invalid_paths(edge)
                log_invalid_path(current_path)
                edge.add_known_invalid_path(current_path + [edge])
                return edge, actual_node

        event = {'departure': datetime.datetime.now(),
                 'from': path[-1]}
        self.timeline.append(event)
        path[-1].perform(self._world)
        current_path.append(path[-1])

        return True

    def explore(self, current_node=None, current_edge=None):
        '''
        Explore this world from the current state, initial node and edges can
        specify we're continuing an exploration from a given point.
        '''
        crawl = True
        LOGGER.info("Started exploration, current node is %s, current edge is"
                    " %s", str(current_node), str(current_edge))
        #FIXME: should use better names for history and current path...
        history = [] #nodes visited until reset
        current_path = [] #edges performed until reset
        base_names = {} #original edge names

        while crawl:
            this_node = self.where_am_i()
            if this_node is None:
                this_node = self.create_node(current_path)
                self._notify_update(this_node)

            if current_edge:
                if current_edge.head:
                    raise Exception("Internal consistency error, "
                                    "edge already has a head")

                current_edge.head = this_node
                if current_edge.return_to_caller == True:
                    current_edge.name = _qualified_edge_name(current_edge,
                                                             base_names)
                    LOGGER.debug("Edge w RTC renamed as %s", current_edge.name)
                    print "Current path is:"
                    self._dump_path(current_path)
                    current_edge.return_to_caller = None

                current_edge.add_known_path(current_path)
                self._notify_update(current_edge.tail)

            current_node = this_node
            history.append(current_node)

            while True:
                current_edge = None
                path = self._get_path_to_unexplored_edge(current_node)
                if len(path) == 0:
                    crawl = False
                    break

                #if needs reset:
                if path[0].tail is self._graph.nodes[0] and len(history) > 1:
                    self.timeline.append("reboot")
                    self._world.reset()
                    history = []
                    current_path = []

                result = self._traverse_path(path, history, current_path)
                if result == True:
                    current_edge = path[-1]
                    break
                else:
                    edge, actual_node = result
                    #edge has multiple destinations, create new one with the
                    #current destination if it does not already exists
                    #FIXME: timeline, history and so
                    already_exists = False
                    if actual_node:
                        for other_edge in edge.tail.edges:
                            if other_edge.head == actual_node:
                                already_exists = True
                                current_path.append(other_edge)
                                break
                    if already_exists:
                        #as it can get stuck in a loop, we reset to initial
                        #node and rely on the blacklisted path
                        current_node = self._graph.nodes[0]
                    else:
                        old_name = edge.name
                        new_edge = edge.clone()
                        edge.name = _qualified_edge_name(edge, base_names)
                        new_edge.head = actual_node
                        current_path.append(new_edge)
                        if actual_node:
                            new_edge.name = _qualified_edge_name(new_edge,
                                                                 base_names)
                            new_edge.add_known_path(current_path)
                            LOGGER.info("New edge created as %s", new_edge)
                            self._notify_update(edge.tail)
                            current_node = actual_node
                        else:
                            current_edge = new_edge
                            new_edge.name = old_name
                            new_edge.return_to_caller = True
                            LOGGER.info("New edge created as %s", new_edge)
                            self._notify_update(edge.tail)
                            break

