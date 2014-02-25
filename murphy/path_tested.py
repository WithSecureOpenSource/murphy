"""
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Encapsulates the list of views and verbs travelled and the state
on each step during an execution
"""
import json

class TestedPath():
    """Array of visited steps within a path and the state of each of them.
    The insertion order is expected to be view, verb, view, verb and so.
    The end of the path can be either a view or a verb but the start must be
    a view.
    """
    PASS = 'pass'
    FAIL = 'fail'
    ERROR = 'error'
    
    def __init__(self):
        self._steps = []
    
    def add_step(self, step_state):
        """Adds the given StepState to the path being traversed"""
        self._steps.append(step_state)
        
    def get_visits(self):
        """Returns a copy of the path traversed so far"""
        return self._steps[:]
        
    def dump_visits(self):
        '''
        Dumps friendly output for the visits
        '''
        for visit in self._steps:
            print "\t%s" % visit

        
class StepState():
    """A step state represents the state of step within a path, each step is
    either a visit to a view or the execution of a verb, the description is
    used as a vehicle for documentation and error tracking, for example when a
    step fails it can add the description of why, or if it fails with error
    it can add the exception raised.
    When creating a StepState, use verb_name as None if this step does not
    represent a verb per se.
    """
    
    def __init__(self, view_name, verb_name, state, description):
        self._view_name = view_name
        self._verb_name = verb_name
        self._state = state
        self._desc = description
    
    @property
    def view_name(self):
        """Returns the name of the view this step represents"""
        return self._view_name

    @property
    def verb_name(self):
        """Returns the name of the verb this step represents"""
        return self._verb_name
        
    @property
    def state(self):
        """Returns the state of this step, should be TestedPath.PASS,
        TestedPath.FAIL or TestedPath.ERROR"""
        return self._state
        
    @property
    def description(self):
        """Returns the description associated with the execution of this step.
        It is mean to be used mostly as the description of a failure or error
        """
        return self._desc
    
    def encode(self):
        """Encodes this instance in a JSON format"""
        return json.JSONEncoder().encode(self.__dict__)
    
    @staticmethod
    def decode(content):
        """Decodes the given string into a StepState object instance"""
        a_dict = json.JSONDecoder().decode(content)
        return StepState(a_dict['_view_name'],
                         a_dict['_verb_name'],
                         a_dict['_state'],
                         a_dict['_desc'])
    
    def __str__(self):
        return "%s.%s (%s) %s" % (self.view_name, self.verb_name, self.state,
                                  self.description)