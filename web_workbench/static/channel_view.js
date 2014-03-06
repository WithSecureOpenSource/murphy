/*jslint indent: 4, maxerr: 50, browser: true */
"use strict";

function ChannelView(channel_id) {
    var _channel = channel_id,
        _window = null,
        _receiving = false,
        _aspect_ratio_set = false,
        _refresh_every_ms = 1000;
    
    this.show = function() {
        require(["scripts/window"], function(Window) {
            _window = new Window();
            var content_panel = document.createElement("img"),
                imgObject = new Image();
                
            _window.content.appendChild(content_panel);
            _window.title = "Live content";

            var width = parseInt(getWidth(document.body) * 0.25),
                height = parseInt(getHeight(document.body) * 0.35),
                left = (getWidth(document.body) - width) - 1,
                top = (getHeight(document.body) - height) / 2;
            
            _window.setRect(left, 1, width, height);
            _window.on_closed = function () {
                _receiving = false;
                _window = null;
            };
            _receiving = true;
            
            imgObject.onload = function () {
                if (_receiving) {
                    content_panel.src = imgObject.src;
                    //sanity check we received an image that looks like a screenshot, not a blank one
                    if (_aspect_ratio_set === false && imgObject.width > 100) {
                        var aspect_ratio = imgObject.width / imgObject.height;
                        _window.setRect(left, 1, width, parseInt(width / aspect_ratio));
                        _aspect_ratio_set = true;
                    }
                    setTimeout(refresh, _refresh_every_ms);
                }
            };
            imgObject.onerror = function () {
                console.log("Error receiving image in channel...");
                refresh();
            };
            
            var refresh = function () {
                imgObject.src = "/channel?model=" + _channel + "&foo=" + new Date().getTime();
            };
            
            setTimeout(refresh, _refresh_every_ms);
        });
    };
    
    this.dispose = function () {
        if (_window != null) {
            _receiving = false;
            _window.dispose();
            _window = null;
        }
    };
};
