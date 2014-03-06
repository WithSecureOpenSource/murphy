'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details

Web based tester workbench for murphy

Stateles application, except for a username cookie that is needed after login.
No user database / password, just a display name for the user.

Every response is wrapped as either:
    {"status": "ok", "response": 
or
    {"status": "fail", "text":
    
'''

import os, sys
#Lets just be sure that pythonpath has murphy, or add it if not
CURRENT_DIR = os.path.abspath(__file__)
MURPHY_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if not MURPHY_DIR in sys.path:
    print "Adding murphy to pythonpath"
    sys.path.append(MURPHY_DIR)

    
from web_workbench.bottle import route, run, static_file, request, redirect, response, HTTPResponse

import json, traceback, time, datetime, uuid, StringIO
from PIL import Image

from web_workbench import utils
from murphy.model import Model
from web_workbench.view_builder import build_view
from web_workbench.planner import (solve_route, find_needed_params, run_plan,
                                   compare_models,
                                   get_edge_logs as _get_edge_logs,
                                   get_graph_logs as _get_graph_logs)
from web_workbench.custom_model import create_custom_model,\
    remove_model_from_workbench
import subprocess

PROJECTS_FILE = 'projects.json'

DYNAMIC_FILES = {}

def _load_projects_list():
    '''
    Loads a list of available projects
    '''
    if not os.path.isfile(PROJECTS_FILE):
        raise ValueError("Projects configuration file is missing")
    with open(PROJECTS_FILE, "rb") as a_file:
        projects = json.load(a_file)

    return projects


def _get_model_file_name(model_name):
    '''
    Returns the file name for the given model name, as in the web page the
    full path is not shown
    '''
    projects = _load_projects_list()
    for project in projects:
        if (project['file'].endswith('/' + model_name) or
          project['file'].endswith('\\' + model_name)):
            return project['file']
    raise ValueError("Model %s not found in list of projects" % model_name)


def _get_views(model_file_name):
    '''
    Returns the view names of the given model
    '''
    if os.path.exists(model_file_name):
        model = Model(model_file_name, load_modules=False)
        view_names = []
        for view in model.model['views']:
            view_names.append({'name': view['name'],
                               'starts_at': view['starts at']})
        return view_names
    else:
        print "No views found since model %s does not exists" % model_file_name
        return []

def _get_user_name():
    '''
    Returns the user name used for the active request or None if there isnt
    '''
    user = request.get_cookie("username")
    if user:
        return user
    else:
        return None


@route('/murphy/get_projects')
def get_projects():
    '''
    Retrieves the list of available projects
    '''
    try:
        projects = _load_projects_list()
        project_list = []
        for project in projects:
            file_name = project['file']
            if not os.path.isfile(file_name):
                print "ERROR: Projects file %s does not exists!" % file_name
            project_list.append(os.path.basename(file_name))
        return {"status": "ok", "response": project_list}
    except Exception, ex:  # pylint: disable=W0703
        return {"status": "fail",
                "text": "Error when loading project list: %s" % str(ex)}


@route('/murphy/get_model_views/:model_name')
def get_model_views(model_name):
    '''
    Returns an array containing the view names for the given model
    '''
    try:
        model_file = _get_model_file_name(model_name)
        return {"status": "ok",
                "response": _get_views(model_file)}
    except Exception, ex:  # pylint: disable=W0703
        return {"status": "fail",
                "text": "Error when loading model: %s" % str(ex)}

@route('/murphy/get_model_live_channel/:model_name')
def get_model_live_channel(model_name):
    '''
    Returns a live channel if there's one
    '''
    try:
        model_file = _get_model_file_name(model_name)
        model_dict = {}
        with open(model_file, 'rb') as the_file:
            model_dict = json.load(the_file)
        return {"status": "ok",
                "response": model_dict.get("live broadcast", "")}
    except Exception, ex:  # pylint: disable=W0703
        return {"status": "fail",
                "text": "Error when loading model: %s" % str(ex)}

@route('/channel')
def get_live_channel():
    try:
        model_file = _get_model_file_name(request.query.model)
        with open(model_file, 'rb') as the_file:
            model_dict = json.load(the_file)
        broadcasts = model_dict.get("live broadcast", "")
        if broadcasts == "":
            raise RuntimeError("Requested broadcast of non broadcasting model")
                
        max_retries = 3
        for i in range(max_retries):
            try:
                with open(broadcasts, 'rb') as a_file:
                    content = a_file.read()
                #test is valid...
                Image.open(StringIO.StringIO(content))
                break
            except:
                if i < max_retries -1:
                    time.sleep(0.1)
                else:
                    raise
            
        headers = {'Content-Length': len(content),
                   'Content-Type': "image/png",
                   'Accept-Ranges': "bytes",
                   'Cache-Control': "no-cache"}
        return HTTPResponse(content, **headers)
            
    except Exception, ex:
        print "Problem: %s" % str(ex)
        with open('static/x-space.png', 'rb') as a_file:
            content = a_file.read()
        headers = {'Content-Length': len(content),
                   'Content-Type': "image/png",
                   'Accept-Ranges': "bytes",
                   'Cache-Control': "no-cache"}
        return HTTPResponse(content, **headers)

                
@route('/murphy/model/:model_name/:view_name')
def get_view(model_name, view_name):
    '''
    Responses are:
        flow.xml
        flow-images.xml
        simple-flow-images.xml
        empty.xml
        local-simple-flow-images is not returned but built for zip
    '''
    try:
        view_type = request.query.type
        if view_type == '':
            view_type = 'flow'
        print "Requested view %s %s %s" % (str(model_name),
                                           str(view_name),
                                           view_type)

        should_build = True
        view_directory = "projects/%s/%s" % (model_name, view_name)
        view_file_name = "%s/%s.xml" % (view_directory, view_type)
        if not os.path.isdir(view_directory):
            os.makedirs(view_directory)

        model_file = _get_model_file_name(model_name)
        if os.path.isfile(view_file_name):
            since = os.stat(view_file_name).st_mtime
            if utils.files_modified_since(os.path.dirname(model_file), since):
                os.remove(view_file_name)
            else:
                should_build = False

        if should_build:
            return_empty = False
            if os.path.exists(model_file) == False:
                return_empty = True
            else:
                model = Model(model_file, load_modules=False)
                view_exists = False
                for view in model.model['views']:
                    if view['name'] == view_name:
                        view_exists = True
                        break
                if not view_exists:
                    return_empty = True
            if return_empty:
                resp = static_file('empty.xml', root='static')
                resp.headers['Cache-Control'] = 'no-cache'
                return resp

            build_view(model_file, view_name, view_type, view_directory)
            utils.inline_images("%s/flow-images.xml" % view_directory)
            utils.inline_images("%s/simple-flow-images.xml" % view_directory)

        if view_type == 'download':
            resp = static_file('%s/download.zip' % view_directory, root='')
        else:
            # FIXME: lacks wrap the answer with status
            if view_type in ('flow-images', 'simple-flow-images'):
                view_file_name = "%s/%s.xml" % (view_directory,
                                                'inlined_' + view_type)
            resp = static_file(view_file_name, root='')
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
    except Exception, ex:  # pylint: disable=W0703
        traceback.print_exc(file=sys.stdout)
        return {"status": "fail",
                "text": "Error when creating the model graph: %s" % str(ex)}

@route('/murphy/get_edge_logs', method='POST')
def get_edge_logs():
    obj = json.load(request.body)
    model_file = _get_model_file_name(obj['model'])
    ret = _get_edge_logs(model_file, obj['node'], obj['edge'])
    if ret != "":
        return {'status': 'ok', 'response': json.loads(ret)}
    else:
        return {'status': 'no data'}


@route('/murphy/get_graph_logs', method='POST')
def get_graph_logs():
    obj = json.load(request.body)
    model_file = _get_model_file_name(obj['model'])
    ret = _get_graph_logs(model_file)
    if ret != "":
        return {'status': 'ok', 'response': json.loads(ret)}
    else:
        return {'status': 'no data'}
    
        
@route('/murphy/solve_route', method='POST')
def solve_route_request():
    '''
    Solves a route given the points to visit
    '''
    try:
        obj = json.load(request.body)
        model_file = _get_model_file_name(obj['model'])
        # TODO: tags support in model and route
        path = solve_route(model_file, obj['steps'], {})
        return {"status": "ok", "response": path}
    except Exception, ex:  # pylint: disable=W0703
        traceback.print_exc(file=sys.stdout)
        return {"status": "fail",
                "text": "Error when creating the model graph: %s" % str(ex)}


@route('/murphy/get_params_needed', method='POST')
def get_params_needed():
    '''
    Returns the parameter names needed for the given steps
    '''
    obj = json.load(request.body)
    model_file = _get_model_file_name(obj['model'])
    plan = find_needed_params(model_file, obj['steps'])
    if type(plan) is list:
        return {'status': 'ok', 'response': plan}
    else:
        return {'status': 'fail', 'text': plan}


@route('/murphy/run', method='POST')
def request_run():
    '''
    Requests a run, format of the request is:
    {'model': name, 'steps': 
        [{'node': name, 'edge': name, 'params': [{'name': name,
                                                  'value': value}]}]}
    '''
    obj = json.load(request.body)
    print "Requested plan:\n%s" % json.dumps(obj, sort_keys=True, indent=4)
    model_file = _get_model_file_name(obj['model'])
    log_file = run_plan(model_file, obj['plan'], get_user_name())
    print "Run request returned %s" % log_file
    return {'status': 'ok', 'response': log_file}


def get_user_name():
    '''
    Returns the user name in use for the given request
    TODO: can also come as an uri value
    '''
    user = request.get_cookie("username")
    if user:
        return user
    else:
        return None


def get_user_runs(user, model):
    '''
    Returns the runs requested by the given user
    '''
    user_directory = "users/%s/%s" % (user, model)
    if not os.path.isdir(user_directory):
        os.makedirs(user_directory)

    ret_json = {"status": "ok", "response": []}
    for a_file in os.listdir(user_directory):
        file_type = a_file.split(".")
        if file_type[1] in ('rdy', 'bsy'):
            this_file = {"name": a_file.split(".")[0]}
            try:
                file_time = time.ctime(os.path.getctime(user_directory
                                                        + '/' + a_file))
                file_time = datetime.datetime.strptime(file_time,
                                                       "%a %b %d %H:%M:%S %Y")
                this_file["when"] = file_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception, ex:  # pylint: disable=W0703
                print "Failed with file %s as %s" % (this_file, ex)
                this_file["when"] = "Executing..."
            this_file['running'] = file_type[1] == "bsy"
            ret_json['response'].append(this_file)

    def compare(a_obj, b_obj):
        '''
        Comparison for sorting runs by their timestamp
        '''
        return cmp(a_obj['when'], b_obj['when'])
    ret_json['response'].sort(compare)
    return ret_json


@route('/murphy/:model/get_runs', method='GET')
def get_runs(model):
    '''
    Returns the runs requested by the current user
    '''
    user = get_user_name()
    if user is None:
        return {"status": "error", "text": "No user specified"}
    # elif user == 'everybody':
    #    return get_all_users_runs()
    else:
        return get_user_runs(user, model)


@route('/murphy/:model/delete_run', method='GET')
def delete_run(model):
    '''
    Deletes a given run
    '''
    run_id = request.query.id
    user = get_user_name()
    filename = "users/%s/%s/%s" % (user, model, run_id)
    print "trying to delete run " + filename
    utils.silent_remove(filename + ".rdy")
    utils.silent_remove(filename + ".bsy")
    utils.silent_remove(filename + ".bmp")
    return {"status": "ok"}


@route('/murphy/:model/get_run_log', method='GET')
def get_run_log(model):
    '''
    Returns the log of the given run
    '''
    run_id = request.query.id
    user = get_user_name()

    filename = "users/%s/%s/%s" % (user, model, run_id)
    if os.path.isfile(filename + ".rdy"):
        filename = filename + ".rdy"
    elif os.path.isfile(filename + ".bsy"):
        filename = filename + ".bsy"
    else:
        filename = 'not_found.err'

    print "trying to get log for " + filename
    # static_file does not properly refresh when requests cames ofthen
    with open(filename, "r") as a_file:
        text = "".join(a_file.readlines())
    return {"status": "ok", "response": text}


@route('/murphy/compare', method='POST')
def compare_model():
    '''
    Compares 2 models and returns an html report of the comparison
    '''
    obj = json.load(request.body)
    model_file = _get_model_file_name(obj['model'])
    reference_file = _get_model_file_name(obj['reference_model'])
    print "Will compare models: %s" % str(obj)
    result = compare_models(model_file, reference_file)
    print "Models compared..."
    return {"status": "ok", "response": result}


@route('/murphy/create_model', method='POST')
def create_model():
    '''
    Requests a model creation, format of the request is:
    '''
    obj = json.load(request.body)
    print "Requested model:\n%s" % json.dumps(obj, sort_keys=True, indent=4)
    
    
    response = create_custom_model(obj)
    if 'status' in response and response['status'] == 'ok':
        #should answer back the log file
        new_file = response['response'] 
        uid = str(uuid.uuid1())
        print "Dynamic file id %s for file %s" % (uid, new_file)
        DYNAMIC_FILES[uid] = new_file
            
        return {'status': 'ok', 'response': uid}
    else:
        return response


@route('/murphy/serve_file/:uid')
def serve_file(uid):
    '''
    Returns a dynamic file identified by a uid, for example a model creation
    log
    '''
    file_name = DYNAMIC_FILES[uid]

    with open(file_name, "r") as a_file:
        text = "".join(a_file.readlines())

    return text

@route('/murphy/delete_model', method='GET')
def delete_model():
    '''
    Requests a model creation, format of the request is:
    '''
    print "Requested model deletion for %s" % request.query.model_name
    model_file = _get_model_file_name(request.query.model_name)
    print "Model file name is %s" % model_file
    subprocess.call(['rmdir', '/s', '/q',
                      os.path.abspath(os.path.dirname(model_file))], shell=True)
    remove_model_from_workbench(model_file)
    
    return {'status': 'ok', 'response': 'ok'}

@route('/murphy/projects/:project_name/:view_name/:file_name')
def server_project_files(project_name, view_name, file_name):
    '''
    Returns files that are specific to a model
    '''
    return static_file(file_name,
                       root='projects/%s/%s' % (project_name, view_name))


@route('/murphy/scripts/<filename>')
def server_static2(filename):
    return static_file(filename, root='static/scripts')
    
@route('/murphy/<filename>')
def server_static(filename):
    '''
    Returns static files but enforces also the use of the username cookie
    FIXME: this wont work for static files referenced in login.html!
    '''
    user = _get_user_name()
    print "Requested by: " + str(user)
    if user is None and filename != 'login2.html':
        return redirect("/murphy/login2.html")
    else:
        return static_file(filename, root='static')

@route('/')
def index():
    '''
    Simple redirection to start page
    '''
    return redirect("/murphy/login2.html")


@route('/favicon.ico')
def icon():
    '''
    Default site icon
    '''
    return static_file("favicon.png", root='static')


if __name__ == '__main__':
    print "Workbench running on pid " + str(os.getpid())
    run(host='0.0.0.0', port=8090)  # , server='cherrypy')
