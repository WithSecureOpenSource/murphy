/*jslint indent: 4, maxerr: 50, nomen: true */
/*global define, document, window */

define(function () {
    "use strict";
    return {

        Dragger : function (element, when_captured, when_drag, when_released) {
            var x = 0,
                y = 0,
                target_element = element,
                drag_approved = false,
                on_capture = when_captured,
                on_drag = when_drag,
                on_release = when_released,
                that_x = this,
                _virtual_x,
                _virtual_y,
                eventListener = function (e) { that_x.capture(e); };

            this.confinement_rect = null;
            element.addEventListener('mousedown', eventListener, false);

            this.capture = function (evt) {
                var evtobj = window.event ? window.event : evt;

                if (evtobj.target === target_element) {
                    drag_approved = true;
                    x = evtobj.clientX;
                    y = evtobj.clientY;

                    evtobj.preventDefault();

                    document.addEventListener('mousemove', that_x.move, false);
                    document.addEventListener('mouseup', that_x.release, false);
                    if (on_capture) {
                        on_capture(evtobj);
                    }
                    _virtual_x = evtobj.pageX;
                    _virtual_y = evtobj.pageY;
                }
            };

            this.move = function (evt) {
                var evtobj = window.event ? window.event : evt,
                    delta_x,
                    delta_y,
                    new_virtual_x,
                    new_virtual_y;

                if (drag_approved === true) {
                    delta_x = evtobj.clientX - x;
                    delta_y = evtobj.clientY - y;

                    if (that_x.confinement_rect) {
                        new_virtual_x = _virtual_x + delta_x;
                        new_virtual_y = _virtual_y + delta_y;
                        if (new_virtual_x < that_x.confinement_rect.left) {
                            if (_virtual_x > that_x.confinement_rect.left) {
                                delta_x = that_x.confinement_rect.left - _virtual_x;
                            } else {
                                delta_x = 0;
                            }
                        } else if (_virtual_x < that_x.confinement_rect.left && new_virtual_x > that_x.confinement_rect.left) {
                            //old pos outside
                            delta_x = new_virtual_x - that_x.confinement_rect.left;
                        } else if (_virtual_x > that_x.confinement_rect.right) {
                            delta_x = 0;
                        }
                        if (new_virtual_y < that_x.confinement_rect.top) {
                            if (_virtual_y > that_x.confinement_rect.top) {
                                delta_y = that_x.confinement_rect.top - _virtual_y;
                            } else {
                                delta_y = 0;
                            }
                        } else if (_virtual_y < that_x.confinement_rect.top && new_virtual_y > that_x.confinement_rect.top) {
                            //old pos outside
                            delta_y = new_virtual_y - that_x.confinement_rect.top;
                        } else if (_virtual_y > that_x.confinement_rect.bottom) {
                            delta_y = 0;
                        }
                        _virtual_x = new_virtual_x;
                        _virtual_y = new_virtual_y;
                    }
                    if (on_drag) {
                        on_drag(evtobj, target_element, delta_x, delta_y, that_x);
                    }
                    x = evtobj.clientX;
                    y = evtobj.clientY;
                    evtobj.preventDefault();
                    return false;
                }
            };

            this.dragInProgress = function () {
                return drag_approved;
            };

            this.release = function (evt) {
                drag_approved = false;
                document.removeEventListener('mousemove', that_x.move, false);
                document.removeEventListener('mouseup', that_x.release, false);
                if (on_release) {
                    on_release(evt);
                }
            };

            this.dispose = function () {
                target_element.removeEventListener('mousedown', eventListener, false);
            };
        }
    };
});
