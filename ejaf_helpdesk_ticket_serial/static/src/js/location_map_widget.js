odoo.define('ejaf_helpdesk_ticket_serial.location_map_widget', function(require){

    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    var GoogleMapWidget = require('ejaf_helpdesk_ticket_serial.google_map_widget');
    var rpc = require('web.rpc');
    var location_map_widget = basic_fields.FieldChar.extend({
        init: function(parent, name, record, options){
            this._super.apply(this, arguments);
            this.lat = 0.0;
            this.lng = 0.0;
        },
        start: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.t = setInterval(function () {
                    if (typeof google != 'undefined') {
                        self.on_ready();
                    }
                }, 1000);///
            });
        },
        on_ready: function(){
            var self = this;

            if(self.t){
                clearInterval(self.t);
            }

            if (!self.$input) {
                return;
            }
            var gmap_widget = new GoogleMapWidget(self);
            gmap_widget.insertAfter(self.$input);
            rpc.query({
                model: 'stock.production.lot',
                method: 'init_map_location',
                args: [this.res_id]
            }).then(function(result){
                console.lo//g(result);
                gmap_widget.lat = result.lat;
                gmap_widget.lng = result.lng;
                gmap_widget.update_marker(result.lat,result.lng);
                self.update_place(result.lat,result.lng);
            });
            var autocomplete_address = new google.maps.places.Autocomplete((self.$input[0]), {types: ['geocode']});

            autocomplete_address.addListener('place_changed', function (){
                var place = autocomplete_address.getPlace();
                
                if(!place.geometry || !place.geometry.location){
                    return;
                }
                var location = place.geometry.location;
                self.lat = location.lat();
                self.lng = location.lng();
                // update gmap
                gmap_widget.update_marker(self.lat, self.lng);
            });

        },
        update_place: function (lat, lng) {
            var self = this;

            if (lat === this.lat && lng === this.lng) {
                return;
            }

            this.lat = lat;
            this.lng = lng;

            var geocoder = new google.maps.Geocoder;
            var latLng = new google.maps.LatLng(lat, lng);
            geocoder.geocode({'location': latLng}, function (results, status) {
                if (status === 'OK') {
                    if (self.$input) {
                        self.$input.val(results[0].formatted_address);
                        var changes ={
                            'serial_latitude':lat,
                            'serial_longitude':lng
                        };
                        self._onUpdateWidgetFields(changes);
                        self._doAction();
                    }
                }
            });
        },
        
         _onUpdateWidgetFields: function (changes) {
            changes = changes || {};
            this.trigger_up('field_changed', {
                dataPointID: this.dataPointID,
                changes: changes,
                viewType: this.viewType,
            });
        }

    });

    registry.add('location_map', location_map_widget);
});