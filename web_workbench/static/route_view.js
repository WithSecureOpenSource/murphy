/*jslint indent: 4, maxerr: 50, browser: true, devel: true */
'use strict';

/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function RouteView(container_element, on_click_function) {
    var container, on_click, removeTitles, removeMainTitle, fixEdgeTitles,
        get_click_function, addClickHandler;

    container = container_element;
    on_click = on_click_function;
    
    this.clear = function () {
        removeChilds(container);
    };
    
    this.draw = function (svg_doc, show_tooltips, enable_clicks) {
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
