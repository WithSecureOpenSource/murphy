/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, console, XMLHttpRequest*/

define(function () {
    "use strict";
    var RunLog = function (model_name, id, when, running) {
            var run_id = id,
                that = this,
                fetchAjax;

            this.model_name = model_name;
            this.when = when;
            this.running = running;

            this.getRuns = function (model_name, callback) {
                fetchAjax(model_name + '/get_runs', callback);
            };

            this.getId = function () {
                return run_id;
            };

            this.on_error = function (err) {
                console.log("Error: " + err);
            };

            this.deleteRun = function () {
                fetchAjax(model_name + '/delete_run?id=' + run_id, null);
            };

            this.getText = function (callback) {
                fetchAjax(model_name + '/get_run_log?id=' + run_id, function (log) {
                    that.running = (log.indexOf('Run finished.') === -1);
                    callback(log);
                });
            };

            //duplicated, generalize
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
                                that.on_error(xhr.responseText);
                            } else if (xhr.getResponseHeader('Content-Type') === 'application/json') {
                                var object = JSON.parse(xhr.responseText);
                                if (object.status === 'fail') {
                                    that.on_error(object.text);
                                } else {
                                    if (callback !== null) {
                                        callback(object.response);
                                    }
                                }
                            } else {
                                callback(xhr);
                            }
                        } catch (err) {
                            that.on_error(err);
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
        getRuns = function (model_name, callback) {
            new RunLog(null).getRuns(model_name, callback);
        };

    return {RunLog: RunLog, getRuns: getRuns};
});
