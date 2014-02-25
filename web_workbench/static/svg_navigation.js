/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function getEventPoint(svg, evt) {
    var p = svg.createSVGPoint();
    //FIXME: hardcoded, doesnt work when the left toolbox is collapsed
    p.x = evt.clientX - 250;
    p.y = evt.clientY;

    return p;
}

function getGraphElement(svg) {
    return svg.getElementsByClassName("graph")[0];
}

function scaleToFit(svg, parent) {
    var desiredWidth = parseInt(parent.style.width);
    var desiredHeight = parseInt(parent.style.height);
    var graph1 = getGraphElement(svg);
    
    var scale = graph1.transform.baseVal.getItem('scale').matrix.a;
    var scale2 = 1.0;
    var scale3 = 1.0;
    if ((svg.width.baseVal.value * scale) > desiredWidth) {
        scale2 = desiredWidth / (svg.width.baseVal.value * scale);
        if ((svg.height.baseVal.value * scale * scale2) > desiredHeight) {
            scale3 = desiredHeight / (svg.height.baseVal.value * scale * scale2);
        }
    } else if ((svg.height.baseVal.value * scale)> desiredHeight) {
        scale2 = desiredHeight / (svg.height.baseVal.value * scale);
    }
    svg.width.baseVal.value *= (scale * scale2 * scale3);
    svg.height.baseVal.value *= (scale * scale2 * scale3);
    svg.viewBox.baseVal.width *= (scale * scale2 * scale3);
    svg.viewBox.baseVal.height *= (scale * scale2 * scale3);

    graph1.transform.baseVal.getItem('scale').matrix.a *= (scale * scale2 * scale3);
    graph1.transform.baseVal.getItem('scale').matrix.d *= (scale * scale2 * scale3);
}

function MouseWheelHandler(e) {
    // cross-browser wheel delta  
    var e = window.event || e; // old IE support  
    var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail))); 
    
    var svg = e.currentTarget;
    e.preventDefault();
    
    var new_val_prod = 0.9;
    var z_step = 1.1;
    if (delta > 0) {
        new_val_prod = 1.1;
        z_step = 0.9;
    }
    //FIXME: in our case this is safe... but not generic
    var graph1 = getGraphElement(svg);
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
    var dx = parseInt(svg.parentElement.scrollLeft) + parseInt(pt.x);
    dx = dx - (dx * new_val_prod);
    var dy = parseInt(svg.parentElement.scrollTop) + parseInt(pt.y);
    dy = dy - (dy * new_val_prod);
    
    svg.parentElement.scrollLeft -= dx;
    svg.parentElement.scrollTop -= dy;

    return false;

}