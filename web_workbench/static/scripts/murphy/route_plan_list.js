/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document*/

define(["scripts/murphy/utils.js"], function (utils) {
    "use strict";
    var RoutePlan = function (container) {
            var container_element = container;

            this.init = function (initial_node) {
                var line;
                utils.removeChilds(container_element);
                if (initial_node !== undefined && initial_node !== null) {
                    this.add_step(initial_node);
                    line = container_element.firstChild;
                    line.firstChild.onclick = null;
                    line.firstChild.src = '/img/x-space.png';
                    line.firstChild.style.cursor = null;
                }
            };

            this.add_step = function (step) {
                //adds the given step to the list
                var line,
                    deleter,
                    text;
                line = document.createElement('div');
                deleter = document.createElement('img');
                deleter.src = '/img/x.png';
                deleter.style.cursor = 'pointer';
                deleter.onclick = function () { line.parentNode.removeChild(line); };
                text = document.createTextNode(step);
                line.appendChild(deleter);
                line.appendChild(text);
                container_element.appendChild(line);
            };

            this.get_steps = function () {
                var line, step, result;
                line = container_element.firstChild;
                step = line.firstChild.nextSibling.textContent;
                result = [];
                result.push(step);
                while (line.nextSibling !== null) {
                    line = line.nextSibling;
                    result.push(line.firstChild.nextSibling.textContent);
                }
                return result;
            };
        };

    return {RoutePlan: RoutePlan};
});
