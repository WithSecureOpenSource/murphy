/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document, alert, setTimeout, confirm, window*/

define(["scripts/murphy/model.js",
        "scripts/murphy/utils.js",
        "scripts/murphy/tab_view_control.js",
        'scripts/murphy/run_list_view.js',
        "scripts/murphy/channel_view.js",
        'scripts/murphy/route_plan_list.js',
        'scripts/murphy/log.js',
        'scripts/murphy/new_model_view.js',
        'scripts/murphy/route_view.js',
        'scripts/murphy/screens_view.js',
        'scripts/murphy/thumbnails_view.js',
        'scripts/murphy/dismantler_view.js',
        'scripts/murphy/run_plan_view.js'], function (models, utils, tab_view, run_list_view, channel_view, route_plan_list,
            log_module, new_model_module, route_view_module, screens_view_module, thumbnails_module, dismantler_view_module, run_plan_module) {
    "use strict";
    var Application = function () { //(models, utils, tab_view) {
            var model = null,
                selected_view = null,
                view_start_node = null,
                route_plan, runs_list, tab_control, route_view, screens_view, thumbnails_view, dismantler_view,
                show_route_view, show_thumbnails_view, show_screens_view, show_simple_flow_view, show_dismantler_view,
                hide_simple_flow_view, run_plan_view,
                initializing = true,
                live_receiver = null,
                show_error,
                adjustSizeableAreaDimensions,
                collapse_toolbox,
                expand_toolbox,
                clear_content,
                that = this;

            show_error = function (error) {
                var msg = error;
                if (error.stack !== undefined) {
                    msg += "\n" + error.stack;
                }
                alert("Error occurred:\n" + msg);
            };

            clear_content = function () {
                utils.removeChilds(document.getElementById('route planner'));
            };

            adjustSizeableAreaDimensions = function () {
                var doc_width, doc_height, map_coords, map_width, map_height, scroll_left, scroll_top;

                doc_width = utils.getComputedWidth(document.body);
                doc_height = utils.getComputedHeight(document.body);
                map_coords = utils.getOffset(document.getElementById('route planner'));
                scroll_left = document.getElementById('route planner').scrollLeft;
                scroll_top = document.getElementById('route planner').scrollTop;
                map_width = doc_width - (scroll_left + map_coords.left);
                map_height = doc_height - (scroll_top + map_coords.top);
                document.getElementById('route planner').style.width = map_width + 'px';
                document.getElementById('route planner').style.height = map_height + 'px';
            };

            collapse_toolbox = function () {
                document.getElementById('left bar').style.display = 'none';
                document.getElementById('collapsed left bar').style.display = 'inline-block';
                adjustSizeableAreaDimensions();
            };

            expand_toolbox = function () {
                document.getElementById('left bar').style.display = 'inline-block';
                document.getElementById('collapsed left bar').style.display = 'none';
                adjustSizeableAreaDimensions();
            };


            this.load_models_list = function (models) {
                var models_list = document.getElementById("models"),
                    scrap,
                    i;
                utils.loadSelectWithArray(models_list, models, true);
                if (initializing === true) {
                    scrap = utils.getCookie("autoscrap");
                    if (scrap !== undefined && scrap !== "") {
                        utils.setCookie("autoscrap", "", 30);
                        for (i = 0; i < models_list.options.length; i += 1) {
                            if (models_list.options.item(i).text === scrap) {
                                models_list.selectedIndex = i;
                                that.load_model(scrap);
                                document.getElementById('autorefresh').click();
                                break;
                            }
                        }
                    }
                    initializing = false;
                }
            };

            this.load_view_list = function (views) {
                var option, i, view_list;
                view_list = document.getElementById("views");
                utils.clearSelect(view_list);
                for (i = 0; i < views.length; i += 1) {
                    option = document.createElement("option");
                    option.text = views[i].name;
                    option.value = views[i].starts_at;
                    view_list.add(option);
                }
                view_list.selectedIndex = 0;
                that.load_selected_view();
            };

            this.load_model = function (name) {
                selected_view = null;
                clear_content();
                runs_list.reload(name);
                route_plan.init();
                if (live_receiver !== null) {
                    live_receiver.dispose();
                    live_receiver = null;
                }
                if (name === '') {
                    model = null;
                    var view_list = document.getElementById("views");
                    utils.loadSelectWithArray(view_list, [], false);
                    document.getElementById('download').style.visibility = 'hidden';
                    document.getElementById('compare').href = null;
                    document.getElementById("delete project").disabled = true;
                } else {
                    model = new models.Model(name, show_error);
                    model.getViews(this.load_view_list);
                    document.getElementById('compare').href = "#";
                    document.getElementById("delete project").disabled = false;
                }
            };

            this.load_selected_model = function () {
                var models_list, model_name;
                models_list = document.getElementById('models');
                model_name = models_list.options[models_list.selectedIndex].text;
                that.load_model(model_name);
            };

            this.toggle_live_transmission = function () {
                if (document.getElementById('autorefresh').checked === true) {
                    if (model !== null) {
                        if (live_receiver === null) {
                            var channel = model.get_live_channel();
                            if (channel !== "") {
                                live_receiver = new channel_view.ChannelView(model.getName(), function () {
                                    if (document.getElementById('autorefresh').checked === true) {
                                        document.getElementById('autorefresh').click();
                                        that.reload_selected_view();
                                    }
                                });
                                live_receiver.show();
                            }
                        } else {
                            alert("not handled 1");
                        }
                    } else {
                        live_receiver.dispose();
                        live_receiver = null;
                    }
                } else {
                    if (live_receiver !== null) {
                        live_receiver.dispose();
                        live_receiver = null;
                    }
                }
            };

            this.reload_and_schedule = function () {
                if (document.getElementById('autorefresh').checked === true && model !== null) {
                    that.reload_selected_view();
                    setTimeout(that.reload_and_schedule, 5000);
                }
            };

            this.delete_selected_model = function () {
                if (model !== null) {
                    if (confirm("Will delete " + model.getName() + ", are you really sure? (cannot be undone)")) {
                        model.delete_model(function () {
                            window.location.reload(true);
                        });
                    }
                }
            };

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
            };

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
            };

            this.solve_route = function () {
                var steps = route_plan.get_steps();
                clear_content();
                model.solveRun(steps, run_plan_view.show);
            };

            this.request_run = function (plan) {
                var full_plan = {};
                full_plan.model = model.getName();
                full_plan.plan = plan;
                model.requestRun(full_plan, function (run_id) {
                    var run = new log_module.RunLog(model.getName(), run_id, "Running...", true);
                    runs_list.addRun(run);
                    tab_control.active_view.show();
                });
            };

            this.create_new_model = function () {
                document.getElementById("models").selectedIndex = 0;
                that.load_model("");
                var create_model_view = new new_model_module.NewModelView(document.getElementById('route planner'),
                                                                function () { that.load_model(""); });
                clear_content();
                create_model_view.show();
            };

            show_route_view = function () {
                var view_type, show_tooltips;

                view_type = document.getElementById("view type");
                show_tooltips = (view_type.checked === true);
                view_type = (view_type.checked) ? 'flow-images' : 'flow';
                if (model !== null) {
                    model.getView(selected_view,
                                  view_type,
                                  function (svg) {
                                      route_view.draw(svg.responseXML, show_tooltips, true, model, view_type === 'flow-images');
                                      route_plan.init(view_start_node);
                        });
                }
            };

            show_dismantler_view = function () {
                if (model !== null) {
                    model.getView(selected_view,
                                  'flow-images',
                                  function (svg) {
                                      dismantler_view.draw(svg.responseXML, true, model);
                                      route_plan.init(view_start_node);
                        });
                }
            };
            
            show_thumbnails_view = function () {
                if (model !== null) {
                    model.getView(selected_view,
                                  'flow-images',
                                  function (svg) {thumbnails_view.draw(svg.responseXML); });
                }
            };

            show_screens_view = function () {
                if (model !== null) {
                    model.getView(selected_view,
                                  'flow-images',
                                  function (svg) {screens_view.draw(svg.responseXML); });
                }
            };

            show_simple_flow_view = function () {
                var view_type = 'simple-flow-images';
                if (model !== null) {
                    model.getView(selected_view,
                                  view_type,
                                  function (svg) {
                                      route_view.draw(svg.responseXML, false, false, model);
                                      route_plan.init(view_start_node);
                        });
                    document.getElementById('download').style.visibility = 'visible';
                }
            };

            hide_simple_flow_view = function () {
                document.getElementById('download').style.visibility = 'hidden';
            };

            this.download_simplified_view = function () {
                var downloadable_name = model.getName();
                if (downloadable_name.search('.') !== -1) {
                    downloadable_name = downloadable_name.split('.')[0];
                }
                downloadable_name = downloadable_name + '-' + selected_view + '-simple.zip';
                document.location.href = 'projects/' + model.getName() + '/' + selected_view + '/' + downloadable_name;
            };

            this.compare_model = function () {
                if (model !== null) {
                    window.open('compare.html?model=' + model.getName(), '_blank');
                    window.focus();
                }
            };

            route_plan = new route_plan_list.RoutePlan(document.getElementById('selections'));
            route_view = new route_view_module.RouteView(document.getElementById('route planner'), route_plan.add_step);
            runs_list = new run_list_view.RunList(document.getElementById('runs'), show_error);
            screens_view = new screens_view_module.ScreensView(document.getElementById('route planner'));
            thumbnails_view = new thumbnails_module.ThumbnailsView(document.getElementById('route planner'));
            dismantler_view = new dismantler_view_module.DismantlerView(document.getElementById('route planner'));
            run_plan_view = new run_plan_module.RunPlanView(document.getElementById('route planner'), that.request_run, that.load_selected_view);

            tab_control = new tab_view.TabbedViewControl();
            tab_control.addView(document.getElementById('route planner tab'), show_route_view);
            tab_control.addView(document.getElementById('thumbnails view tab'), show_thumbnails_view);
            tab_control.addView(document.getElementById('screen view tab'), show_screens_view);
            tab_control.addView(document.getElementById('simplified view tab'), show_simple_flow_view, hide_simple_flow_view);
            tab_control.addView(document.getElementById('dismantler view tab'), show_dismantler_view);

            document.getElementById('models').addEventListener('change', this.load_selected_model);

            document.getElementById('delete project').addEventListener('click', this.delete_selected_model);

            document.getElementById('new project').addEventListener('click', this.create_new_model);

            document.getElementById('views').addEventListener('change', this.load_selected_view);
            document.getElementById('Make Run').addEventListener('click', this.solve_route);

            document.getElementById('view type').addEventListener('click', this.load_selected_view);
            document.getElementById('reload').addEventListener('click', this.reload_selected_view);
            document.getElementById('reload2').addEventListener('click', this.reload_selected_view);

            document.getElementById('download').addEventListener('click', this.download_simplified_view);

            document.getElementById('autorefresh').addEventListener('change', this.reload_and_schedule);
            document.getElementById('autorefresh').addEventListener('change', this.toggle_live_transmission);

            document.getElementById('compare').addEventListener('click', this.compare_model);

            document.getElementById("user").innerText = utils.getCookie("username");

            document.getElementById('collapse').addEventListener('click', collapse_toolbox);
            document.getElementById('expand').addEventListener('click', expand_toolbox);

            
            document.getElementById('logout user').addEventListener('click', function (evt) {
                evt.preventDefault();
                utils.setCookie("username", "", 30);
                window.location.replace('login2.html');
            });
            
            document.body.addEventListener('resize', adjustSizeableAreaDimensions);
            window.addEventListener('resize', adjustSizeableAreaDimensions);
            adjustSizeableAreaDimensions();

            models.getModels(this.load_models_list, show_error);
            tab_control.getView(0).show();
        };

    return {
        Application: Application,
    };
});

