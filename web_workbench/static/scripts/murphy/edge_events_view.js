/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, require, document*/

define(["scripts/murphy/utils.js"], function (utils) {
    "use strict";

    var EdgeEventsView = function (model, node_name, edge_name) {
        var _model = model,
            _node = node_name,
            _edge = edge_name,
            _addPath,
            _addRows,
            _addRowsHeader,
            _addSection,
            _show_text_instead_fn;

        _show_text_instead_fn = function (evt) {
            var elem = document.createElement("div");
            elem.appendChild(document.createTextNode(evt.srcElement.alt));
            elem.style.display = "inline-block";
            elem.style.verticalAlign = "middle";
            evt.srcElement.parentElement.insertBefore(elem, evt.srcElement);
            evt.srcElement.parentElement.removeChild(evt.srcElement);
        };

        _addPath = function (trace, container) {
            var i,
                text = "",
                flow_div = document.createElement("div"),
                proj_path = "/murphy/projects/" + _model.getName() + "/All/",
                img,
                nodepath,
                node,
                edge;

            flow_div.style.padding = "10px";
            for (i = 0; i < trace.length; i += 1) {
                nodepath = trace[i].split(".");
                node = nodepath[0];
                edge = nodepath[1];

                if (i > 0) {
                    img = document.createElement("img");
                    img.style.padding = "5px";
                    img.src = "/img/arr_right.png";
                    img.style.display = "inline-block";
                    img.style.verticalAlign = "middle";
                    flow_div.appendChild(img);
                }

                img = document.createElement("img");
                if (node === "Node 0") {
                    img.src = proj_path + node.replace(/ /g, "_") + "0.1.ref.png";
                } else {
                    img.src = proj_path + node.replace(/ /g, "_") + ".0.ref.png";
                }
                img.style.display = "inline-block";
                img.style.verticalAlign = "middle";
                img.style.maxWidth = "100px";
                img.style.maxHeight = "50px";
                img.style.padding = "5px";
                flow_div.appendChild(img);

                img = document.createElement("img");
                img.style.padding = "5px";
                img.src = "/img/arr_right.png";
                img.style.display = "inline-block";
                img.style.verticalAlign = "middle";
                flow_div.appendChild(img);

                img = document.createElement("img");
                img.src = proj_path + node.replace(/ /g, "_") + ".edge." + edge.replace(/ /g, "_") + ".0.png";
                img.alt = edge;
                img.addEventListener("error", _show_text_instead_fn);
                img.style.maxWidth = "100px";
                img.style.maxHeight = "50px";
                img.style.display = "inline-block";
                img.style.verticalAlign = "middle";
                img.style.padding = "5px";
                flow_div.appendChild(img);

                text += trace[i] + " => ";
            }
            text = text.slice(0, -4);
            container.appendChild(flow_div);
            container.appendChild(document.createElement("br"));
        };

        _addSection = function (data, content_panel, section, header) {
            var traces = data.instrumentation[section],
                key,
                ops;
            for (key in traces) {
                _addPath(data.instrumentation.traces[key], content_panel);
                ops = traces[key];
                _addRowsHeader(content_panel, header);
                _addRows(content_panel, ops);
            }
        };

        _addRowsHeader = function (content_panel, header) {
            var node = document.createTextNode(header);
            content_panel.appendChild(node);
            content_panel.appendChild(document.createElement("br"));
            content_panel.appendChild(document.createElement("br"));
        };

        _addRows = function (content_panel, ops) {
            var row,
                node;
            for (row = 0; row < ops.length; row += 1) {
                node = document.createTextNode(JSON.stringify(ops[row]));
                content_panel.appendChild(node);
                content_panel.appendChild(document.createElement("br"));
            }
            content_panel.appendChild(document.createElement("br"));
            content_panel.appendChild(document.createElement("br"));
        };

        this.show = function () {
            var background_panel,
                data,
                width,
                height,
                left,
                top,
                content_panel;

            background_panel = document.createElement("div");
            background_panel.className = 'popup-background-pane';
            background_panel.style.width = utils.getComputedWidth(document.body);
            background_panel.style.height = utils.getComputedHeight(document.body);

            width = Math.round(utils.getComputedWidth(document.body) * 0.6);
            height = Math.round(utils.getComputedHeight(document.body) * 0.8);
            left = Math.round((utils.getComputedWidth(document.body) - width) / 2);
            top = Math.round((utils.getComputedHeight(document.body) - height) / 2);

            document.body.appendChild(background_panel);

            data = _model.get_edge_logs(_node, _edge);
            if (data !== null) {
                data = data.data();
            }

            content_panel = document.createElement("div");
            content_panel.style.overflow = "auto";
            content_panel.style.userSelect = "text";
            content_panel.style.webkitUserSelect = "text";
            content_panel.style.whiteSpace = "nowrap";

            if (data.instrumentation.WriteFile !== undefined) {
                _addSection(data, content_panel, "WriteFile", "File operations:");
            }
            if (data.instrumentation['TCP Receive'] !== undefined) {
                _addSection(data, content_panel, "TCP Receive", "Network read:");
            }
            if (data.instrumentation.RegSetValue !== undefined) {
                _addSection(data, content_panel, "RegSetValue", "Registry writes:");
            }

            require(["scripts/window"], function (Window) {
                var win = new Window();
                win.content.appendChild(content_panel);
                win.title = _edge;

                win.setRect(left, top, width, height);
                win.on_closed = function () {
                    document.body.removeChild(background_panel);
                };
                background_panel.addEventListener('click', function (evt) {
                    win.dispose();
                });
            });
        };
    };
    return {EdgeEventsView: EdgeEventsView};
});
