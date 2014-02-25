'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

import os, sys, json

from murphy import utils
from murphy.worker import Worker

class Model(object):
    '''
    Helper class for holding state of an opened model
    '''
    def __init__(self, file_name, load_modules=True):
        self._model = utils.load_json_object(file_name)
        if not 'coverage' in self._model:
            self._model['coverage'] = 'coverage.json'
        self._file_name = file_name
        self._working_dir = os.path.dirname(file_name)
        
        self.current_view = None
        self.tags = dict()

        if 'business rules' in self._model and load_modules:
            name = "%s.%s" % (self._model['namespace'],
                              self._model['business rules'])
            full_path = os.path.abspath(file_name)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(full_path)))
            # Normally the rules file is 2 dirs deeper than the model dir
            if not base_dir in sys.path:
                # print "Adding %s to pythonpath" % base_dir
                sys.path.append(base_dir)
            __import__(name)
            self._rules_module = sys.modules[name]
        else:
            self._rules_module = None
            
    @property
    def model(self):
        '''
        Returns the model object
        '''
        return self._model

    def get_starting_node(self, view_name):
        #FIXME: not quite ok, will need more of a view wrapping object and so
        for view in self.model['views']:
            if view['name'] == view_name:
                return view['starts at']
        return None
    
    def save(self):
        '''
        Saves the model file, overwrites existing one!
        '''
        content = json.dumps(self._model, sort_keys=True, indent=4)
        with open(self._file_name, 'w') as a_file:
            a_file.write(content)

    def new_worker(self, user_simulation=None):
        '''
        Get a murphy worker, it will act over the given user simulation, if
        not provided defaults to a user in the running machine
        @return: murphy.worker.Worker
        '''
        return Worker(user_simulation, self.model, self.images_dir)
        
    @property
    def rules(self):
        '''
        Returns the rules module
        '''
        return self._rules_module
        
    @property
    def file_name(self):
        '''
        Returns the file name of this model
        '''
        return self._file_name

    @property
    def images_dir(self):
        '''
        Returns the directory where images are stored for this model
        '''
        if os.path.isabs(self.model['images dir']):
            return self.model['images dir']
        else:
            return "%s/%s" % (os.path.dirname(self.file_name),
                                              self.model['images dir'])
    
    @property
    def working_dir(self):
        '''
        Returns the working directory for this model, which is the same
        directory of the model itself
        '''
        return self._working_dir

    @property
    def coverage_file(self):
        '''
        Returns the file name of the coverage, solving the relative path from
        the model
        '''
        if os.path.isabs(self._model['coverage']):
            return self._model['coverage']
        else:
            return os.path.join(self.working_dir, self._model['coverage'])
    
    @coverage_file.setter
    def coverage_file(self, file_name):
        '''
        Sets the file name of the coverage, can be relative to the model file
        or absolute
        '''
        self._model['coverage'] = file_name

    def reset_coverage(self):
        '''
        Cleans coverage from previous runs
        '''
        utils.save_coverage([], self.coverage_file)
        
    def load_coverage(self):
        '''
        Returns the current coverage
        FIXME: must be synchronized - thread friendly
        '''
        if os.path.isfile(self.coverage_file):
            coverage = utils.load_coverage(self.coverage_file)
        else:
            coverage = []
        return coverage

    def append_coverage(self, new_coverage):
        '''
        Appends the given coverage to the existing coverage
        FIXME: must be synchronized - thread friendly
        '''
        old_coverage = self.load_coverage()
        old_coverage.append(new_coverage)
        utils.save_coverage(old_coverage, self.coverage_file)
