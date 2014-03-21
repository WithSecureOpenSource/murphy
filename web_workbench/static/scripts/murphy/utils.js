/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document, escape, unescape, window*/

define(function () {
    "use strict";
    var removeChilds,
        getComputedWidth,
        getComputedHeight,
        getOffset,
        clearSelect,
        loadSelectWithArray,
        setCookie,
        getCookie,
        QueryString;

    removeChilds = function (elem) {
        while (elem.hasChildNodes()) {
            elem.removeChild(elem.lastChild);
        }
    };

    getComputedWidth = function (element) {
        return parseInt(document.defaultView.getComputedStyle(element).getPropertyValue("width"), 10);
    };

    getComputedHeight = function (element) {
        return parseInt(document.defaultView.getComputedStyle(element).getPropertyValue("height"), 10);
    };

    getOffset = function (elem) {
        var x = 0, y = 0;
        while (elem && !isNaN(elem.offsetLeft) && !isNaN(elem.offsetTop)) {
            x += elem.offsetLeft - elem.scrollLeft;
            y += elem.offsetTop - elem.scrollTop;
            elem = elem.offsetParent;
        }
        return {top: y, left: x};
    };
    
    clearSelect = function (select_elem) {
        while (select_elem.length > 0) {
            select_elem.remove(0);
        }
    };

    loadSelectWithArray = function (select_elem, elements, add_empty_option) {
        var option, i;
        clearSelect(select_elem);
        if (add_empty_option) {
            option = document.createElement("option");
            option.text = "";
            select_elem.add(option);
        }
        for (i = 0; i < elements.length; i += 1) {
            option = document.createElement("option");
            option.text = elements[i];
            select_elem.add(option);
        }
    };

    setCookie = function (c_name, value, exdays) {
        var exdate = new Date(),
            c_value;
        exdate.setDate(exdate.getDate() + exdays);
        c_value = escape(value) + ((exdays === null) ? "" : "; expires=" + exdate.toUTCString());
        document.cookie = c_name + "=" + c_value;
    };

    getCookie = function (c_name) {
        var i,
            x,
            y,
            ARRcookies = document.cookie.split(";");
        for (i = 0; i < ARRcookies.length; i += 1) {
            x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
            y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
            x = x.replace(/^\s+|\s+$/g, "");
            if (x === c_name) {
                return unescape(y);
            }
        }
    };

    QueryString = function () {
        // This function is anonymous, is executed immediately and
        // the return value is assigned to QueryString!
        var query_string = {},
            query = window.location.search.substring(1),
            vars = query.split("&"),
            arr,
            pair,
            i;

        for (i = 0; i < vars.length; i += 1) {
            pair = vars[i].split("=");
            // If first entry with this name
            if (query_string[pair[0]] === undefined) {
                query_string[pair[0]] = pair[1];
                // If second entry with this name
            } else if (typeof query_string[pair[0]] === "string") {
                arr = [query_string[pair[0]], pair[1]];
                query_string[pair[0]] = arr;
                // If third or later entry with this name
            } else {
                query_string[pair[0]].push(pair[1]);
            }
        }
        return query_string;
    };

    return {
        removeChilds: removeChilds,
        getComputedWidth: getComputedWidth,
        getComputedHeight: getComputedHeight,
        getOffset: getOffset,
        clearSelect: clearSelect,
        loadSelectWithArray: loadSelectWithArray,
        setCookie: setCookie,
        getCookie: getCookie,
        QueryString: QueryString
    };
});
