/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, require, Image, document, setTimeout, console*/

define(["scripts/murphy/utils.js"], function (utils) {
    "use strict";
    var ChannelView = function (channel_id, on_transmission_finished) {
        var _channel = channel_id,
            _transmission_finished = on_transmission_finished,
            _window = null,
            _receiving = false,
            _aspect_ratio_set = false,
            _refresh_every_ms = 1000;

        this.show = function () {
            require(["scripts/window"], function (Window) {
                _window = new Window();
                var content_panel = document.createElement("img"),
                    imgObject = new Image(),
                    refresh = function () {
                        imgObject.src = "/channel?model=" + _channel + "&foo=" + new Date().getTime();
                    },
                    width = Math.round(utils.getComputedWidth(document.body) * 0.25),
                    height = Math.round(utils.getComputedHeight(document.body) * 0.35),
                    left = Math.round((utils.getComputedWidth(document.body) - width) - 1),
                    top = Math.round((utils.getComputedHeight(document.body) - height) / 2);

                _window.content.appendChild(content_panel);
                _window.title = '<a href="vnc://192.168.56.1:5900" style="color: rgb(255,255,255)">Live content</a>';

                _window.setRect(left, 1, width, height);
                _window.on_closed = function () {
                    _receiving = false;
                    _window = null;
                };
                _receiving = true;

                imgObject.addEventListener("load", function () {
                    if (_receiving) {
                        //EOT signal?
                        if (imgObject.width === 1 && imgObject.height === 1) {
                            if (_transmission_finished) {
                                _transmission_finished();
                            }
                            return;
                        }
                        content_panel.src = imgObject.src;
                        //sanity check we received an image that looks like a screenshot, not a blank one
                        //FIXME: reshape window when aspect ration changes
                        if (_aspect_ratio_set === false && imgObject.width > 100) {
                            var aspect_ratio = imgObject.width / imgObject.height;
                            _window.setRect(left, 1, width, Math.round(width / aspect_ratio));
                            _aspect_ratio_set = true;
                        }
                        setTimeout(refresh, _refresh_every_ms);
                    }
                });
                imgObject.addEventListener("error", function () {
                    //we dont want to popup errors for this if/when it happens
                    if (console) {
                        console.log("Error receiving image in channel...");
                    }
                    refresh();
                });

                setTimeout(refresh, _refresh_every_ms);
            });
        };

        this.dispose = function () {
            if (_window !== null) {
                _receiving = false;
                _window.dispose();
                _window = null;
            }
        };
    };
    return {ChannelView: ChannelView};
});
