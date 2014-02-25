/*jslint indent: 4, maxerr: 50, browser: true, devel: true */
'use strict';

/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/


function View(element, show_function, hide_function, tabbed_view_control) {
    var tab_element, show_fn, hide_fn, tab_control, that;
    
    tab_element = element;
    tab_control = tabbed_view_control;
    show_fn = show_function;
    hide_fn = hide_function;
    that = this;

    this.hide = function () {
        if (hide_fn !== undefined && hide_fn !== null) {
            hide_fn();
        }
        if (tab_element.classList.contains('selected-tab')) {
            tab_element.classList.remove('selected-tab');
        }
        if (tab_element.classList.contains('unselected-tab') === false) {
            tab_element.classList.add('unselected-tab');
        }
    };
    
    this.show = function () {
        if (tab_control.active_view !== null) {
            tab_control.active_view.hide();
            tab_control.active_view = null;
        }
        if (tab_element.classList.contains('unselected-tab')) {
            tab_element.classList.remove('unselected-tab');
        }
        if (tab_element.classList.contains('selected-tab') === false) {
            tab_element.classList.add('selected-tab');
        }
        show_fn();
        tab_control.active_view = that;
    };
    
    if (tab_element.classList.contains('unselected-tab') === false) {
        tab_element.classList.add('unselected-tab');
    }
    if (tab_element.classList.contains('selected-tab')) {
        tab_element.classList.remove('selected-tab');
    }
    tab_element.addEventListener('click', this.show, false);
}


function TabbedViewControl() {
    var views;
    views = [];
    this.active_view = null;
    
    this.addView = function (element, show_function, hide_function) {
        /*
            Defines a view inside a tab-controlled strip of views.
            element is the html element used as the tab header for selecting it
        */
        var view = new View(element, show_function, hide_function, this);
        views.push(view);
        return view;
    };
    
    this.getView = function (index) {
        return views[index];
    };
}
