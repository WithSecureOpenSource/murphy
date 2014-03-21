/*jslint indent: 4, maxerr: 50, nomen: true */
/*global define, document, window */

define(["scripts/drag"], function (drag) {
    "use strict";
    var _all_windows = [],
        Element,
        LayoutProperty,
        Layout,
        HorizontalLayout,
        VerticalLayout,
        TitleBar,
        BorderSizer;

    /*
        Still tons of things to do but is a starting point for a minimalistic
        windowing helper library, main purpose is to have some easy popup
        windows to overlap content with a page
     */
    LayoutProperty = function (layout, elem) {
        var _layout = layout,
            _element = elem,
            _expands = false;

        this.getExpands = function () {
            return _expands;
        };
        this.setExpands = function (stretches) {
            var elem = _element.getHtmlElement();
            if (stretches) {
                elem.classList.remove("layout_element_compact_class");
                elem.classList.add("layout_element_stretch_class");
                _expands = true;
            } else {
                elem.classList.remove("layout_element_stretch_class");
                elem.classList.add("layout_element_compact_class");
                _expands = false;
            }
        };
        this.getLayout = function () {
            return _layout;
        };
        this.setExpands(false);
    };

    Layout = function (parent, direction) {
        /*
            Direction: 0 - horizontal, 1 - vertical
         */
        var _parent = parent,
            _elements = [];

        _parent.getHtmlElement().classList.add("layout_panel_class");
        if (direction === 1) {
            _parent.getHtmlElement().style.flexDirection = "column";
        }
        this.add = function (elem) {
            _parent.getHtmlElement().appendChild(elem.getHtmlElement());
            var layout_prop = new LayoutProperty(this, elem);
            _elements.push(layout_prop);
            return layout_prop;
        };
        this.getElement = function (index) {
            return _elements[index];
        };
        this.getElements = function () {
            return _elements.slice(0);
        };
        this.getDirection = function () {
            return 1;
        };
    };
    Element = function () {
        var _content = document.createElement("div"),
            _stretches = false,
            _layout = null;

        this.getHtmlElement = function () {
            return _content;
        };
    };
    TitleBar = function () {
        var _title_frame = new Element(),
            _layout = new Layout(_title_frame),
            _title = new Element(),
            _minimize = new Element(),
            _close = new Element(),
            img,
            _drag,
            _captured,
            _moved,
            _released,
            _that = this;

        _title_frame.getHtmlElement().classList.add("title_bar_class");
        _title_frame.getHtmlElement().classList.add("no-select");
        // menu, title, min, max, close buttons

        _title.getHtmlElement().style.overflow = "hidden";
        _title.getHtmlElement().style.cursor = 'url("/img/hand.cur"), default';
        _title.getHtmlElement().style.textAlign = 'center';
        _layout.add(_title).setExpands(true);

        img = document.createElement("img");
        img.src = "/img/minimize.png";
        _close.getHtmlElement().appendChild(img);
        _close.getHtmlElement().style.cursor = 'pointer';
        _layout.add(_close);

        this.getHtmlElement = function () {
            return _title_frame.getHtmlElement();
        };

        Object.defineProperty(this,
                              "title",
                                {get : function () {
                                    return _title.getHtmlElement().innerHTML;
                                 },
                                 set : function (new_title) {
                                    _title.getHtmlElement().innerHTML = new_title;
                                 },
                                 enumerable : true
                                });

        Object.defineProperty(this,
                               "on_closing",
                               {value : null,
                                writable : true,
                                enumerable : true,
                                configurable : true});

        Object.defineProperty(this,
                               "on_drag",
                               {value : null,
                                writable : true,
                                enumerable : true,
                                configurable : true});

        _close.getHtmlElement().addEventListener("click", function () {
            if (_that.on_closing !== null) {
                _that.on_closing();
            }
        });
        _captured = function () {
            _title.getHtmlElement().style.cursor = 'url("/img/grab.cur"), default';
        };
        _moved = function (evtobj, target_element, delta_x, delta_y, that_x) {
            if (_that.on_drag !== null) {
                _that.on_drag(delta_x, delta_y);
            }
        };
        _released = function () {
            _title.getHtmlElement().style.cursor = 'url("/img/hand.cur"), default';
        };
        _drag = new drag.Dragger(_title.getHtmlElement(), _captured, _moved, _released);
    };
    BorderSizer = function (element) {
        var _element = element,
            _sizing_cuadrant,
            _corner_width = 15, //FIXME: border needs to be accounted for, also they may differ in size...
            _corner_height = 15,
            _captured,
            _moved,
            _released,
            _drag,
            _cuadrant_locked = false,
            _that = this;

        _element.getHtmlElement().addEventListener("mousemove", function (evt) {
            if (_cuadrant_locked) {
                return;
            }
            if (evt.target === _element.getHtmlElement()) {
                var client = evt.target.getClientRects()[0],
                    x = evt.clientX - client.left,
                    y = evt.clientY - client.top;

                //8 cuadrants from top-left to right bottom, we know now it is on the borders
                if (x < _corner_width) { //cuadrant 0-3-5
                    if (y < _corner_height) {
                        _sizing_cuadrant = 0;
                    } else if (y < (client.height - _corner_height)) {
                        _sizing_cuadrant = 3;
                    } else {
                        _sizing_cuadrant = 5;
                    }
                } else if (x >= (client.width - _corner_width)) { // cuadrants 2-4-7
                    if (y < _corner_height) {
                        _sizing_cuadrant = 2;
                    } else if (y < (client.height - _corner_height)) {
                        _sizing_cuadrant = 4;
                    } else {
                        _sizing_cuadrant = 7;
                    }
                } else {
                    if (y < _corner_height) {
                        _sizing_cuadrant = 1;
                    } else {
                        _sizing_cuadrant = 6;
                    }
                }
                switch (_sizing_cuadrant) {
                case 0:
                case 7:
                    evt.target.style.cursor = 'nw-resize';
                    break;
                case 2:
                case 5:
                    evt.target.style.cursor = 'ne-resize';
                    break;
                case 1:
                case 6:
                    evt.target.style.cursor = 'n-resize';
                    break;
                case 3:
                case 4:
                    evt.target.style.cursor = 'e-resize';
                    break;
                }
            }
        }, false);

        Object.defineProperty(this,
                               "on_resizing",
                               {value : null,
                                writable : true,
                                enumerable : true,
                                configurable : true});

        _captured = function () {
            _cuadrant_locked = true;
        };
        _moved = function (evtobj, target_element, delta_x, delta_y, that_x) {
            if (_that.on_resizing !== null) {
                _that.on_resizing(_sizing_cuadrant, delta_x, delta_y);
            }
        };
        _released = function () {
            _cuadrant_locked = false;
        };
        _drag = new drag.Dragger(_element.getHtmlElement(), _captured, _moved, _released);
    };
    Window = function (parent) {
        var _parent = parent,
            _main_frame = new Element(),
            _layout = new Layout(_main_frame, 1),
            _client_area = new Element(),
            _title_bar = null,
            foo,
            _sizer = new BorderSizer(_main_frame),
            _that = this;

        foo = _main_frame.getHtmlElement();
        foo.className = "window_class";
        foo.style.left = 100;
        foo.style.top = 100;
        foo.style.width = 200;
        foo.style.height = 200;
        foo.id = "winX";

        foo = _client_area.getHtmlElement();
        foo.classList.add("client_area_class");

        if (_parent === undefined) {
            _parent = document.body;
        }
        _parent.appendChild(_main_frame.getHtmlElement());
        _all_windows.push(this);
        this.getMainFrame = function () {
            return _main_frame;
        };
        _title_bar = new TitleBar();
        _layout.add(_title_bar);
        _layout.add(_client_area).setExpands(true);
        _client_area.getHtmlElement().classList.add("client_area_class");

        this.setRect = function (left, top, width, height) {
            var elem = _main_frame.getHtmlElement(),
                style = window.getComputedStyle(elem, null),
                borderLeft = parseInt(style.borderLeftWidth),
                borderTop = parseInt(style.borderTopWidth),
                borderRight = parseInt(style.borderRightWidth),
                borderBottom = parseInt(style.borderBottomWidth);
                
            
            elem.style.left = (left) + "px";
            elem.style.top = (top) + "px";
            elem.style.width = (width - (borderLeft + borderRight)) + "px";
            elem.style.height = (height - (borderTop + borderBottom)) + "px";
        };
        
        this.dispose = function () {
            var elem = _main_frame.getHtmlElement();
            elem.parentElement.removeChild(elem);
            _all_windows.pop(_that);
            if (this.on_closed) {
                this.on_closed();
            }
        };
        Object.defineProperty(this,
                              "visible",
                                {get : function () {
                                    return _main_frame.getHtmlElement().parentElement !== null;
                                 },
                                 set : function (show) {
                                    if (show) {
                                        if (_that.visible === false) {
                                            _parent.appendChild(_main_frame.getHtmlElement());
                                        }
                                    } else {
                                        if (_that.visible === true) {
                                            _parent.removeChild(_main_frame.getHtmlElement());
                                        }
                                    }
                                 },
                                 enumerable : true
                                 });
        Object.defineProperty(this,
                              "content",
                                {get : function () {
                                    return _client_area.getHtmlElement();
                                 },
                                 enumerable : true
                                 });
        Object.defineProperty(this,
                              "title",
                                {get : function () {
                                    return _title_bar.title;
                                 },
                                 set : function (new_title) {
                                    _title_bar.title = new_title;
                                 },
                                 enumerable : true
                                });
        Object.defineProperty(this,
                               "on_closed",
                               {value : null,
                                writable : true,
                                enumerable : true,
                                configurable : true});
                                
        _title_bar.on_closing = function () {
            _that.dispose();
        };
        _title_bar.on_drag = function (delta_x, delta_y) {
            var elem = _main_frame.getHtmlElement();
            elem.style.left = (parseInt(elem.style.left) + delta_x) + "px";
            elem.style.top = (parseInt(elem.style.top) + delta_y) + "px";
        };
        _sizer.on_resizing = function (cuadrant, delta_x, delta_y) {
            var elem = _main_frame.getHtmlElement();
            switch (cuadrant) {
            case 0:
                elem.style.left = (parseInt(elem.style.left) + delta_x) + "px";
                elem.style.top = (parseInt(elem.style.top) + delta_y) + "px";
                elem.style.width = (parseInt(elem.style.width) - delta_x) + "px";
                elem.style.height = (parseInt(elem.style.height) - delta_y) + "px";
                break;
            case 1:
                elem.style.top = (parseInt(elem.style.top) + delta_y) + "px";
                elem.style.height = (parseInt(elem.style.height) - delta_y) + "px";
                break;
            case 2:
                elem.style.top = (parseInt(elem.style.top) + delta_y) + "px";
                elem.style.width = (parseInt(elem.style.width) + delta_x) + "px";
                elem.style.height = (parseInt(elem.style.height) - delta_y) + "px";
                break;
            case 3:
                elem.style.left = (parseInt(elem.style.left) + delta_x) + "px";
                elem.style.width = (parseInt(elem.style.width) - delta_x) + "px";
                break;
            case 4:
                elem.style.width = (parseInt(elem.style.width) + delta_x) + "px";
                break;
            case 5:
                elem.style.left = (parseInt(elem.style.left) + delta_x) + "px";
                elem.style.width = (parseInt(elem.style.width) - delta_x) + "px";
                elem.style.height = (parseInt(elem.style.height) + delta_y) + "px";
                break;
            case 6:
                elem.style.height = (parseInt(elem.style.height) + delta_y) + "px";
                break;
            case 7:
                elem.style.width = (parseInt(elem.style.width) + delta_x) + "px";
                elem.style.height = (parseInt(elem.style.height) + delta_y) + "px";
                break;
            }
        };
    };

    return Window;
});
