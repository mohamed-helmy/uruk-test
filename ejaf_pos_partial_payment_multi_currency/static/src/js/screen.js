odoo.define('ejaf_pos_partial_payment_multi_currency.screen', function (require) {
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;

screens.PaymentScreenWidget.include({
    renderElement: function() {
        var self = this;
        this._super();
        var return_currency_buttons = this.render_return_currency_buttons();
        return_currency_buttons.appendTo(this.$('.return-currency-container'));
    },

    render_return_currency_buttons: function() {
        var self = this;
        var buttons = $(QWeb.render('ReturnPaymentCurrecy', { widget:this }));
            buttons.on('click','.js_return_currency_change',function(){
                var currency_id = $(this).data('currency')
                if (currency_id){
                    var currency = _.findWhere(self.pos.multi_currencies, {id: currency_id});
                    if (currency){
                        self.pos.get_order().set_amount_return_currency(currency);
                        // return currency buttons
                        self.$('.return-currency-container').empty();
                        self.renderElement();
                    }
                }
            });
        return buttons;
    },

    click_paymentmethods: function (id){
        this._super.apply(this, arguments);

        // currency buttons
        this.$('.currency-buttons').empty();
        var $currency_buttons = $(QWeb.render('PaymentCurrecy', {widget: this}));
        $currency_buttons.appendTo(this.$('.currency-buttons'));

        // return currency buttons
        this.$('.return-currency-container').empty();
        var return_currency_buttons = this.render_return_currency_buttons();
        return_currency_buttons.appendTo(this.$('.return-currency-container'));

        var payment_method = this.pos.payment_methods_by_id[id];
        if (payment_method.currency_id[0]) {
            var payment_method_currency = _.findWhere(this.pos.multi_currencies, {id:payment_method.currency_id[0]})
        } else {
            var payment_method_currency = false;
        }
        currency = payment_method_currency || this.pos.currency
        if (currency){
            this.pos.get_order().set_currency(currency);
        }
    },
});

screens.ReceiptScreenWidget.include({

    render_change: function() {
        this._super.apply(this, arguments);
        this.$('.change-value').html(this.format_return_currency(this.pos.get_order().get_change()));
    },

});

});
