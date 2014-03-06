/*jslint indent: 4, maxerr: 50, browser: true, devel: true */
'use strict';

/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function RouteView(container_element, on_click_function) {
    var container, on_click, removeTitles, removeMainTitle, fixEdgeTitles,
        get_click_function, addClickHandler, addLogInfo, addIcons, has_hd_activity;

    container = container_element;
    on_click = on_click_function;
    
    this.clear = function () {
        removeChilds(container);
    };
    
    this.draw = function (svg_doc, show_tooltips, enable_clicks, model, images_mode) {
        /*
            Draws this svg into the container, fixing minor svg issues and
            adding click handling to the map
        */
        this.clear();
        var node = document.importNode(svg_doc.documentElement, true);
        node.id = 'svg map';
        if (show_tooltips === false) {
            removeTitles(node);
        } else {
            removeMainTitle(node);
            fixEdgeTitles(node);
        }
        if (images_mode)
            addLogInfo(model, node);
        addClickHandler(node, enable_clicks);
        node.onmousewheel=MouseWheelHandler;
        node.addEventListener("DOMMouseScroll", MouseWheelHandler, true);
        scaleToFit(node, container);
        container.appendChild(node);
    };
    
    removeTitles = function (node) {
        /*
          Removes all the title nodes and title attributes of the given node
          and it's descendants
        */
        var titles, links, i;
        //weirdest of weirds...
        while (true) {
            titles = node.getElementsByTagName("title");
            for (i = 0; i < titles.length; i += 1) {
                titles[i].parentNode.removeChild(titles[i]);
            }
            if (titles.length === 0) {
                break;
            }
        }
        
        links = node.getElementsByTagName("a");
        for (i = 0; i < links.length; i += 1) {
            links[i].removeAttribute('xlink:title');
        }
    };
    
    removeMainTitle = function (node) {
        /*
            Remove the annoying main title from the svg
        */
        var titles, i;
        titles = node.getElementsByTagName("title");
        for (i = 0; i < titles.length; i += 1) {
            if (titles[i].textContent === 'finite_state_machine') {
                titles[i].parentNode.removeChild(titles[i]);
                break;
            }
        }
    };
    
    fixEdgeTitles = function (node) {
        /*
            Fix the titles in the links by removing the enclosing quotes and
            for edges it removes the 1st part (as the format is Node.Edge)
        */
        var links, link, i, candidate;
        
        links = node.getElementsByTagName("a");
        for (i = 0; i < links.length; i += 1) {
            link = links[i];
            if (link.getAttribute('xlink:title') === '<TABLE>') {
                candidate = link.getAttribute('xlink:href');
                candidate = candidate.slice(1, -1);
                candidate = candidate.split(".")[1];
                link.setAttribute('xlink:title', candidate);
            }
        }
    };
    
    addIcons = function (parent, images, x, y, click_fn) {
        var this_img,
            next_x,
            next_y;
        
        for (var i = 0; i < images.length; i++) {
            this_img = images[i];
            var svgimg = document.createElementNS('http://www.w3.org/2000/svg','image');
            if (this_img === "hdsave.png") {
                svgimg.setAttribute('width','16px');
                svgimg.setAttribute('height','16px');
                next_x = x + 16 + 3;
                next_y = y;
                this_img = "hd.svg";
            } else if (this_img === "network.png") {
                svgimg.setAttribute('width','18px');
                svgimg.setAttribute('height','16px');
                next_x = x + 18 + 3;
                next_y = y;
                this_img = "network.svg";
            }else {
                svgimg.setAttribute('width','16px');
                svgimg.setAttribute('height','16px');
                next_x = x + 16 + 3;
                next_y = y;
                this_img = "registry.svg";
            }
            svgimg.setAttribute('id','testimg2');
            svgimg.setAttributeNS('http://www.w3.org/1999/xlink', 'href', this_img);
            svgimg.setAttribute('x', x);
            svgimg.setAttribute('y', y);
            svgimg.addEventListener("click", click_fn);
            svgimg.style.cursor = 'pointer';
            parent.appendChild(svgimg);
            x = next_x;
            y = next_y;
        }
    };
    
    function later(graph, i, images, fn) {
        var images_copy = images.slice(0);
        setTimeout(function() {
            var bbox = i.getBBox();
            addIcons(graph,
                     images_copy,
                     i.x.baseVal.getItem(0).value + (bbox.width / 2) + 3,
                     i.y.baseVal.getItem(0).value - ((bbox.height / 2) + 18),
                     fn);
        }, 0);
    };
    
    function show_edge_logs_fn(model, node_name, edge_name) {
        return function(evt) {
            new EdgeEventsView(model, node_name, edge_name).show();
        };
    }
    
    addLogInfo = function (model, node) {
        var i, j, bbox,
            graph = node.getElementsByClassName("graph")[0],
            edges = node.getElementsByClassName("edge"),
            has_network_activity = true,
            elem = null,
            node_name = null,
            edge_name = null,
            images = null,
            an_edge_log = null,
            graph_logs = null;
            
        graph_logs = model.get_graph_logs();
            
        for (i = 0; i < edges.length; i += 1) {
            node_name = edges[i].getElementsByTagName("a")[0].href.baseVal;
            node_name = node_name.substr(1, node_name.length - 2).split(".");
            edge_name = node_name[1];
            node_name = node_name[0];
            
            //an_edge_log = model.get_edge_logs(node_name, edge_name);
            an_edge_log = graph_logs[node_name + "." + edge_name];
            
            if (an_edge_log !== undefined && an_edge_log.hasActivity() === true) {
                images = [];
                if (an_edge_log.hasDiskActivity() === true) {
                    images.push('hdsave.png');
                }
                if (an_edge_log.hasNetworkActivity() === true) {
                    images.push('network.png');
                }
                if (an_edge_log.hasRegistryActivity() === true) {
                    images.push('registry.png');
                }
                
                elem = edges[i].getElementsByTagName("image")[0];
                if (elem) {
                    addIcons(graph,
                             images,
                             elem.x.baseVal.value + elem.width.baseVal.value - (3 + 16 + 3 + 8 + 3 + 16),
                             elem.y.baseVal.value,
                             show_edge_logs_fn(model, node_name, edge_name));
                } else {
                    elem = edges[i].getElementsByTagName("text")[0];
                    later(graph, elem, images, show_edge_logs_fn(model, node_name, edge_name));
                }
            }
        }
    };
    
    get_click_function = function (destination) {
        return function () { on_click(destination);
            };
    };
    
    addClickHandler = function (node, enable) {
        /*
          Installs proper click handling on the links
         */
        var links, link, i, destination;
        links = node.getElementsByTagName("a");
        for (i = 0; i < links.length; i += 1) {
            link = links[i];
            destination = link.getAttribute('xlink:href').slice(1, -1);
            link.removeAttribute('xlink:href');
            if (on_click !== undefined && on_click !== null && enable === true) {
                link.addEventListener('click', get_click_function(destination), false);
                link.style.cursor = 'pointer';
            }
        }
    };
}
