/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, XMLHttpRequest*/

//FIXME: errors to popup, not to console

define(["scripts/murphy/edge_log.js"], function (edge_log) {
    "use strict";
    var Model = function (model_name, error_callback) {
            var name = model_name,
                on_error = error_callback,
                fetchAjax;

            this.getName = function () {
                return name;
            };
            this.getModels = function (callback) {
                /*
                   Returns a list of murphy projects available on this server.
                   See static method below for proper semantics
                */
                fetchAjax('get_projects', callback);
            };
            this.getViews = function (callback) {
                /*
                    Returns a list of the views the given model has, the format of the
                    response is [{'name': 'something', 'starts_at': 'first node'}]
                */
                fetchAjax('get_model_views/' + model_name, callback);
            };
            this.getView = function (view_name, type, callback) {
                /*
                    Returns the requested view definition
                    type ignored in view builder...
                    type = flow | flow-images | simple-flow-images | download
                    if type == download, returns zip file
                    response is either a zip file or an xml svg doc
                */
                fetchAjax('model/' + model_name + '/' + view_name + '?type=' + type, callback);
            };
            this.solveRun = function (steps, callback) {
                /*
                    Calculates a run that will visit all the steps given and returns
                    a step-by-step array of how to traverse, including any needed
                    parameter.
                    Format of the response is:
                    [{'node': name, 'arc': name, 'params': ['name']}]
                */
                var post = {};
                post.model = name;
                post.steps = steps;
                fetchAjax('solve_route',
                    function (solved_steps) {
                        var params_post = {};
                        params_post.model = name;
                        params_post.steps = solved_steps;
                        fetchAjax('get_params_needed', callback, JSON.stringify(params_post));
                    },
                    JSON.stringify(post));
            };
            this.requestRun = function (plan, callback) {
                fetchAjax('run',
                    function (response) {
                        callback(response);
                    },
                    JSON.stringify(plan));
            };
            this.compare = function (model_name, callback) {
                var request = {};
                request.model = name;
                request.reference_model = model_name;

                fetchAjax('compare', callback, JSON.stringify(request));
            };
            this.create = function (request, callback) {
                /*
                    Request a model creation
                    This is very specific to f-secure so needs to be considered
                 */
                fetchAjax('create_model', callback, request);
            };
            this.delete_model = function (callback) {
                /*
                    Requests this model to be permanently deleted
                 */
                fetchAjax('delete_model?model_name=' + name, callback);
            };
            this.get_edge_logs = function (node_name, edge_name) {
                var xhr = new XMLHttpRequest(),
                    log_data = null,
                    ret_val = null;
                xhr.open('POST', 'get_edge_logs', false);
                xhr.send(JSON.stringify({'model': name, 'node': node_name, 'edge': edge_name}));
                if (xhr.status === 200) {
                    log_data = JSON.parse(xhr.responseText);
                    if (log_data.status === "ok") {
                        ret_val = new edge_log.EdgeLog(log_data.response);
                    } else {
                        ret_val = new edge_log.EdgeLog(null);
                    }
                } else {
                    console.log("Error: " + xhr.statusText);
                }
                return ret_val;
            };
            this.get_live_channel = function () {
                var xhr = new XMLHttpRequest(),
                    response = null,
                    ret_val = null;
                xhr.open('GET', 'get_model_live_channel/' + name, false);
                xhr.send();
                if (xhr.status === 200) {
                    response = JSON.parse(xhr.responseText);
                    if (response.status === "ok") {
                        ret_val = response.response;
                    } else {
                        ret_val = response.text;
                    }
                } else {
                    console.log("Error: " + xhr.statusText);
                }
                return ret_val;
            };
            this.get_graph_logs = function () {
                var xhr = new XMLHttpRequest(),
                    log_data = null,
                    result = [],
                    key;
                xhr.open('POST', 'get_graph_logs', false);
                xhr.send(JSON.stringify({'model': name}));
                if (xhr.status === 200) {
                    log_data = JSON.parse(xhr.responseText);
                    if (log_data.status === "ok") {
                        for (key in log_data.response) {
                            result[key] = new edge_log.EdgeLog(log_data.response[key]);
                        }
                    }
                } else {
                    console.log("Error: " + xhr.statusText);
                }
                return result;
            };
            fetchAjax = function (url, callback, content) {
                /*
                    Internal use only, fetches an ajax response from te server and
                    validates it accordingly, chain the call to callback with the
                    result
                */
                var xhr = new XMLHttpRequest();
                if (content === undefined || content === null) {
                    xhr.open('GET', url, true);
                } else {
                    xhr.open('POST', url, true);
                }
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4) {
                        try {
                            if (xhr.status !== 200) {
                                on_error(xhr.responseText);
                            } else if (xhr.getResponseHeader('Content-Type') === 'application/json') {
                                var object = JSON.parse(xhr.responseText);
                                if (object.status === 'fail') {
                                    on_error(object.text);
                                } else {
                                    callback(object.response);
                                }
                            } else {
                                callback(xhr);
                            }
                        } catch (err) {
                            on_error(err);
                        }
                    }
                };
                if (content === undefined) {
                    xhr.send(null);
                } else {
                    xhr.send(content);
                }
            };
        },
        getModels = function (callback, error) {
            /*
               Returns a list of murphy models available on this server.
               Calls callback(list) or error(message) on completion
            */
            new Model(null, error).getModels(callback);
        };

    return {Model: Model,
            getModels: getModels};
});