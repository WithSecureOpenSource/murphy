/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function fix_nodes_links() {
    var nodes = document.getElementsByClassName('node');
    for (var i=0; i < nodes.length; i++) {
        var link = nodes[i].childNodes[2];
        var href = link.href.baseVal;
        var name = 'node_' + href.split("'")[1];
        nodes[i].setAttribute('name', name);
        link.href.baseVal = 'javascript:add_node(' + href + ');';
    }
}

function fix_arcs_links() {
    var edges = document.getElementsByClassName('edge');
    for (var i=0; i < edges.length; i++) {
        var link = edges[i].childNodes[2];
        var href = link.href.baseVal;
        var name = 'arc_' + href.split("'")[1];
        edges[i].setAttribute('name', name);
        link.href.baseVal = 'javascript:add_arc(' + href + ');';
        edges[i].childNodes[4].href.baseVal = link.href.baseVal;
    }
}

function getGraphNode(name)
{
    var elements = document.getElementsByName("node_" + name);
    if (elements.length > 0) {
        return elements[0];
    } else {
        //dunno why doesnt work in ff10 the getElementsByName in this case
        var nodes = document.getElementsByClassName('node');
        for (var i=0; i < nodes.length; i++) {
            if (nodes[i].getAttribute('name') == "node_" + name)
                return nodes[i];
        }
        return null;
    }
}

function getGraphEdge(node, edge)
{
    var elements = document.getElementsByName("arc_" + node + "." + edge);
    if (elements.length > 0) {
        return elements[0];
    } else {
        //dunno why doesnt work in ff10 the getElementsByName in this case
        var edges = document.getElementsByClassName('edge');
        for (var i=0; i < edges.length; i++) {
            if (edges[i].getAttribute('name') == ("arc_" + node + "." + edge))
                return edges[i];
        }
        return null;
    }
}

function adjust_map() {
    fix_nodes_links();
    fix_arcs_links();
}

function set_node_color(node, color) {
    node.setAttribute("fill", "white");
    node.childNodes[2].childNodes[1].setAttribute('fill', color);
}

function get_node_color(node) {
    return node.childNodes[2].childNodes[1].getAttribute('fill');
}

function set_edge_color(edge, color) {
    edge.setAttribute("fill", color);
    edge.childNodes[2].childNodes[1].setAttribute('stroke', color);
    edge.childNodes[2].childNodes[3].setAttribute('stroke', color);
    edge.childNodes[2].childNodes[3].setAttribute('fill', color);
}

function get_edge_color(edge) {
    return edge.childNodes[2].childNodes[1].getAttribute('stroke');
}


function getEventPoint(svg, evt) {
    var p = svg.createSVGPoint();

    p.x = evt.clientX - 250;
    p.y = evt.clientY;

    return p;
}

function MouseWheelHandler(e) {
    // cross-browser wheel delta  
    var e = window.event || e; // old IE support  
    var delta = Math.max(-1, Math.min(1, (e.wheelDelta || -e.detail))); 
    svg = document.getElementById('svg map');

    e.preventDefault();
    
    var new_val_prod = 0.9;
    var z_step = 1.1;
    if (delta > 0) {
        new_val_prod = 1.1;
        z_step = 0.9;
    }
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