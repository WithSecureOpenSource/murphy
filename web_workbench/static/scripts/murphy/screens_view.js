/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document*/

define(["scripts/murphy/utils.js"], function (utils) {
    "use strict";
    var ScreensView = function (container_element) {
        var container;

        container = container_element;

        this.clear = function () {
            utils.removeChilds(container);
        };

        this.draw = function (svg_doc) {
            var nodes, node, node_index, images, i, image, source, full_image;

            this.clear();

            node = document.importNode(svg_doc.documentElement, true);
            nodes = node.getElementsByClassName("node");

            for (node_index = 1; node_index < nodes.length; node_index += 1) {
                images = nodes[node_index].getElementsByTagName("image");
                for (i = 0; i < images.length; i += 1) {
                    image = images[i];
                    source = image.href.baseVal;
                    if (source.indexOf('/turtle.gif') === -1 && source.indexOf('data:image/gif;') === -1) {
                        full_image = document.createElement("img");
                        full_image.src = source;
                        full_image.style.padding = '5px';
                        container.appendChild(full_image);
                    }
                }
            }
        };
    };
    return {ScreensView: ScreensView};
});

