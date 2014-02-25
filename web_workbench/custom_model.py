'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Custom model extraction in separate process, models can be requested with
arbitrary params and in arbitrary modules
'''

from multiprocessing import Process, Queue
import json
from murphy.utils import load_json_object
import traceback
import sys
import os

def add_model_to_workbench(model_name):
    '''
    Adds the given model to the list of models in the config file
    '''
    this_dir = os.path.abspath(os.path.dirname(__file__))
    models = load_json_object(this_dir + '/projects.json')
    this_model = {'file':model_name}
    if not this_model in models:
        models.append(this_model)
        encoded = json.dumps(models, sort_keys=True, indent=2)
        with open(this_dir + '/projects.json', "w") as the_file:
            the_file.write(encoded)


def remove_model_from_workbench(model_name):
    '''
    Adds the given model to the list of models in the config file
    '''
    this_dir = os.path.abspath(os.path.dirname(__file__))
    models = load_json_object(this_dir + '/projects.json')
    this_model = { 'file': model_name }
    if this_model in models:
        models.remove(this_model)
        encoded = json.dumps(models, sort_keys=True, indent=2)
        with open(this_dir + '/projects.json', "w") as the_file:
            the_file.write(encoded)


def _create_model(request, response):
    '''
    Creates a custom model by invoking the given function in the given module
    '''
    module = None
    
    try:
        request = json.loads(request)    
        module = __import__(request['module'], fromlist=[request['function']])
    except Exception, ex: #pylint: disable=W0703
        traceback.print_exc(file=sys.stdout)
        result = {"status": "fail", "text": str(ex)}
        response.put(result)
        return
    
    getattr(module, request['function'])(request, response)



def create_custom_model(request):
    '''
    Executes the given plan, returns a file
    '''
    response = Queue()
    proc = Process(target=_create_model, args=(json.dumps(request),response,))
    proc.start()
    return response.get()