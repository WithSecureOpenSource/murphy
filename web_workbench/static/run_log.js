/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function RunLog (run_identifier) {
    var run_id = run_identifier;
    var text = "";
    var remote_machine_alive = null;
    var ajax_failed = false;
    
    this.reload = function(callback) {
        fetchAjax('/murphy/get_run_log?id=' + run_id,
            function(ajax) {
                if (ajax.status!=200) {
                    ajax_failed = true;
                }
                text = ajax.responseText;
                callback();
            });
    };
    
    this.get_text = function() {
        return text;
    };

    this.get_time_of_run = function() {
        var match=text.match(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/);
        if (match !== null)
            return match[0];
        else
            return null;
    };
    
    this.get_vnc = function() {
        var match=text.match("Vnc at (.*):(.*)");
        if (match !== null && match.length == 3)
            return {ip: match[1], port: match[2]};
        else
            return null;
    };

    this.get_ip = function() {
        var match=text.match("Machine ip is (.*)");
        if (match !== null && match.length == 2)
            return match[1];
        else
            return null;
    };
    
    this.get_remote_machine_id = function() {
        var match=text.match("Machine id is (.*)");
        if (match !== null && match.length == 2)
            return match[1];
        else
            return null;
    };

    this.finished = function() {
        var did_finished = text.search("Test Finished.") != -1;
        if (did_finished == true || ajax_failed == true) {
            return true;
        } else {
            return false;
        }
    };
    
    this.is_remote_machine_alive = function() {
        return remote_machine_alive;
    };

    this.set_remote_machine_alive = function(alive) {
        remote_machine_alive = alive;
    };
}
