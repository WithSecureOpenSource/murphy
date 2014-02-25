/*jslint indent: 4, maxerr: 50, browser: true */

/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function RunList(container_element) {
    var container = container_element;
    var that = this;
    
    this.addRun = function (a_run) {
        /*
         * Adds the given run to the list of runs, placing it in the topmost
         * position
         */
        var line, deleter, link;
        line = document.createElement('div');
        deleter = document.createElement('img');
        deleter.src = 'x.png';
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
        link.href = 'javascript:showRun("' + a_run.model_name + '", "' + a_run.getId() + '");'
        line.appendChild(deleter);
        line.appendChild(link);
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
        removeChilds(container);
        RunLog.getRuns(model_name, function (runs) {
            var i, a_run;
            for (i = 0; i < runs.length; i += 1) {
                a_run = new RunLog(model_name, runs[i].name, runs[i].when, runs[i].running);
                that.addRun(a_run);
            }
        });
    };
}