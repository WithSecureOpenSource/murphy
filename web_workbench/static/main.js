/*jslint indent: 4, maxerr: 50, browser: true, devel: true */
"use strict";

/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function clear_content() {
    removeChilds(document.getElementById('route planner'));
}

function show_error(error) {
    alert("Error occurred:\n" + error);
}


/*
 * Sizing for the content area
 */
function getOffset(el) {
    var x = 0, y = 0;
    while (el && !isNaN(el.offsetLeft) && !isNaN(el.offsetTop)) {
        x += el.offsetLeft - el.scrollLeft;
        y += el.offsetTop - el.scrollTop;
        el = el.offsetParent;
    }
    return {top: y, left: x};
}

function getWidth(element) {
    return parseInt(document.defaultView.getComputedStyle(element).getPropertyValue("width"));
}
function getHeight(element) {
    return parseInt(document.defaultView.getComputedStyle(element).getPropertyValue("height"));
}

function adjustSizeableAreaDimensions() {
    var doc_width, doc_height, map_coords, map_width, map_height, scroll_left, scroll_top;
    
    doc_width = getWidth(document.body);
    doc_height = getHeight(document.body);
    map_coords = getOffset(document.getElementById('route planner'));
    scroll_left = document.getElementById('route planner').scrollLeft;
    scroll_top = document.getElementById('route planner').scrollTop;
    map_width = doc_width - (scroll_left + map_coords.left);
    map_height = doc_height - (scroll_top + map_coords.top);
    document.getElementById('route planner').style.width = map_width + 'px';
    document.getElementById('route planner').style.height = map_height + 'px';
}


/*
 * Toolbox functions
 */
function collapse_toolbox() {
    document.getElementById('left bar').style.display = 'none';
    document.getElementById('collapsed left bar').style.display = 'inline-block';
    adjustSizeableAreaDimensions();
}

function expand_toolbox() {
    document.getElementById('left bar').style.display = 'inline-block';
    document.getElementById('collapsed left bar').style.display = 'none';
    adjustSizeableAreaDimensions();
}


