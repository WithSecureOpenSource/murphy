/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define*/

define(function () {
    "use strict";
    var EdgeLog = function (log_content) {
        var _content = log_content;

        this.hasDiskActivity = function () {
            return _content !== null && _content.instrumentation.WriteFile !== undefined;
        };

        this.hasNetworkActivity = function () {
            return _content !== null && _content.instrumentation['TCP Receive'] !== undefined;
        };

        this.hasRegistryActivity = function () {
            return _content !== null && _content.instrumentation.RegSetValue !== undefined;
        };

        this.hasActivity = function () {
            return _content !== null;
        };

        this.data = function () {
            return _content;
        };
    };
    return {EdgeLog: EdgeLog};
});
