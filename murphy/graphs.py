'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

This module is for generating the graph files (dot) of the application flow
'''

from murphy.path_tested import TestedPath
import re

class Graphs():
    '''
    This class encapsulates the creation of the dot and map files of
    GraphViz.
    '''
    #FIXME: parametrize coloring
    START_BOX_COLOR = "green"
    IMPLEMENTED_COLOR = "black"
    UNVISITED_COLOR = IMPLEMENTED_COLOR
    UNIMPL_COLOR = "aquamarine"
    UNDEFINED_COLOR = "aquamarine"
    VISITED_COLOR = "blue"
    ERROR_COLOR = "red"
    FAILED_COLOR = "gold1"
    
    start_view = ('\t"%(view)s" [color=' + START_BOX_COLOR + ' style=filled ' +
                                 'URL="\'%(view)s\'"];\n')
    impl_view = ('\t"%(view)s" [color=' + IMPLEMENTED_COLOR + 
                 ' URL="\'%(view)s\'"];\n')
    #verb targets a view that is not defined
    unimpl_view = ('\t"%(view)s" [color=' + UNIMPL_COLOR + ' style=filled' +
                    ' URL="\'%(view)s\'"];\n')
    #verb does not have destination (goes to)
    unknown_view = ('\t"%(view)s" [label="???" color=' + UNDEFINED_COLOR + 
                    ' style=filled URL="\'%(view)s\'"];\n')
    #relationship
    relationship = '\t"%(view)s" -> "%(dest)s" %(rel)s;\n'
    #verb lacks 'how'
    undef_verb = ('[label="%(verb)s" color=' + UNDEFINED_COLOR + 
                  ' URL="\'%(view)s.%(verb)s\'"]')
    impl_verb = ('[label="%(verb)s" color=' + IMPLEMENTED_COLOR +
                 ' URL="\'%(view)s.%(verb)s\'"]')
 
    dot_head = ('digraph finite_state_machine { \n' +
                '\trankdir=TB;\n' +
                '\tsize="68,65";\n' +
                '\tnode [shape=rectangle];\n' +
                '%s}')
                
    def __init__(self, views):
        self._views = views


    def generate_from_spider(self, starting_view, tags=None):
        '''
        Generates the graph starting from the specified view, the algorithm
        will just spider thru all reachable views from the starting ones
        Tags can be a dictionary with name:value pair that filters out
        the edges that has tags but not with the requested value
        '''
        builder = _DotBuilder()

        start_def = Graphs.start_view % { 'view': starting_view }
        builder.add_definition(starting_view, start_def)

        view_name = starting_view
        
        pending_views = []
        processed_views = []
        
        while True:
            rel_obj = _Relationship(self._views, view_name, None)
            if view_name in self._views:
                view = self._views[view_name]
                builder.add_relationship(rel_obj)
                for verb_name in view['verbs'].keys():
                    verb = view['verbs'][verb_name]
                    
                    filtered_out = False
                    
                    if not tags is None and 'tags' in verb:
                        for tag, value in verb['tags'].items():
                            if tag in tags and tags[tag] != value:
                                filtered_out = True
                                break
                
                    if not filtered_out:
                        rel_obj = _Relationship(self._views, view_name, verb_name)
                        builder.add_relationship(rel_obj)
                        
                        if 'goes to' in verb and verb['goes to'] != '':
                            target = verb['goes to']
                            if not target in processed_views:
                                pending_views.append(target)
            
            processed_views.append(view_name)
            if len(pending_views) > 0:
                view_name = pending_views.pop(0)
            else:
                break
            
        return builder.get_dot_text()
       

    def merge_coverage(self, src_dot, visits):
        '''
        Given the dot file content paint with colors the visits provided in
        visits array, the expected format for visits is the one provided by
        Executor.get_trip
        Returns the content of a dot file ready to be saved
        '''
        #FIXME: weak implementation, full dot parser needed but works for now
        #same goes for the generator
        # sample lines:
        # "Clean Machine" [color=black URL="'Clean Machine'"];
        # "Clean Machine" -> "Language Selection" [label="Run network installer"
        #   color=black URL="'Clean Machine.Run network installer'"];
        #TODO: superview path from base model *could* be painted?
        get_view = re.compile('"([^"]*)"')
        get_verb = re.compile('label="([^"]*)"')
        dot_lines = src_dot.split("\n")

        for step in visits:
            view = step.view_name
            verb = step.verb_name
            
            for i in range(len(dot_lines)):
                line = dot_lines[i]
                view_def = get_view.search(line)
                verb_def = get_verb.search(line)
                
                if verb_def:
                    if view_def.group(1) == view and verb_def.group(1) == verb:
                        dot_lines[i] = _paint_line(line, step.state)
                else:
                    if verb is None:
                        if not view_def is None:
                            
                            if view_def.group(1) == view:
                                dot_lines[i] = _paint_line(line, step.state)
                        
                            #superviews should be painted if their shadow view is painted
                            for superview in self._views.values():
                                if ('superview of' in superview['self'].HERE and
                                  superview['self'].HERE['superview of'] == view and
                                  view_def.group(1) == superview['self'].HERE['desc']):
                                    dot_lines[i] = _paint_line(line, step.state)
                    
                
        return "\n".join(dot_lines)


def _paint_line(dot_line, state):
    '''
    Paints the given line with the appropriate color for the given
    state, returns the formatted line as a string
    '''
    ret = dot_line
    color = re.search('(?P<color>color=[^ |\]]*)', dot_line).group("color")
    if state == TestedPath.ERROR:
        #paint it no matter the underlying color
        ret = dot_line.replace(color, "color=" + Graphs.ERROR_COLOR)
    elif state == TestedPath.FAIL:
        #paint if underlying color is not ERROR
        if color != "color=" + Graphs.ERROR_COLOR:
            ret = dot_line.replace(color, "color=" + Graphs.FAILED_COLOR)
    elif state == TestedPath.PASS:
        #paint only if underlying color is unvisited
        if color == "color=" + Graphs.UNVISITED_COLOR:
            ret = dot_line.replace(color, "color=" + Graphs.VISITED_COLOR)
    else:
        raise Exception("Unexpected state %s for painting" % state)
    
    return ret
        
    
class _Relationship():
    """Helper class for creating dot lines"""
    
    def __init__(self, views, view_name, verb_name):
        self._views = views
        self._source = view_name
        self._source_def = self._get_view_def(view_name)
        if verb_name is None:
            self._target = None
            self._target_def = None
            self._relationship = None
        else:
            self._target, self._target_def = self._get_target_def( view_name,
                                                                   verb_name )
            self._relationship = self._get_relationship_def( view_name,
                                                             verb_name,
                                                             self._target )
    @property
    def source(self):
        """Returns the source name of the relationship"""
        return self._source
        
    @property
    def source_def(self):
        """Returns the source definition of the relationship"""
        return self._source_def
    
    @property
    def target(self):
        """Returns the target name of the relationship"""
        return self._target
        
    @property
    def target_def(self):
        """Returns the target definition of the relationship"""
        return self._target_def
        
    @property
    def relationship(self):
        """Returns the relationship definition (a -> b [label])"""
        return self._relationship
        
    def _get_view_def(self, view_name):
        """Returns the definition of a known view, an unknown view is when
        a verb lacks it's destination (goes to)
        Use it for getting the view definition of the source view, do not use
        for the target view of a verb, for that case use _get_target_def
        instead
        """
        if not view_name in self._views:
            return Graphs.unimpl_view % {'view': view_name}
        else:
            return Graphs.impl_view % {'view': view_name}
    
    
    def _get_target_def(self, view_name, verb_name):
        """Returns the definition of the target view of a verb, it can be
        either defined, undefined or unknown (when the verb lacks a 'goes to'
        """
        verb = self._views[view_name]['verbs'][verb_name]
        if 'goes to' in verb:
            target = verb['goes to']
            target_def = self._get_view_def(target)
        else:
            target = view_name + "." + verb_name
            target_def = Graphs.unknown_view % {'view': target}
        return target, target_def
    
    
    def _get_relationship_def(self, view_name, verb_name, target):
        """Returns the relationship definition, the target parameter must be
        the one returned from a previous call to _get_target_def as it
        contemplates the case of the 'unknown' view
        """
        verb = self._views[view_name]['verbs'][verb_name]
        if 'goes to' in verb:
            if 'how' in verb:
                link = Graphs.impl_verb % { 'view': view_name,
                                            'verb': verb_name }
            else:
                link = Graphs.undef_verb % { 'view': view_name,
                                             'verb': verb_name }
        else:
            link = Graphs.undef_verb % { 'view': view_name,
                                         'verb': verb_name }
        return Graphs.relationship % { 'view': view_name,
                                           'dest': target,
                                           'rel': link }

class _DotBuilder():
    """Helper class for generating the dot files"""
    
    def __init__(self):
        self._definitions = dict()
        self._relationships = []
        self._first_definition = None
        
    def add_definition(self, name, definition):
        """Adds the given view definition"""
        if not name is None:
            if self._first_definition is None:
                self._first_definition = definition
            if not name in self._definitions:
                self._definitions[name] = definition
                
    def add_relationship(self, rel):
        """Adds the given relationship"""
        self.add_definition(rel.source, rel.source_def)
        self.add_definition(rel.target, rel.target_def)
        if (not rel.relationship is None and 
          not rel.relationship in self._relationships):
            self._relationships.append(rel.relationship)

    def get_dot_text(self):
        """Get the full text that composes the dot file"""
        content = ""
        if self._first_definition:
            content += self._first_definition
            
        for definition in self._definitions.values():
            if definition != self._first_definition:
                content += definition
        for rel in self._relationships:
            content += rel
        return Graphs.dot_head % content        

        
