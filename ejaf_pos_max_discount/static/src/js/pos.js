odoo.define('ejaf_pos_max_discount.pos', function (require) {
    var core    = require('web.core');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');

    var _t      = core._t;

    models.load_fields("res.users", "pos_max_discount");


    screens.OrderWidget.include({
        set_value: function (val) {

            var order = this.pos.get_order();
            var mode = this.numpad_state.get('mode');

            if (order.get_selected_orderline() && mode === 'discount') {
                 user_id= this.pos.user;

                 if (val > user_id.pos_max_discount){
                        this.gui.show_popup('error', {
                            title : _t("Discount Not Possible"),
                            body  : _t("You cannot apply discount above the discount limit."),
                        });
                        order.get_selected_orderline().set_discount(0);
                    }
                    else
                    {
                        order.get_selected_orderline().set_discount(val);
                    }
            } else {
                this._super(val);
            }
        },
    });

});


