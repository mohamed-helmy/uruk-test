odoo.define('ejaf_product_details_barcode.product_details_client_action', function (require) {
'use strict';

var core = require('web.core');
var ClientAction = require('stock_barcode.ClientAction');
var ViewsWidget = require('stock_barcode.ViewsWidget');

var _t = core._t;


ClientAction.include({
    _getState: function (recordId, state) {
        if (this.actionParams.model == 'product.product') {
            return
        } else {
            return this._super.apply(this, arguments);
        }
    },

    _save: function (params) {
        params = params || {};
        var self = this;

        // keep a reference to the currentGroup
        var currentPage = this.pages[this.currentPageIndex];
        if (! currentPage) {
            currentPage = {};
        }
        var currentLocationId = currentPage.location_id;
        var currentLocationDestId = currentPage.location_dest_id;


        // make a write with the current changes
        var recordId = this.actionParams.pickingId || this.actionParams.inventoryId;
        var applyChangesDef =  this._applyChanges(this._compareStates()).then(function (state) {
            if (state) {
                // Fixup virtual ids in `self.scanned_lines`
                var virtual_ids_to_fixup = _.filter(self._getLines(state[0]), function (line) {
                    return line.dummy_id;
                });
                _.each(virtual_ids_to_fixup, function (line) {
                    if (self.scannedLines.indexOf(line.dummy_id) !== -1) {
                        self.scannedLines = _.without(self.scannedLines, line.dummy_id);
                        self.scannedLines.push(line.id);
                    }
                });
            }
            return self._getState(recordId, state);
        }, function (error) {
            // on server error, let error be displayed and do nothing
            if (error !== undefined) {
                return Promise.reject();
            }
            if (params.forceReload) {
                return self._getState(recordId);
            } else {
                return Promise.resolve();
            }
        });

        return applyChangesDef.then(function () {
            self.pages = self._makePages();

            var newPageIndex = _.findIndex(self.pages, function (page) {
                return page.location_id === (params.new_location_id || currentLocationId) &&
                    (self.actionParams.model === 'stock.inventory' ||
                    page.location_dest_id === (params.new_location_dest_id || currentLocationDestId));
            }) || 0;
            if (newPageIndex === -1) {
                newPageIndex = 0;
            }
            self.currentPageIndex = newPageIndex;
        });
    },
});


var ProductDetailsClientAction = ClientAction.extend({

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.currentStep = 'productDetails';
        this.mode = 'productDetails';
        if (! this.actionParams.model) {
            this.actionParams.model = 'product.product';
        }
    },

    /**
     * @override
     */
    _makeNewLine: function (product, barcode, qty_done, package_id, result_package_id) {
        var virtualId = this._getNewVirtualId();
        var currentPage = this.pages[this.currentPageIndex];
        var newLine = {
            'product_id': {
                'id': product.id,
                'display_name': product.display_name,
                'price': product.list_price,
                'qty_available': product.qty_available,
                'currency_symbol': product.currency_symbol,
                'currency_symbol_before': product.currency_symbol_before,
                'currency_symbol_after': product.currency_symbol_after,
                'qty_per_location': product.qty_per_location,
                'barcode': barcode,
                'tracking': product.tracking,
            },
            'product_barcode': barcode,
            'display_name': product.display_name,
            'list_price': product.list_price,
            'qty_available': product.qty_available,
            'currency_symbol': product.currency_symbol,
            'currency_symbol_before': product.currency_symbol_before,
            'currency_symbol_after': product.currency_symbol_after,
            'qty_per_location': product.qty_per_location,
            'product_uom_id': product.uom_id,
            'reference': this.name,
            'virtual_id': virtualId,
        };
        return newLine;
    },

    /**
     * Handle what needs to be done when a product is scanned.
     *
     * @param {string} barcode scanned barcode
     * @param {Object} linesActions
     * @returns {Promise}
     */
    _step_productDetails: function (barcode, linesActions) {
        var self = this;
        this.currentStep = 'productDetails';
        var errorMessage;

        var product = this._isProduct(barcode);
        if (product) {
            var res = this._incrementLines({'product': product, 'barcode': barcode});
            if (this.actionParams.model === 'product.product') {
                linesActions.push([this.linesWidget.addProduct, [res.lineDescription, this.actionParams.model]]);
            }
            this.scannedLines.push(res.id || res.virtualId);
            return Promise.resolve({linesActions: linesActions});
        }
        else {
            var success = function (res) {
                return Promise.resolve({linesActions: res.linesActions});
            };
            var fail = function (specializedErrorMessage) {
                self.currentStep = 'productDetails';
                if (specializedErrorMessage){
                    return Promise.reject(specializedErrorMessage);
                }
                if (! self.scannedLines.length) {
                    errorMessage = _t('You are expected to scan one or more products.');
                    return Promise.reject(errorMessage);
                }
            };

            return fail('No product found with the barcode: ' + barcode)
        }
    },
});

core.action_registry.add('stock_barcode_product_details_client_action', ProductDetailsClientAction);

return ProductDetailsClientAction;

});