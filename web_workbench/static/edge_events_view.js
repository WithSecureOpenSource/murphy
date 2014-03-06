/*jslint indent: 4, maxerr: 50, browser: true */
"use strict";

function EdgeEventsView(model, node_name, edge_name) {
    var _model = model,
        _node = node_name,
        _edge = edge_name,
        _addPath,
        _addRows,
        _addRowsHeader,
        _addSection;
    
    _addPath = function (trace, container) {
        var i, text = "";
        
        for (i = 0; i < trace.length; i++) {
            text += trace[i] + " => ";
        }
        text = text.slice(0, -4);
        var node = document.createTextNode("Path traversed:");
        container.appendChild(node);
        container.appendChild(document.createElement("br"));
        container.appendChild(document.createElement("br"));
        
        node = document.createTextNode(text);
        container.appendChild(node);
        container.appendChild(document.createElement("br"));
        container.appendChild(document.createElement("br"));
    };

    _addSection = function (data, content_panel, section, header) {
        var traces = data.instrumentation[section];
        for (var key in traces) {
            _addPath(data.instrumentation.traces[key], content_panel);
            var ops = traces[key];
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
        for (var row = 0; row < ops.length; row++) {
            var node = document.createTextNode(JSON.stringify(ops[row]));
            content_panel.appendChild(node);
            content_panel.appendChild(document.createElement("br"));
        }
        content_panel.appendChild(document.createElement("br"));
        content_panel.appendChild(document.createElement("br"));
    };
    
    this.show = function() {
        var background_panel,
            data;
        
        background_panel = document.createElement("div");
        background_panel.className = 'popup-background-pane';
        background_panel.style.width = getWidth(document.body);
        background_panel.style.height = getHeight(document.body);
        
        var width = parseInt(getWidth(document.body) * 0.4),
            height = parseInt(getHeight(document.body) * 0.8),
            left = (getWidth(document.body) - width) / 2,
            top = (getHeight(document.body) - height) / 2;

        document.body.appendChild(background_panel);

        data = _model.get_edge_logs(_node, _edge);
        if (data !== null) {
            data = data.data();
        }
        
        var content_panel = document.createElement("div");
        content_panel.style.overflow = "auto";
        content_panel.style.userSelect = "text";
        content_panel.style.webkitUserSelect = "text";
        content_panel.style.whiteSpace = "nowrap";
        
        if ('WriteFile' in data.instrumentation) {
            _addSection(data, content_panel, "WriteFile", "File operations:");
        }
        if ('TCP Receive' in data.instrumentation) {
            _addSection(data, content_panel, "TCP Receive", "Network read:");
        }
        if ('RegSetValue' in data.instrumentation) {
            _addSection(data, content_panel, "RegSetValue", "Registry writes:");
        }

        require(["scripts/window"], function(Window) {
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
