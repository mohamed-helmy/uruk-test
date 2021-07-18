odoo.define('ejaf_product_details_barcode.ProductMenu', function (require) {
'use strict';

    var MainMenu = require('stock_barcode.MainMenu').MainMenu;

    MainMenu.include({
        events: _.extend({}, MainMenu.prototype.events, {
            "click .button_product": function(){
                this.open_product_details();
            },
        }),
        open_product_details: function() {
            var self = this;
            return this._rpc({
                model: 'stock.inventory',
                method: 'open_product_details',
            })
            .then(function(result) {
                self.do_action(result);
            });
        },
    });
});
