/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, require, document, location, setTimeout, MouseWheelHandler, scaleToFit*/

define(["scripts/murphy/utils.js", "scripts/murphy/svg_navigation.js"], function (utils, svg_module) {
    "use strict";
    var DismantlerView = function (container_element) {
            var container, removeTitles, removeMainTitle, fixEdgeTitles,
                get_click_function, addClickHandler, _model, dismantle;

            container = container_element;

            this.draw = function (svg_doc, enable_clicks, model) {
                /*
                    Draws this svg into the container, fixing minor svg issues and
                    adding click handling to the map
                */
                utils.removeChilds(container);
                var node = document.importNode(svg_doc.documentElement, true);
                node.id = 'svg map';
                removeMainTitle(node);
                fixEdgeTitles(node);
                addClickHandler(node);
                node.onmousewheel = svg_module.MouseWheelHandler;
                node.addEventListener("DOMMouseScroll", svg_module.MouseWheelHandler, true);
                svg_module.scaleToFit(node, container);
                container.appendChild(node);
                _model = model;
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

            dismantle = function (panel, obj) {
                if (obj.HERE !== undefined && obj.HERE.custom !== undefined && obj.HERE.custom.scraper !== undefined && obj.HERE.custom.scraper === "windows api") {
                    var childs = obj.HERE.custom.scrap.childs,
                        index,
                        child,
                        root,
                        window_elem,
                        elem,
                        orig_x,
                        orig_y,
                        image;
                    
                    image = new Image();
                    image.src = "/murphy/get_node_image/" + _model.getName() + "/" + obj.HERE.desc;
                    image.addEventListener("load", function () {
                    
                        var canvas = document.createElement("canvas");
                        canvas.width = image.width;
                        canvas.height = image.height;
                        canvas.getContext('2d').drawImage(image, 0, 0, image.width, image.height);                    
                    
                        child = obj.HERE.custom.scrap;
                        
                        orig_x = child.rect.left;
                        orig_y = child.rect.top;
                        root = child;
                        window_elem = document.createElement("div");
                        window_elem.style.position = 'absolute';
                        window_elem.style.left = "30px";
                        window_elem.style.top = "30px";
                        window_elem.style.width = (child.rect.right - child.rect.left) + "px";
                        window_elem.style.height = (child.rect.bottom - child.rect.top) + "px";
                        window_elem.style.overflow = "hidden";
                        
                        window_elem.style.border = "1px solid #000000";
                        panel.appendChild(window_elem);

                        var data = canvas.getContext('2d').getImageData(10, image.height - 30, 1, 1).data;
                        window_elem.style.backgroundColor = "#" + data[0].toString(16) + data[1].toString(16) + data[2].toString(16);
                        
                        for (index = 0; index < childs.length; index++) {
                            child = childs[index];
                            if (child.class === "Button") {
                                if (child.text == "Destination Folder") {
                                    elem = document.createElement("div");
                                } else {
                                    elem = document.createElement("input");
                                    elem.type = "button";
                                    elem.value = child.text.replace("&", "");
                                    if (child.enabled === false) {
                                        elem.disabled = true;
                                    }
                                }
                            } else if (child.class === "Static") {
                                elem = document.createElement("span");
                                elem.textContent = child.text;
                                data = canvas.getContext('2d').getImageData((child.rect.left - root.rect.left) + 1, (child.rect.top - root.rect.top) + 1, 1, 1).data;
                                elem.style.backgroundColor = "#" + data[0].toString(16) + data[1].toString(16) + data[2].toString(16);
                            } else if (child.class === "Edit") {
                                elem = document.createElement("input");
                                elem.type = "text";
                                elem.value = child["wm text"];
                            } else {
                                elem = document.createElement("div");
                                data = canvas.getContext('2d').getImageData((child.rect.left - root.rect.left) + 4, (child.rect.top - root.rect.top) + 4, 1, 1).data;
                                elem.style.backgroundColor = "#" + data[0].toString(16) + data[1].toString(16) + data[2].toString(16);
                            }
                            elem.style.fontSize = "11px";
                            elem.style.position = 'absolute';
                            elem.style.whiteSpace = 'normal';
                            elem.style.left = (child.rect.left - orig_x) + "px";
                            elem.style.top = (child.rect.top - orig_y) + "px";
                            elem.style.width = (child.rect.right - child.rect.left) + "px";
                            elem.style.height = (child.rect.bottom - child.rect.top) + "px";
                            //elem.style.border = "1px solid #00ff00";
                            window_elem.appendChild(elem);
                        }
                    });
                } else {
                    panel.textContent = "Dont know how to dump this: " + JSON.stringify(obj);
                }
            };
            
            get_click_function = function (destination) {
                return function () {
                    require(["scripts/window"], function (Window) {
                        var background_panel = document.createElement("div"),
                            win,
                            content_panel = document.createElement("div"),
                            left,
                            top,
                            width,
                            height;

                        background_panel.className = 'popup-background-pane';
                        background_panel.style.width = utils.getComputedWidth(document.body);
                        background_panel.style.height = utils.getComputedHeight(document.body);
                        document.body.appendChild(background_panel);

                        win = new Window();
                        width = Math.round(utils.getComputedWidth(document.body) * 0.6);
                        height = Math.round(utils.getComputedHeight(document.body) * 0.8);
                        left = Math.round((utils.getComputedWidth(document.body) - width) / 2);
                        top = Math.round((utils.getComputedHeight(document.body) - height) / 2);

                        content_panel.style.overflow = "auto";
                        content_panel.style.userSelect = "text";
                        content_panel.style.webkitUserSelect = "text";
                        content_panel.style.whiteSpace = "nowrap";
                        win.content.appendChild(content_panel);
                        win.title = "Dismantled!";

                        win.setRect(left, top, width, height);
                        win.on_closed = function () {
                            document.body.removeChild(background_panel);
                        };
                        background_panel.addEventListener('click', function (evt) {
                            win.dispose();
                        });
                        
                        var xhr = new XMLHttpRequest();
                        xhr.open('POST', "/murphy/get_node_json", true);
                        xhr.onreadystatechange = function () {
                            if (xhr.readyState === 4) {
                                try {
                                    if (xhr.status !== 200) {
                                        alert(xhr.responseText);
                                    } else {
                                        var object = JSON.parse(xhr.responseText);
                                        if (object.status === 'fail') {
                                            alert(object.text);
                                        } else {
                                            dismantle(content_panel, object.response);
                                        }
                                    }
                                } catch (err) {
                                    alert(err);
                                }
                            }
                        };
                        xhr.send(JSON.stringify({model: _model.getName(), node: destination}));
                    });
                    //alert("clicked on " + destination);
                };
            };

            addClickHandler = function (node) {
                /*
                  Installs proper click handling on the links
                 */
                var links, link, i, destination;
                links = node.getElementsByTagName("a");
                for (i = 0; i < links.length; i += 1) {
                    link = links[i];
                    destination = link.getAttribute('xlink:href').slice(1, -1);
                    link.removeAttribute('xlink:href');
                    link.addEventListener('click', get_click_function(destination), false);
                    link.style.cursor = 'pointer';
                }
            };
        };
    return {DismantlerView: DismantlerView};
});

