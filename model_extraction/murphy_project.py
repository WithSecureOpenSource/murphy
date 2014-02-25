'''
Copyright (c) 2011-2014 F-Secure
See LICENSE for details

Generic murphy project management functions
'''
import os, shutil, subprocess, json, time

import logging
LOGGER = logging.getLogger('root.' + __name__)
    
class Project(object):

    def __init__(self, graph, rules_template=None):
        #FIXME: rules module ends always being rules, even if the user
        #uses a different template name, name should be additional param
        self._graph = graph
        if self._graph.path == '.':
            self._full_path = self._graph.name
        else:
            self._full_path = os.path.join(self._graph.path, self._graph.name)
            
        if rules_template is None:
            self.rules_module = os.path.join(os.path.dirname(__file__), 'templates', 'rules.py')
        else:
            self.rules_module = rules_template

            
    @property
    def graph(self):
        return self._graph

        
    @property
    def path(self):
        return os.path.abspath(self._full_path)

        
    def create(self, override_if_exists=False):
        if override_if_exists and self.exists():
            self.delete()

        LOGGER.info("Creating project at %s" % os.path.abspath(self._full_path))
        script_dir = os.path.dirname(os.path.abspath(self._full_path))
        python_module_dir_file = script_dir + "/__init__.py"
        with open(python_module_dir_file, "w+"):
            # creates if it does not exists, we merely want to be sure
            # is there so we can later load modules from it
            pass
            
        if os.path.isfile(self._full_path) or os.path.isdir(self._full_path):
            raise ValueError("A file or directory already exists in %s" % 
                             self._full_path)
        os.makedirs(self._full_path)
        if self._graph.images_dir:
            images_dir = os.path.join(self._full_path, self._graph.images_dir)
            os.makedirs(images_dir)
            
        the_file = open(os.path.join(self._full_path, '__init__.py'), 'w')
        the_file.close()
        shutil.copy(self.rules_module, os.path.join(self._full_path, 'rules.py'))
        
        
    def save(self, extra_model_attributes=None):
        '''
        Saves current state of the model definition, if extra_model_attributes
        are given then they are added to the model definition, they have to
        be a dict type, for example {'reference model': '../some/project.json'}
        '''
        package_name = self._graph.path
        if self._graph.path == '.':
            package_name = os.path.basename(os.getcwd())
            
        project = {"business rules": "rules", 
                   "coverage": "coverage.json", 
                   "global timeout": 90, 
                   "images dir": self._graph.images_dir,
                   "modules": [], 
                   #FIXME: not right
                   "namespace": "%s.%s" % (package_name, self._graph.name),
                   "tags": [],
                   "views": [
                        {"name": "All", 
                         "starts at": "Node 0"}]}
                         
        if len(self._graph.nodes) > 0:
            project['views'][0]['starts at'] = self._graph.nodes[0].name
            
        if extra_model_attributes:
            project.update(extra_model_attributes)
            
        for node in self._graph.nodes:
            project['modules'].append(node.file_name)
            
        encoded = json.dumps(project, sort_keys=True, indent=4)
        json_file_name = os.path.join(self._full_path,
                                      self._graph.name + '.json')
        with open(json_file_name, "w") as the_file:
            the_file.write(encoded)
        
        
    def delete(self):
        for i in range(3):
            LOGGER.info("Deleting old files at %s" % self._full_path) 
            subprocess.check_call(['rmdir', '/s', '/q', self._full_path],
                                  shell=True)
            for i in range(10):
                if self.exists() == False:
                    return
                LOGGER.debug("Directory still exists, waiting a bit...")
                time.sleep(0.5)
            if i != 2:
                LOGGER.info("File deletion did not succeded, will retry...")

        raise RuntimeError("Unable to delete the directory and files at %s" % self._full_path)
        
    def exists(self):
        return os.path.isdir(self._full_path)
            
    