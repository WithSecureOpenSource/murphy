/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document, window*/

define(function () {
    "use strict";
    var getEventPoint = function (svg, evt) {
            var p = svg.createSVGPoint();
            //FIXME: hardcoded, doesnt work when the left toolbox is collapsed
            p.x = evt.clientX - 250;
            p.y = evt.clientY;

            return p;
        },
        getGraphElement = function (svg) {
            return svg.getElementsByClassName("graph")[0];
        },
        scaleToFit = function (svg, parent) {
            var desiredWidth = parseInt(parent.style.width, 10),
                desiredHeight = parseInt(parent.style.height, 10),
                graph1 = getGraphElement(svg),
                scale = graph1.transform.baseVal.getItem('scale').matrix.a,
                scale2 = 1.0,
                scale3 = 1.0;

            if ((svg.width.baseVal.value * scale) > desiredWidth) {
                scale2 = desiredWidth / (svg.width.baseVal.value * scale);
                if ((svg.height.baseVal.value * scale * scale2) > desiredHeight) {
                    scale3 = desiredHeight / (svg.height.baseVal.value * scale * scale2);
                }
            } else if ((svg.height.baseVal.value * scale) > desiredHeight) {
                scale2 = desiredHeight / (svg.height.baseVal.value * scale);
            }
            svg.width.baseVal.value *= (scale * scale2 * scale3);
            svg.height.baseVal.value *= (scale * scale2 * scale3);
            svg.viewBox.baseVal.width *= (scale * scale2 * scale3);
            svg.viewBox.baseVal.height *= (scale * scale2 * scale3);

            graph1.transform.baseVal.getItem('scale').matrix.a *= (scale * scale2 * scale3);
            graph1.transform.baseVal.getItem('scale').matrix.d *= (scale * scale2 * scale3);
        },
        MouseWheelHandler = function (evt) {
            // cross-browser wheel delta
            var e = window.event || evt, // old IE support
                delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail))),
                svg = e.currentTarget,
                graph1 = getGraphElement(svg),
                new_val_prod = 0.9,
                z_step = 1.1,
                pt,
                dx,
                dy;

            e.preventDefault();

            if (delta > 0) {
                new_val_prod = 1.1;
                z_step = 0.9;
            }

            pt = getEventPoint(svg, e);

            svg.width.baseVal.value = svg.width.baseVal.value * new_val_prod;
            svg.height.baseVal.value = svg.height.baseVal.value * new_val_prod;
            svg.viewBox.baseVal.width = svg.viewBox.baseVal.width * new_val_prod;
            svg.viewBox.baseVal.height = svg.viewBox.baseVal.height * new_val_prod;
            graph1.transform.baseVal.getItem('scale').matrix.a *= new_val_prod;
            graph1.transform.baseVal.getItem('scale').matrix.d *= new_val_prod;
            //CHROME BUG, does not properly readjust width
            svg.style.width = svg.width.baseVal.value;

            /*
            var dx = parseInt(svg.parentElement.scrollLeft) + parseInt(pt.x) - parseInt(document.getElementById('left spacer').style.width);
            dx = dx - (dx * new_val_prod);
            var dy = parseInt(svg.parentElement.scrollTop) + parseInt(pt.y) - parseInt(document.getElementById('top spacer').style.height);
            dy = dy - (dy * new_val_prod);
            */
            dx = parseInt(svg.parentElement.scrollLeft, 10) + parseInt(pt.x, 10);
            dx = dx - (dx * new_val_prod);
            dy = parseInt(svg.parentElement.scrollTop, 10) + parseInt(pt.y, 10);
            dy = dy - (dy * new_val_prod);

            svg.parentElement.scrollLeft -= dx;
            svg.parentElement.scrollTop -= dy;

            return false;
        };

    return {
        getEventPoint: getEventPoint,
        getGraphElement: getGraphElement,
        scaleToFit: scaleToFit,
        MouseWheelHandler: MouseWheelHandler
    };
});
