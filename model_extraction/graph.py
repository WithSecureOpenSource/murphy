'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Basic graph structures for directed graphs
'''
import re

def breadth_first(node, is_destination, prune_edge=None):
    '''
    Returns the first edge that meets the given is_destination(node) function,
    a prunning function prune_edge(edge) can be provided for filter out edges
    that should not be considered. Note that incomplete edges (edges lacking
    a head) will fail with an exception, if working with partially defined
    edges it is neccessary to provide a prune_edge function that filters them
    out, see self tests for examples.
    It does traverse the graph using the breadth first search.
    See http://en.wikipedia.org/wiki/Breadth-first_search
    '''

    start_node = object()

    queue = [[start_node]]
    marks = []
    marks.append(node)
    result = []

    while len(queue) > 0:
        path = queue.pop(0)
        if path[-1] is start_node:
            edges = node.edges
        else:
            edges = path[-1].head.edges
        for edge in edges:
            if prune_edge is None or prune_edge(path[1:] + [edge]) == False:
                if is_destination(edge):
                    result = path[1:] + [edge]
                    break
                elif not edge.head in marks:
                    queue.append(path + [edge])
                    marks.append(edge.head)
        if len(result) > 0:
            break

    return result


class Edge(object):
    '''
    An edge of a graph, defined as
    tail -> edge -> head
    '''
    def __init__(self, tail, name, head=None):
        self.tail = tail
        self.name = name
        self.head = head
        self.return_to_caller = None
        self.known_paths = []
        self.known_invalid_paths = []

    def __str__(self):
        return "Edge %s (%s)" % (self.name, self.tail.name)


    def add_return_to_caller(self, head):
        '''
        Converts this edge to a 'return to caller' type and adds a new edge
        to the given returning node
        '''
        self.return_to_caller = 'Yes'
        new_edge = self.clone()
        new_edge.head = head
        return new_edge


    def add_known_path(self, path):
        '''
        Adds the given path to the list of known paths valid for performing
        this edge
        '''
        '''
        if not path[-1].head is self.tail:
            print "Valid known path for %s:" % self.name
            for e in path:
                print "%s->%s" % (e.tail.name, e.name)
                if e.head:
                    print "\t%s" % e.head.name
                else:
                    print "Head not set yet"
            print "My tail is %s" % str(self.tail)
            if self.tail:
                print "My tail name is %s" % str(self.tail.name)
            raise RuntimeError("Internal inconsistency error, trying to set a known path that does not lead to the tail of this edge")
        '''    
        if not path in self.known_paths:
            self.known_paths.append(path[:])


    def add_known_invalid_path(self, path):
        '''
        Adds the given path to the list of known invalid paths, tells when the
        edge cannot be executed
        '''
        if not path in self.known_invalid_paths:
            self.known_invalid_paths.append(path[:])


    def shortest_known_path(self):
        '''
        Returns the shortest known path to this edge
        '''
        best = -1
        for path in self.known_paths:
            if best == -1 or len(path) < len(self.known_paths[best]):
                best = self.known_paths.index(path)

        if best != -1:
            return self.known_paths[best]
        else:
            return []


    def clone(self):
        '''
        Returns a copy of this edge with modified name, the new name format is
        old name (x) where x will be the next in sequence so if this edge is
        'element 1', the cloned one will be 'element 1 (1)', 'element 1 (2)'
        and so on.
        Subclasses should call this method and clone any additional field they
        add.
        '''

        #find appropriate name
        candidate = 2
        base_name = self.name
        number = re.findall("\\(([^\\)]+)\\)", base_name)
        if len(number) == 1 and base_name.endswith('(%s)' % number):
            base_name = base_name[:-len('(%s)' % number)].strip()

        candidate_name = ""
        while True:
            candidate_name = "%s (%s)" % (base_name, candidate)
            in_use = False
            for edge in self.tail.edges:
                if edge.name == candidate_name:
                    in_use = True
                    break
            if in_use == False:
                break
            candidate += 1
        new_one = self.tail.create_edge(candidate_name, self.head)
        new_one.return_to_caller = self.return_to_caller
        new_one.tail.edges.append(new_one)
        return new_one


class Node(object):
    '''
    A node in a graph
    '''

    def __init__(self, name):
        self.name = name
        self.edges = []
        self.graph = None


    def create_edge(self, name, head=None):
        '''
        Creates an Edge with this node as it's tail and the given one as
        it's head.
        The name of the edge cannot be the same as other edges of this
        node.
        '''
        edge = Edge(self, name, head)
        self.edges.append(edge)
        return edge

    def get_edge(self, name):
        for edge in self.edges:
            if edge.name == name:
                return edge

        return None

    def path_to(self, destination, filter=None):
        '''
        Returns a list of edges to traverse as to reach destination from this
        node, if there's no route or destination is the current node an empty
        array is returned.
        Default implementation is a breadth first search.
        '''
        if filter:
            return breadth_first(self,
                                 lambda edge: edge.head == destination,
                                 filter)
        else:
            return breadth_first(self, lambda edge: edge.head == destination)

    def clone(self):
        '''
        Returns a copy of this node with modified name, the new name format is
        old name (x) where x will be the next in sequence so if this edge is
        'node 1', the cloned one will be 'node 1 (1)', 'node 1 (2)'
        and so on.
        Edges will be creaated with the same name as this node, their tails
        will point to the cloned node but their heads will be set to None
        Subclasses should call this method and clone any additional field they
        add.
        '''
        #find appropriate name
        candidate = 2
        base_name = self.name
        number = re.findall("\\(([^\\)]+)\\)", base_name)
        if len(number) == 1 and base_name.endswith('(%s)' % number):
            base_name = base_name[:-len('(%s)' % number)].strip()

        candidate_name = ""
        while True:
            candidate_name = "%s (%s)" % (base_name, candidate)
            in_use = False
            for a_node in self.graph.nodes:
                if a_node.name == candidate_name:
                    in_use = True
                    break
            if in_use == False:
                break
            candidate += 1
        new_one = self.graph.create_node(candidate_name)
        for edge in self.edges:
            new_one.create_edge(edge.name)
        return new_one

    def __str__(self):
        output = "Node %s" % self.name
        output += " (%s)" % len(self.edges)
        for edge in self.edges:
            head_name = None
            if edge.head:
                head_name = edge.head.name
            output += '\n\t->%s->%s' % (str(edge.name), str(head_name))
        return output

    def as_graphviz(self):
        for edge in self.edges:
            print '\t"%s" -> "%s" [label="%s"];' % (edge.tail.name, edge.head.name, edge.name)

            
class Graph(object):
    '''
    Holds the collection of Nodes that composes a graph
    '''
    def __init__(self):
        self.nodes = []

    def create_node(self, name):
        '''
        Creates a node object, name must be unique
        '''
        node = Node(name)
        node.graph = self
        self.nodes.append(node)
        return node

    def get_node(self, name):
        '''
        Returns the node with the given name
        '''
        for node in self.nodes:
            if node.name == name:
                return node

        return None

    def as_graphviz(self):
        print 'digraph finite_state_machine {\n\trankdir=TB;\n\tsize="68,65";\n\tnode [shape=rectangle];';
        for node in self.nodes:
            node.as_graphviz()
        print "}"
        
    def dump_graph(self, dump_known_paths=False):
        for node in self.nodes:
            print "Node %s" % node.name
            for edge in node.edges:
                if edge.head:
                    dest = edge.head.name
                else:
                    dest = "Unknown"
                print "\tEdge %s -> %s" % (edge.name, dest)
                if dump_known_paths:
                    for path in edge.known_paths:
                        a_path = ""
                        for step in path:
                            a_path += ",[%s -> %s -> %s]" % (step.tail.name,
                                                             step.name,
                                                             step.head.name)
                        print "\t\tKnown path: %s" % a_path[1:]

    def __str__(self):
        output = ""
        for node in self.nodes:
            output += str(node) + "\n"
        return output
