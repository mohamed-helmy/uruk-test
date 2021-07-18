odoo.define('ejaf_pos_partial_payment_multi_currency.models', function (require) {
var core = require('web.core');
var utils = require('web.utils');
var models = require('point_of_sale.models');
var PosBaseWidget = require('point_of_sale.BaseWidget');
var _t = core._t;

var round_di = utils.round_decimals;
var round_pr = utils.round_precision;


models.load_fields("pos.payment.method", "currency_id");

models.load_models({
    model: 'res.currency',
    fields: ['name','symbol','position','rounding','rate'],
    loaded: function (self, currencies) {
        self.multi_currencies = currencies;
    }
});

var _super_Order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function () {
        _super_Order.initialize.apply(this, arguments);
        this.currency = this.currency || this.pos.currency;
        this.amount_return_currency = this.amount_return_currency || this.pos.currency;
    },
    init_from_JSON: function (json) {
        _super_Order.init_from_JSON.apply(this, arguments);
        this.currency = json.currency;
        this.amount_return_currency = json.amount_return_currency;
    },
    export_as_JSON: function () {
        var values = _super_Order.export_as_JSON.apply(this, arguments);
        values.currency = this.currency;
        values.amount_return_currency = this.amount_return_currency;
        return values;
    },
    set_currency: function (currency) {
//        if (this.currency.id === currency.id) {
//            return;
//        }
//        var from_currency = this.currency || this.pos.currency;
//        var to_currency = currency;
//        this.orderlines.each(function (line) {
//            line.set_currency_price(from_currency, to_currency);
//            line.trigger('change',line);
//        });
//        this.currency = currency;
//        this.trigger('change');
//
//        // trigger change to update currency symbol in lines
//        this.orderlines.each(function (line) {
//            line.trigger('change',line);
//        });

        // set the amount return currency
        this.set_amount_return_currency(currency);

    },
    set_amount_return_currency: function (currency) {
        if (this.amount_return_currency.id === currency.id) {
            return;
        }
        var from_currency = this.amount_return_currency || this.pos.currency;
        var to_currency = currency;
        this.amount_return_currency = currency;
        this.trigger('change');
    },
    get_currency: function (){
        return this.currency;
    },
    get_amount_return_currency: function (){
        return this.amount_return_currency;
    },
    add_paymentline: function (payment_method) {
        var paymentlines = this.get_paymentlines();
        var is_multi_currency = false;
        _.each(paymentlines, function (line) {

            if (line.payment_method.currency_id[0] !== payment_method.currency_id[0]) {
                is_multi_currency = true;
            }
        });
//        if (is_multi_currency) {
//            this.pos.gui.show_popup('alert', {
//                title : _t("Payment Error"),
//                body  : _t("Payment of order should be in same currency. Payment could not be done with two different currency"),
//            });
//        } else {
            var journal_currency_id = payment_method.currency_id[0] || this.pos.currency.id;
            if (this.currency.id !== journal_currency_id) {
                var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
                if (currency){
                    this.set_currency(currency);
                }
            }
            _super_Order.add_paymentline.apply(this, arguments);
//        }
    },
    remove_paymentline: function(line){
        _super_Order.remove_paymentline.apply(this, arguments);
        var lines = this.paymentlines.models;
        var empty = [];
        for ( var i = 0; i < lines.length; i++) {
            empty.push(lines[i]);
        }
        if (! empty.length) {
            this.set_currency(this.pos.currency);
        }
        this.trigger('change');
    },
    convert_currency: function (from_currency, to_currency, amount){
        var conversion_rate =  to_currency.rate / from_currency.rate;
        return amount * conversion_rate;
    },
//    get_change_currency: function(paymentline) {
//        var change = this.get_change(paymentline);
//        if (paymentline) {
//            var journal_currency_id = paymentline.payment_method.currency_id[0] || this.pos.currency.id;
//            if (this.currency.id !== journal_currency_id) {
//                var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
//                if (currency){
//                    change = this.convert_currency(this.currency, currency, change)
//                }
//            }
//        }
//        return change;
//    },
    get_due_currency: function(paymentline) {
        var due = this.get_due(paymentline);
        if (paymentline) {
            var journal_currency_id = paymentline.payment_method.currency_id[0] || this.pos.currency.id;
            if (this.currency.id !== journal_currency_id) {
                var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
                if (currency){
                    due = this.convert_currency(this.currency, currency, due)
                }
            }
        }
        return due;
    },

    get_due: function(paymentline) {
        if (!paymentline) {
            var due = this.get_total_with_tax() - this.get_total_paid();
        } else {
            var due = this.get_total_with_tax();
            var lines = this.paymentlines.models;
            for (var i = 0; i < lines.length; i++) {
                if (lines[i] === paymentline) {
                    break;
                } else {
                    var payment_amount = lines[i].get_amount();
                    var journal_currency_id = lines[i].payment_method.currency_id[0] || lines[i].pos.currency.id;
                    if (lines[i].order.currency.id !== journal_currency_id) {
                        var currency = _.findWhere(lines[i].pos.multi_currencies, {id:journal_currency_id})
                        if (currency){
                            payment_amount = lines[i].order.convert_currency(currency, lines[i].order.currency, payment_amount)
                        }
                    }

                    due -= payment_amount;
                }
            }
        }
        return round_pr(due, this.pos.currency.rounding);
    },

    get_total_paid: function() {
        return round_pr(this.paymentlines.reduce((function(sum, paymentLine) {
            var payment_amount = paymentLine.get_amount();
            var journal_currency_id = paymentLine.payment_method.currency_id[0] || paymentLine.pos.currency.id;
            if (paymentLine.order.currency.id !== journal_currency_id) {
                var currency = _.findWhere(paymentLine.pos.multi_currencies, {id:journal_currency_id})
                if (currency){
                    payment_amount = paymentLine.order.convert_currency(currency, paymentLine.order.currency, payment_amount)
                }
            }

            if (paymentLine.get_payment_status()) {
                if (paymentLine.get_payment_status() == 'done') {
                    sum += payment_amount;
                }
            } else {
                sum += payment_amount;
            }
            return sum;
        }), 0), this.pos.currency.rounding);
    },

    get_change_value: function(paymentline) {
        if (!paymentline) {
//            var change = this.get_total_paid() - this.get_total_with_tax();
            var change = 0.0;
            var lines  = this.paymentlines.models;
            for (var i = 0; i < lines.length; i++) {
                if (i == (lines.length - 1)) {
                    var payment_amount = lines[i].get_amount();
                    change += payment_amount - lines[i].order.get_due_currency(lines[i]);

                    if (this.amount_return_currency.id != lines[i].payment_method.currency_id[0]) {
                        var currency = _.findWhere(this.pos.multi_currencies, {id:lines[i].payment_method.currency_id[0]})
                        if (currency){
                            change = this.convert_currency(currency, this.amount_return_currency, change);
                        }
                    }
                }
            }
        } else {
            var change = 0.0;
            var lines  = this.paymentlines.models;
            for (var i = 0; i < lines.length; i++) {
                var payment_amount = lines[i].get_amount();

                if (lines[i] === paymentline) {
                    change += payment_amount - lines[i].order.get_due_currency(lines[i]);

                    if (this.amount_return_currency.id != lines[i].payment_method.currency_id[0]) {
                        var currency = _.findWhere(this.pos.multi_currencies, {id:lines[i].payment_method.currency_id[0]})
                        if (currency){
                            change = this.convert_currency(currency, this.amount_return_currency, change);
                        }
                    }
                    break;
                }
            }
        }
        return round_pr(change, this.pos.currency.rounding)
    },


});

