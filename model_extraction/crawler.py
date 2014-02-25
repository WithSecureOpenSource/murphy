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
        
TODO: return to caller logic could be implemented in derived class as to keep
the core implementation simple and as generic as possible
'''

import logging
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
        LOGGER.warn(("It was expeted to reach node %s but instead node %s "
                    "was reached") % (edge.head.name, actual_node.name))
    else:
        LOGGER.warn(("It was expeted to reach node %s but instead an "
                    "unidentified node was reached") % (edge.head.name,
                                                        actual_node.name))
    
    history = ""
    for an_edge in current_path:
        history += '\t"%s" -> "%s" -> "%s"\n' % (an_edge.tail.name,
                                                 an_edge.name,
                                                 an_edge.head)
    LOGGER.warn("Path walked was: \n%s" % history)
    for a_path in edge.known_paths:
        history = ""
        for an_edge in a_path:
            history += '\t"%s" -> "%s" -> "%s"\n' % (an_edge.tail.name,
                                                     an_edge.name,
                                                     an_edge.head)
        LOGGER.warn("Known path of edge %s: \n%s" % (edge.name,
                                                     history))
    
    
def print_invalid_paths(edge):
    print "Invalid known paths:"
    for a_path in edge.known_invalid_paths:
        for a_step in a_path:
            print ("\t" + a_step.tail.name + "." + a_step.name
                   + " => " + a_step.head.name)  

def print_invalid_path(a_path):
    print "Invalid path:"
    for a_step in a_path:
        print ("\t" + a_step.tail.name + "." + a_step.name
               + " => " + a_step.head.name)  
    
class Crawler(object):
    '''
    Current limitations:
        it cannot identify when same state can be reached from different points
        and from that state will return to different places depending on
        where does it comes from, for example a popup dialog that can be
        launched from different places and returns to the caller.
        for now, avoid such situations by ignoring the edge that would trigger
        the recognition of it
    '''

    def __init__(self, world, graph):
        self._world = world
        self._graph = graph
        self.ignorable_edges = [] #2-tuple of node-edge indexes to ignore
        
        
    def where_am_i(self):
        '''
        Returns the node that identifies the current world state if there is
        one, None otherwise
        '''
        for node in self._graph.nodes:
            if node.is_in(self._world):
                return node
        return None

    
    def create_node(self):
        '''
        Shorthand for creating a node that represents the current state of the
        world
        '''
        node = self._graph.create_node(self._world)
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

        # FIXME: remove the return to caller as it is...
        '''
        if edge.return_to_caller == 'Yes':
            predecessor_edge = _find_predecessor_in_edge_array(edges)
            if predecessor_edge and edge.head is predecessor_edge.tail:
                pass
            else:
                LOGGER.debug(("will ignore edge %s (%s) as it is a return to "
                              "caller scenario") % (edge.name, edge.head.name))
                return True
        '''
        if edges in edge.known_invalid_paths:
            print "Invalid path rejected."
            return False
        
        if (node_index, edge_index) in self.ignorable_edges:
            LOGGER.debug("will ignore edge %s" % str((node_index, edge_index)))
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
    
    
    def explore(self, current_node=None, current_edge=None):
        '''
        Explore this world from the current state, initial node and edges can
        specify we're continuing an exploration from a given point.
        '''
        crawl = True
        LOGGER.info(("Started exploration, current node is %s, current edge is"
                     " %s") % (str(current_node), str(current_edge)))
        history = []
        current_path = []
        
        base_names = {}
        
        while crawl:
            this_node = self.where_am_i()
            if this_node is None:
                this_node = self.create_node()
                LOGGER.info("Node created for state %s" % str(this_node))
                self._notify_update(this_node)
                
            if current_edge:
                if current_edge.head:
                    raise Exception("Internal consistency error, "
                                    "edge already has a head")
                
                current_edge.head = this_node
                if current_edge.return_to_caller == True:
                    LOGGER.debug("Edge with RTC attrib %s" % current_edge.name)
                    current_edge.name = (current_edge.name + "__" +
                                         this_node.name).capitalize()
                    LOGGER.debug("Edge renamed as %s" % current_edge.name)
                    current_edge.return_to_caller = None
                    
                current_edge.add_known_path(current_path)
                self._notify_update(current_edge.tail)
                
            current_node = this_node
            history.append(current_node)
            find_path = True
            while find_path:
                find_path = False
                actual_node = None
                #get the path to nearest unvisited edge
                needs_reset = False
                path = current_node.path_to(None, self._filter_edges)
                if len(path) == 0 and not current_node is self._graph.nodes[0]:
                    needs_reset = True
                    LOGGER.info("No reachable node from here, resetting world")
                    path = self._graph.nodes[0].path_to(None,
                                                        self._filter_edges)
                elif len(history) > 1 and current_node is self._graph.nodes[0]:
                    needs_reset = True
                    LOGGER.info("Reached initial state again, resetting world")
                    path = self._graph.nodes[0].path_to(None,
                                                        self._filter_edges)

                #FIXME: TODO: path solving avoiding a node (or a list of nodes)
                for candidate_edge in path[1:]:
                    if candidate_edge.tail is self._graph.nodes[0]:
                        needs_reset = True
                        LOGGER.info("Reached initial state again (thru path solving), resetting world")
                        path = self._graph.nodes[0].path_to(None,
                                                            self._filter_edges)
                    
                if len(path) == 0:
                    crawl = False
                else:
                    if needs_reset:
                        self._world.reset()
                        history = []
                        current_path = []
                    
                    perform_last_edge = True    
                    for edge in path[:-1]:
                        current_edge = edge
                        edge.perform(self._world)
                        current_path.append(current_edge)
                        history.append(edge.head)
                        if edge.head.is_in(self._world):
                            edge.add_known_path(current_path)
                        else:
                            actual_node = self.where_am_i()
                            # if current path is a known path to this edge =>
                            # undeterministic behaviour, abort
                            if current_path in edge.known_paths:
                                _log_unexpected_destination(edge,
                                                            actual_node,
                                                            current_path)
                                raise Exception("Unexpected /"
                                                " undetermined node")
                            
                            #this node took us to another place...
                            LOGGER.debug("Edge %s has invalid path %s" % (
                                 edge, str(current_path)))
                            print_invalid_paths(edge)
                            print_invalid_path(current_path)
                            edge.add_known_invalid_path(current_path)

                            alternate_edge = None
                            if actual_node:
                                for candidate in edge.tail.edges:
                                    if candidate.head == actual_node:
                                        alternate_edge = candidate
                                        break
                                     
                            if alternate_edge:
                                #we're in a known node, find a path from here
                                LOGGER.info("Current edge switch to %s" % 
                                            alternate_edge)
                                current_node = actual_node
                                current_edge = alternate_edge
                                find_path = True
                            else:
                                new_edge = edge.clone()
                                #FIXME: base name must be parent name.edge name!
                                base_name = base_names.get(edge.name, edge.name)
                                edge.name = (base_name + "__" +
                                             edge.head.name).capitalize()
                                base_names[edge.name] = base_name
                                current_node = actual_node
                                current_edge = new_edge
                                if actual_node:
                                    new_edge.name = (base_name + "__" +
                                                  actual_node.name).capitalize()
                                    base_names[new_edge.name] = base_name
                                    new_edge.head = actual_node
                                    new_edge.add_known_path(current_path)
                                    find_path = True
                                else:
                                    new_edge.head = None
                                    new_edge.return_to_caller = True
                                    find_path = False
                                    perform_last_edge = False
                                LOGGER.info("New edge created as %s" % new_edge)
                                
                            
                            self._notify_update(edge.tail)
                            break
                            
                    if find_path == False and perform_last_edge == True:
                        path[-1].perform(self._world)
                        current_edge = path[-1]
                        current_path.append(current_edge)


        