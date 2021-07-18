odoo.define('ejaf_pos_partial_payment_multi_currency.partial_payment', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var Order = models.Order;
    var PaymentScreenWidget = require('point_of_sale.screens').PaymentScreenWidget


    /*--------------------------------------*\
     |           THE ORDER MODEL            |
    \*======================================*/

    var order_model_super = models.Order.prototype;
    models.Order = models.Order.extend({
        is_paid: function(){
            var _super = order_model_super.is_paid.bind(this)();
            if (! _super && this.pos.config && this.pos.get_order().is_to_invoice() && this.pos.config.allow_partial_payment && this.get_total_paid() >= 0) {
                return true;
            }
            return _super;
        }
    });

});
