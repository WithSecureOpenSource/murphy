'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

from multiprocessing import Process, Queue
import traceback

def _solve_route(steps, model_file_name, tags, response):
    '''
    Multiprocessing friendly implementation
    '''
    from murphy.model import Model
    from murphy.run_planner import solve_plan
    from murphy.errors import NoRouteFound
    
    model = Model(model_file_name)
    plan = []
    for step in steps:
        a_step = {'node': step, 'heuristics': ['shortest']}
        plan.append(a_step)

    path = []
    try:
        path = solve_plan(plan, model.new_worker(), model, tags)
    except NoRouteFound:
        pass #return an empty path when there's no path

    response.put(path)


def _find_needed_params(model_file_name, path, response):
    from murphy.model import Model
    from murphy.run_planner import get_params_needed

    model = Model(model_file_name)
    path = get_params_needed(path, model.new_worker())
    response.put(path)
    

def _run_plan(model_file_name, plan, out_file_name):
    import os, sys, time, json
    try:
        os.makedirs(os.path.dirname(out_file_name))
    except:
        pass
    print "should log to " + out_file_name

    import logging
    from murphy.model import Model
    fileHandler = logging.FileHandler(out_file_name + '.bsy', mode='a', encoding=None, delay=False)
    root_logger = logging.getLogger('root')
    root_logger.addHandler(fileHandler)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(formatter)
    logging.getLogger().removeHandler(logging.getLogger().handlers[0])
    #fileHandler.setFormatter(format)

    #root_logger.level = logging.DEBUG
    #root_logger.format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #logging.basicConfig(level=logging.DEBUG,
    #                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #                    filename=out_file_name + '.bsy',
    #                    filemode='w')
    LOGGER = logging.getLogger('root.' + __name__)
    LOGGER.info("Run request runs on pid " + str(os.getpid()))
    remoting = None
    try:
        steps = []
        run_params = {}
        for step in plan:
            steps.append((step['node'], step['arc']))
            params = step['params']
            for param in params:
                values = run_params.get(param['name'], [])
                values.append(param['value'])
                run_params[param['name']] = values
        
        model = Model(model_file_name)
        remoting = model.rules.get_remoting_vnc_object()
        worker = model.new_worker(remoting.automation)
        worker.parameters.update(run_params)
        LOGGER.info("Requesting run:\n%s" % json.dumps(steps,
                                                       sort_keys=True,
                                                       indent=4))
        LOGGER.info("Using values:\n%s" % json.dumps(worker.parameters,
                                                     sort_keys=True,
                                                     indent=4))
        LOGGER.info("Running at ip %s" % remoting.ip_address)
        LOGGER.info("Remoting at vnc://%s:%s" % (remoting.vnc_host,
                                                 remoting.vnc_port))
        worker.Walk_ext(steps)
    except Exception, ex:
        # traceback.print_exc(file=sys.stdout)
        LOGGER.exception(ex)
    finally:
        if remoting:
            try:
                remoting.automation.disconnect()
            except:
                pass
        try:
            LOGGER.info("Run finished.")
            logging.shutdown()
        except:
            pass
        for i in range(10):
            try:
                os.rename(out_file_name + '.bsy', out_file_name + '.rdy')
                break
            except Exception, ex:
                print "Failed renaming, will retry (%s)" % str(ex)
                time.sleep(1)
        
    sys.exit(0)
    
def solve_route(model_file_name, steps, tags):
    '''
    Given a series of unconnected points to visit, returns a list of each edge
    to be visited that will travel the given points.
    '''
    response = Queue()
    proc = Process(target=_solve_route, args=(steps, model_file_name, tags, response, ))
    proc.start()
    proc.join()
    if proc.exitcode != 0:
        raise Exception("Failed to solve the route %s for model %s" % (str(steps), model_file_name))
    return response.get()
    
    
def find_needed_params(model_file_name, steps):
    '''
    Given a series of unconnected points to visit, returns a list of each edge
    to be visited that will travel the given points.
    '''
    response = Queue()
    proc = Process(target=_find_needed_params, args=(model_file_name, steps, response,))
    proc.start()
    proc.join()
    if proc.exitcode != 0:
        raise Exception("Failed to solve needed params for path %s in model %s" % (str(steps), model_file_name))
    return response.get()
    

def run_plan(model_file_name, plan, username):
    '''
    Executes the given plan, returns a file
    '''
    import uuid, os
    uid = str(uuid.uuid1())
    out_file = 'users/%s/%s/%s' % (username, #user name
                                   os.path.basename(model_file_name),
                                   uid)
    out_file = os.path.abspath(out_file)
    proc = Process(target=_run_plan, args=(model_file_name, plan, out_file,))
    proc.start()
    proc = None
    return uid

    
def _compare_models(model_file_name, reference_model_file_name, response):
    import sys, traceback
    from murphy import model_comparison
    try:
        response.put(model_comparison.compare(model_file_name, reference_model_file_name))
    except Exception, ex:
        traceback.print_exc(file=sys.stdout)
        print "Problem: %s" % str(ex)
        response.put("Error while comparing: %s" % str(ex))
    

def compare_models(model_file_name, reference_model_file_name):
    '''
    Executes the given plan, returns a file
    '''
    response = Queue()
    proc = Process(target=_compare_models, args=(model_file_name, reference_model_file_name, response,))
    proc.start()
    return response.get()