function Application() {
    var model, selected_view, view_start_node;
 
    var route_plan, runs_list, tab_control;
    var route_view, screens_view, thumbnails_view;
    
    var show_route_view, show_thumbnails_view, show_screens_view, show_simple_flow_view, hide_simple_flow_view, run_plan_view;
    var that;
    
    model = null;
    selected_view = null;
    view_start_node = null;
    that = this;
    
    this.load_models_list = function (models) {
        var models_list = document.getElementById("models");
        load_select_with_array(models_list, models, true);
    }

    this.load_view_list = function (views) {
        var option, i, view_list;
        view_list = document.getElementById("views");
        clear_select(view_list);
        for (i = 0; i < views.length; i += 1) {
            option = document.createElement("option");
            option.text = views[i].name;
            option.value = views[i].starts_at;
            view_list.add(option);
        }
        view_list.selectedIndex = 0;
        that.load_selected_view();
    }

    this.load_model = function (name) {
        selected_view = null;
        clear_content();
        runs_list.reload(name);
        route_plan.init();
        if (name === '') {
            model = null;
            var view_list = document.getElementById("views");
            load_select_with_array(view_list, new Array(), false);
            document.getElementById('download').style.visibility = 'hidden';
            document.getElementById('compare').href = null;
            document.getElementById("delete project").disabled = true;
        } else {
            model = new Model(name, show_error);
            model.getViews(this.load_view_list);
            document.getElementById('compare').href = "#";
            document.getElementById("delete project").disabled = false;
        }
    }

    this.load_selected_model = function () {
        var models_list, model_name;
        models_list = document.getElementById('models');
        model_name = models_list.options[models_list.selectedIndex].text;
        that.load_model(model_name);
    }

    this.reload_and_schedule = function () {
        if (document.getElementById('autorefresh').checked === true && model !== null) {
            that.reload_selected_view();
            setTimeout(that.reload_and_schedule, 30000);
        }
    }
    
    this.delete_selected_model = function () {
        if (model !== null) {
        	if (confirm("Will delete " + model.getName() + ", are you really sure? (cannot be undone)")) {
        		model.delete_model(function() {
        			window.location.reload(true);
        		});
        	}
        }
    }
    
    this.reload_selected_view = function () {
        //if no views available for the current model, try reload them
        var view_list = document.getElementById("views");
        if (model !== null) {
            if (view_list.options.length === 0) {
                model.getViews(this.load_view_list);
            } else {
                that.load_selected_view();
            }
        }
    }
    
    this.load_selected_view = function () {
        var view_list = document.getElementById("views");
        if (view_list.options.length === 0) {
            selected_view = null;
            view_start_node = null;
        } else {
            selected_view = view_list.options[view_list.selectedIndex].text;
            view_start_node = view_list.options[view_list.selectedIndex].value;
            tab_control.active_view.show();
        }
    }

    this.solve_route = function() {
        var steps = route_plan.get_steps();
        model.solveRun(steps, run_plan_view.show)
    }

    this.request_run = function(plan) {
        var full_plan = new Object();
        full_plan.model = model.getName();
        full_plan.plan = plan;
        model.requestRun(full_plan, function (run_id) {
            var run = new RunLog(model.getName(), run_id, "Running...", true);
            runs_list.addRun(run);
            tab_control.active_view.show();
        });
    }
    
    show_route_view = function () {
        var view_type, show_tooltips;
        
        view_type = document.getElementById("view type");
        show_tooltips = (view_type.checked == true);
        view_type = (view_type.checked) ? 'flow-images' : 'flow';
        if (model !== null) {
            model.getView(selected_view,
                          view_type,
                          function(svg) {
                              route_view.draw(svg.responseXML, show_tooltips, true);
                              route_plan.init(view_start_node);
                          });
        }
    }
    
    show_thumbnails_view = function () {
        if (model !== null) {
            model.getView(selected_view,
                          'flow-images',
                          function(svg) {thumbnails_view.draw(svg.responseXML);});
        }
    }

    show_screens_view = function () {
        if (model !== null) {
            model.getView(selected_view,
                          'flow-images',
                          function(svg) {screens_view.draw(svg.responseXML);});
        }
    }

    show_simple_flow_view = function () {
        var view_type = 'simple-flow-images';
        if (model !== null) {
            model.getView(selected_view,
                  view_type,
                  function(svg) {
                      route_view.draw(svg.responseXML, false, false);
                      route_plan.init(view_start_node);
                  });
            document.getElementById('download').style.visibility = 'visible';
        }
    }
    
    hide_simple_flow_view = function() {
        document.getElementById('download').style.visibility = 'hidden';
    }

    this.download_simplified_view = function () {
        var downloadable_name = model.getName();
        if (downloadable_name.search('.') !== -1) {
            downloadable_name = downloadable_name.split('.')[0];
        }
        downloadable_name = downloadable_name + '-' + selected_view + '-simple.zip';
        document.location.href = 'projects/' + model.getName() + '/' + selected_view + '/' + downloadable_name;
    }

    this.compare_model = function () {
        if (model !== null) {
            window.open('compare.html?model=' + model.getName(), '_blank');
            window.focus();
        }
    }
    
    route_plan = new RoutePlan(document.getElementById('selections'));
    route_view = new RouteView(document.getElementById('route planner'), route_plan.add_step);

    runs_list = new RunList(document.getElementById('runs'), show_error);

    screens_view = new ScreensView(document.getElementById('route planner'));
    thumbnails_view = new ThumbnailsView(document.getElementById('route planner'));
    run_plan_view = new RunPlanView(document.getElementById('route planner'), this.request_run, this.load_selected_view);

    tab_control = new TabbedViewControl();
    tab_control.addView(document.getElementById('route planner tab'), show_route_view);
    tab_control.addView(document.getElementById('thumbnails view tab'), show_thumbnails_view);
    tab_control.addView(document.getElementById('screen view tab'), show_screens_view);
    tab_control.addView(document.getElementById('simplified view tab'), show_simple_flow_view, hide_simple_flow_view);

    document.getElementById('models').addEventListener('change', this.load_selected_model);
    
    document.getElementById('delete project').addEventListener('click', this.delete_selected_model);
    
    document.getElementById('views').addEventListener('change', this.load_selected_view);
    document.getElementById('Make Run').addEventListener('click', this.solve_route);

    document.getElementById('view type').addEventListener('click', this.load_selected_view);
    document.getElementById('reload').addEventListener('click', this.reload_selected_view);
    document.getElementById('reload2').addEventListener('click', this.reload_selected_view);

    document.getElementById('download').addEventListener('click', this.download_simplified_view);
    
    document.getElementById('autorefresh').addEventListener('change', this.reload_and_schedule);
    
    document.getElementById('compare').addEventListener('click', this.compare_model);

    document.getElementById("user").innerText = getCookie("username");
    
    Model.getModels(this.load_models_list, show_error);
    tab_control.getView(0).show();
}

function logout() {
	setCookie("username", "", 30);
	window.location.replace('login2.html');
}
