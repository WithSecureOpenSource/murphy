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

import json, datetime, logging
from model_extraction import csv_unicode

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

def _procmon_time_to_timestamp(time_as_string):
    '''
    Convenient converter from process monitor time string to python time
    '''
    hour, mins, secs = time_as_string.split(":")
    secs, millis = secs.split(",")
    millis = millis[:6]
    return datetime.time(int(hour), int(mins), int(secs), int(millis))

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

    def explore(self, current_node=None, current_edge=None):
        '''
        Explore this world from the current state, initial node and edges can
        specify we're continuing an exploration from a given point.
        '''
        crawl = True
        LOGGER.info("Started exploration, current node is %s, current edge is"
                    " %s", str(current_node), str(current_edge))
        history = []
        current_path = []

        base_names = {}

        while crawl:
            this_node = self.where_am_i()
            if this_node is None:
                this_node = self.create_node()
                LOGGER.info("Node created for state %s", str(this_node))
                self._notify_update(this_node)

            if current_edge:
                if current_edge.head:
                    raise Exception("Internal consistency error, "
                                    "edge already has a head")

                current_edge.head = this_node
                if current_edge.return_to_caller == True:
                    LOGGER.debug("Edge with RTC attrib %s", current_edge.name)
                    current_edge.name = (current_edge.name + "__" +
                                         this_node.name).capitalize()
                    LOGGER.debug("Edge renamed as %s", current_edge.name)
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
                        LOGGER.info("Reached initial state again (thru path "
                                    "solving), resetting world")
                        path = self._graph.nodes[0].path_to(None,
                                                            self._filter_edges)

                if len(path) == 0:
                    crawl = False
                else:
                    if needs_reset:
                        self.timeline.append("reboot")
                        self._world.reset()
                        history = []
                        current_path = []

                    perform_last_edge = True
                    for edge in path[:-1]:
                        current_edge = edge
                        event = {'departure': datetime.datetime.now(),
                                 'from': edge}
                        self.timeline.append(event)
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
                            LOGGER.debug("Edge %s has invalid path %s",
                                         edge,
                                         str(current_path))
                            log_invalid_paths(edge)
                            log_invalid_path(current_path)
                            edge.add_known_invalid_path(current_path)

                            alternate_edge = None
                            if actual_node:
                                for candidate in edge.tail.edges:
                                    if candidate.head == actual_node:
                                        alternate_edge = candidate
                                        break

                            if alternate_edge:
                                #we're in a known node, find a path from here
                                LOGGER.info("Current edge switch to %s",
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
                                LOGGER.info("New edge created as %s", new_edge)


                            self._notify_update(edge.tail)
                            break

                    if find_path == False and perform_last_edge == True:
                        event = {'departure': datetime.datetime.now(),
                                 'from': path[-1]}
                        self.timeline.append(event)
                        path[-1].perform(self._world)
                        current_edge = path[-1]
                        current_path.append(current_edge)

    def _add_trace_to_edge(self, edge, trace_index):
        '''
        Adds a trace, meaning the series of steps used with that index in
        the timeline to pair with the log info
        '''
        steps = []
        for i in range(trace_index - 1, -1, -1):
            if self.timeline[i] == 'reboot':
                break
            timeline_edge = self.timeline[i]['from']
            steps.insert(0, "%s.%s" % (timeline_edge.tail.name,
                                       timeline_edge.name))

        if not 'traces' in edge.logs['instrumentation']:
            edge.logs['instrumentation']['traces'] = {}
        edge.logs['instrumentation']['traces'][trace_index] = steps
        
    def _add_logged_event_to_edge(self, edge, operation, trace_index, row):
        '''
        Adds the given row of data to the given edge as instrumentation captured
        data
        '''
        if not 'instrumentation' in edge.logs:
            edge.logs['instrumentation'] = {}
        if not operation in edge.logs['instrumentation']:
            edge.logs['instrumentation'][operation] = {}
        if not trace_index in edge.logs['instrumentation'][operation]:
            edge.logs['instrumentation'][operation][trace_index] = []
            self._add_trace_to_edge(edge, trace_index)
        edge.logs['instrumentation'][operation][trace_index].append(row)

    def _correlate_log(self, csv_reader, edge, until, timeline_index):
        '''
        Adds events from the given log to the corresponding edge, times are
        matched from the crawler timeline against the edge it was executed.
        In this context edge represents what it was executed and until the
        timestamp of the next edge execution
        '''
        ignorable_processes = ["mobsync.exe", "wmpnetwk.exe", "spoolsv.exe",
                               "smss.exe", "lsm.exe", "wmpnscfg.exe",
                               "python.exe", "cmd.exe", "wermgr.exe",
                               "conhost.exe", "tvnserver.exe", "Explorer.EXE",
                               "Procmon.exe", "Procmon64.exe", "svchost.exe",
                               "DllHost.exe", "System", "taskhost.exe",
                               "services.exe", "lsass.exe"]
        ignorable_path = "C:\\Users\\testuser\\AppData\\Local\\"
        last_message = ""
        headers = csv_reader.next()
        if headers is None:
            return (None, None)
        #typical header:
        #['Time of Day', 'Process Name', 'PID', 'Operation', 'Path', 'Result',
        # 'Detail']

        while True:
            try:
                row = csv_reader.next()
            except StopIteration:
                break
            time, process, _, operation, path, _, _ = row
            if process in ignorable_processes:
                pass
            elif path.startswith(ignorable_path):
                pass
            else:
                timestamp = _procmon_time_to_timestamp(time)
                if timestamp <= until:
                    message = "%s %s %s" % (process, operation, path)
                    if operation == "WriteFile" and not edge is None:
                        self._add_logged_event_to_edge(edge,
                                                       operation,
                                                       timeline_index,
                                                       row)
                        if message != last_message:
                            print "\t%s: %s" % (time, message)
                        last_message = message
                    elif operation.startswith("TCP") and not edge is None:
                        self._add_logged_event_to_edge(edge,
                                                       operation,
                                                       timeline_index,
                                                       row)
                        if message != last_message:
                            print "\t%s: %s" % (time, message)
                        last_message = message
                    elif operation == "RegSetValue" and not edge is None:
                        self._add_logged_event_to_edge(edge,
                                                       operation,
                                                       timeline_index,
                                                       row)
                        if message != last_message:
                            print "\t%s: %s" % (time, message)
                        last_message = message
                else:
                    last_message = ""
                    while True:
                        timeline_index += 1
                        if timeline_index == len(self.timeline):
                            return (None, None)
                        if self.timeline[timeline_index] == "reboot":
                            pass #print "Reset"
                        elif self.timeline[timeline_index]['departure'].time() > timestamp:
                            until = self.timeline[timeline_index]['departure'].time()
                            if (timeline_index > 2 and
                              self.timeline[timeline_index - 1] == "reboot"):
                                edge = self.timeline[timeline_index - 2]['from']
                                print edge.tail.name + "." + edge.name
                                print "Reset"
                            else:
                                edge = self.timeline[timeline_index - 1]['from']
                                print edge.tail.name + "." + edge.name
                            break
                        else:
                            edge = self.timeline[timeline_index - 1]['from']
                            print edge.tail.name + "." + edge.name
        return (edge, timeline_index)


    def correlate_events(self):
        '''
        Matches log events to edge executions
        '''
        timeline_index = 0
        until = self.timeline[0]['departure'].time()
        edge = None
        # print "Logs in world: %s" % str(self._world.event_logs)
        # print
        print "Will try to correlate events from log with timeline"
        print "Logs are %s" % str(self._world.event_logs)
        for log in self._world.event_logs:
            with open(log, 'r') as log_file:
                csv_reader = csv_unicode.UnicodeReader(log_file,
                                                       encoding="utf-8-sig")
                (edge, timeline_index) = self._correlate_log(csv_reader,
                                                           edge,
                                                           until,
                                                           timeline_index)
