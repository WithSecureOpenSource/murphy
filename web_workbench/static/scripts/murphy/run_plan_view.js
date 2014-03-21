/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document*/

define(function () {
    "use strict";
    var RunPlanView = function (container_element, on_run, on_cancel) {
            var container, run_request, cancel_run_request, plan, call_run_request;

            container = container_element;
            run_request = on_run;
            cancel_run_request = on_cancel;
            plan = null;

            call_run_request = function () {
                var i, j, step, param, counter, input, full_plan;

                full_plan = JSON.parse(JSON.stringify(plan));
                counter = 0;
                for (i = 0; i < plan.length; i += 1) {
                    step = plan[i];
                    for (j = 0; j < step.params.length; j += 1) {
                        param = step.params[j];
                        input = document.getElementById('param_' + counter);
                        counter += 1;
                        full_plan[i].params[j] = {name: param,
                                                  value: input.value};
                    }
                }
                //FIXME: put param values into plan
                run_request(full_plan);
            };

            this.show = function (path) {
                var i, step, param_count, pre, text, input, a_button;
                pre = document.createElement("pre");
                text = "";
                param_count = 0;
                //FIXME: avoid hand coded html, put inputs in appropriate array
                for (i = 0; i < path.length; i += 1) {
                    step = path[i];
                    text += step.node + " -> " + step.arc;
                    if (step.params.length > 0) {
                        input = "&nbsp;&nbsp;<input type=text id='param_" + param_count + "' + name='" + step.params[0] + "'>";
                        param_count += 1;
                        text += input;
                    }
                    text += '\n';
                }
                pre.innerHTML = text;
                container.appendChild(pre);

                plan = JSON.parse(JSON.stringify(path));

                a_button = document.createElement("input");
                a_button.type = 'button';
                a_button.value = 'Run';
                a_button.style.marginLeft = '10px';
                a_button.addEventListener('click', call_run_request, false);
                container.appendChild(a_button);

                a_button = document.createElement("input");
                a_button.type = 'button';
                a_button.value = 'Cancel';
                a_button.style.marginLeft = '100px';
                a_button.addEventListener('click', cancel_run_request, false);
                container.appendChild(a_button);
            };
        };
    return {RunPlanView: RunPlanView};
});

