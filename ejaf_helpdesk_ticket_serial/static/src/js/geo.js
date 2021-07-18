// create new widget with attrs calles widget == 'geo' 
// This To Capture Location and Write into stock.production.lot
odoo.define('ejaf_helpdesk_ticket_serial.geo', function (require) {
    "use strict";
    var form_widget = require('web.FormController');
    var rpc = require('web.rpc');
    form_widget.include({
        _onButtonClicked: function (event) {
            if (event.data.attrs.widget == "geo") {
                var data_id = this.getSelectedIds()[0];
                var record_id = event.data.record.data.id;
                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        // call function update_location
                        rpc.query({
                            model: 'stock.production.lot',
                            method: 'update_location',
                            args: [data_id, position.coords.latitude, position.coords.longitude, record_id]
                        });
                        location.reload();
                        return;
                    },
                    function (error) {
                        alert(error.message);
                    },
                    {
                        enableHighAccuracy: true
                        , timeout: 5000
                    }
                );
            }
            else {

                return this._super(event);
            }
        },
    });
});