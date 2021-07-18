odoo.define('ejaf_product_details_barcode.LinesWidget', function (require) {
'use strict';

    var LinesWidget = require('stock_barcode.LinesWidget');

    LinesWidget.include({

        addProduct: function (lineDescription, model, doNotClearLineHighlight) {
            if (this.mode === 'productDetails') {
                var $body = this.$el.filter('.o_barcode_lines');
                $body.empty();
            }
            this._super.apply(this, arguments);
            if (this.mode === 'productDetails') {
                this._toggleScanMessage('scan_products');
            }
        },

        _renderLines: function () {
            this._super.apply(this, arguments);
            if (this.mode === 'productDetails') {
                this._toggleScanMessage('scan_products');
            }
        },

    });

});