/*jslint indent: 4, maxerr: 50, browser: true */

/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function EdgeLog(log_content) {
    var _content = log_content;
    
    this.hasDiskActivity = function () {
        return _content !== null && 'WriteFile' in _content.instrumentation;
    };
    
    this.hasNetworkActivity = function () {
        return _content !== null && 'TCP Receive' in _content.instrumentation;
    };
    
    this.hasRegistryActivity = function () {
        return _content !== null && 'RegSetValue' in _content.instrumentation;
    };
    
    this.hasActivity = function () {
        return _content !== null;
    };
    
    this.data = function () {
        return _content;
    }
}
