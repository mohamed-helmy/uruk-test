// init_config and load places lib ..
odoo.define('ejaf_helpdesk_ticket_serial.init_config', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    //default key set default for testing only
    var default_key = 'AIzaSyAu47j0jBPU_4FmzkjA3xc_EKoOISrAJpI';
    rpc.query({
        model: 'google_map.config',
        method: 'get_api_key',
        args: []
    }).then(function (key) {
        
        if (!key) {
            // for testing ...
            key = default_key;
        }
        // Load Places Lib..
        $.getScript('http://maps.googleapis.com/maps/api/js?key=' + key + '&libraries=places');
    });
});