models.Orderline = models.Orderline.extend({
    set_currency_price: function (from_currency, to_currency){
        var conversion_rate =  to_currency.rate / from_currency.rate;
        this.price = this.price * conversion_rate;
    },
});


PosBaseWidget.include({
    format_currency: function (amount,precision){
        var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
        amount = this.format_currency_no_symbol(amount, precision);
        currency = (!this.product_list && this.pos.get_order().currency) || currency;
        if (currency.position === 'after') {
            return amount + ' ' + (currency.symbol || '');
        } else {
            return (currency.symbol || '') + ' ' + amount;
        }
    },

    format_return_currency: function (amount, precision){
        var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
        amount = this.format_currency_no_symbol(amount, precision);
        currency = (!this.product_list && this.pos.get_order().amount_return_currency) || (!this.product_list && this.pos.get_order().currency) || currency;

//        from_currency = (!this.product_list && this.pos.get_order().currency) || currency
//        to_currency = (!this.product_list && this.pos.get_order().amount_return_currency)
//
//        if (from_currency && to_currency) {
//            amount = this.pos.get_order().convert_currency(from_currency, to_currency, amount);
//            amount = this.format_currency_no_symbol(amount, precision);
//        }

        if (currency.position === 'after') {
            return amount + ' ' + (currency.symbol || '');
        } else {
            return (currency.symbol || '') + ' ' + amount;
        }
    },
});

var _super_Paymentline = models.Paymentline.prototype;
models.Paymentline = models.Paymentline.extend({

    export_as_JSON: function(){
        var values = _super_Paymentline.export_as_JSON.apply(this, arguments);
        values.amount = this.amount
        return values
    },
    set_amount: function(value){
        if((this.payment_method && !this.payment_method.is_cash_count) || this.pos.config.iface_precompute_cash){
            var journal_currency_id = this.payment_method.currency_id[0] || this.pos.currency.id;
            if (this.order.currency.id !== journal_currency_id) {
                var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
                if (currency){
                    value = this.order.convert_currency(currency, this.order.currency, value)
                }
            }
        }

        this.order.assert_editable();
        this.amount = round_di(parseFloat(value) || 0, this.pos.currency.decimals);
        this.pos.send_current_order_to_customer_facing_display();
        this.trigger('change',this);
    },

    // returns the amount of money on this paymentline
//    get_amount: function(){
//        var amount = this.amount;
//        var journal_currency_id = this.payment_method.currency_id[0] || this.pos.currency.id;
//        if (this.order.currency.id !== journal_currency_id) {
//            var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
//            if (currency){
//                amount = this.order.convert_currency(currency, this.order.currency, amount)
//            }
//        }
//        return amount;
//    },
    get_amount_currency: function(){
        return this.amount;
    },
    get_amount_str: function(){
        var journal_currency_id = this.payment_method.currency_id[0] || this.pos.currency.id;
        if (this.order.currency.id !== journal_currency_id) {
            var currency = _.findWhere(this.pos.multi_currencies, {id:journal_currency_id})
            if (currency){
                return field_utils.format.float(this.get_amount(), {digits: [69, currency.decimals]});
            }
        }
        return field_utils.format.float(this.get_amount(), {digits: [69, this.pos.currency.decimals]});
    },

});


});
