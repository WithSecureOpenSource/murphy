/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, require, document, location, setTimeout*/

define(["scripts/murphy/utils.js"], function (utils) {
    "use strict";
    var RunList = function (container_element) {
            var container = container_element,
                that = this,
                waitVnc,
                addClickHandler,
                scheduleIcon;

            addClickHandler = function (a_run, opener) {
                opener.addEventListener("click", function () {
                    a_run.getText(function (log) {
                        var vnc = log.match(/vnc:\/\/\d+\.\d+\.\d+\.\d+:\d+/g);
                        location.href = vnc;
                    });
                });
            };

            waitVnc = function (a_run, line, opener) {
                a_run.getText(function (log) {
                    var vnc = log.match(/vnc:\/\/\d+\.\d+\.\d+\.\d+:\d+/g),
                        link;
                    if (vnc === null) {
                        scheduleIcon(a_run, line, opener);
                    } else {
                        opener.src = "/img/monitor.png";
                        opener.style.cursor = "pointer";
                        addClickHandler(a_run, opener);
                        if (log.search("Run finished.") !== -1) {
                            link = line.getElementsByTagName("a");
                            if (link.length > 0) {
                                link[0].removeChild(link[0].firstChild);
                                link[0].appendChild(document.createTextNode("Just finished."));
                            }
                        } else {
                            scheduleIcon(a_run, line, opener);
                        }
                    }
                });
            };

            scheduleIcon = function (a_run, line, opener) {
                setTimeout(function () {
                    waitVnc(a_run, line, opener);
                }, 1000);
            };

            this.addRun = function (a_run) {
                /*
                 * Adds the given run to the list of runs, placing it in the topmost
                 * position
                 */
                var line = document.createElement('div'),
                    deleter = document.createElement('img'),
                    link,
                    opener,
                    timediff;

                deleter.src = '/img/x.png';
                deleter.style.cursor = 'pointer';
                deleter.style.marginLeft = '2px';
                deleter.style.marginRight = '4px';

                deleter.addEventListener('click', function () { that.deleteRun(a_run, line); });
                link = document.createElement('a');
                if (a_run.running === true) {
                    link.appendChild(document.createTextNode("Running..."));
                } else {
                    link.appendChild(document.createTextNode(a_run.when));
                }
                link.addEventListener("click", function (evt) {
                    evt.preventDefault();
                    window.open('view_run2.html?model=' + a_run.model_name + '&id=' + a_run.getId(), '_blank');
                    window.focus();
                });
                link.href = 'show run';

                opener = document.createElement("img");
                opener.style.paddingLeft = "8px";
                line.appendChild(deleter);
                line.appendChild(link);

                timediff = (new Date()) - Date.parse(a_run.when);
                if (isNaN(timediff)) {
                    opener.src = "/img/working.gif";
                    opener.style.cursor = "default";
                    opener.style.width = "16px";
                    opener.style.height = "16px";
                    line.appendChild(opener);
                    scheduleIcon(a_run, line, opener);
                } else {
                    //only give link for anything no older than 3 hours
                    if ((timediff / (1000 * 60 * 60)) < 3) {
                        opener.src = "/img/monitor.png";
                        opener.style.cursor = "pointer";
                        addClickHandler(a_run, opener);
                        line.appendChild(opener);
                    }
                }
                if (container.hasChildNodes()) {
                    container.insertBefore(line, container.firstChild);
                } else {
                    container.appendChild(line);
                }
            };

            this.deleteRun = function (a_run, div_elem) {
                a_run.deleteRun();
                div_elem.parentNode.removeChild(div_elem);
            };

            this.reload = function (model_name) {
                utils.removeChilds(container);
                if (model_name === '') {
                    return;
                }
                require(['scripts/murphy/log.js'], function (module) {
                    module.getRuns(model_name, function (runs) {
                        var i, a_run;
                        for (i = 0; i < runs.length; i += 1) {
                            a_run = new module.RunLog(model_name, runs[i].name, runs[i].when, runs[i].running);
                            that.addRun(a_run);
                        }
                    });
                });
            };
        };

    return {RunList: RunList};
});
