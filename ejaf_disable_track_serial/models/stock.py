# -*- coding: utf-8 -*-


import logging

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """
        Override Original method to disable tracking with serial in receipts and internal transfer
        """
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if not self.company_id.track_serial_sales_only or (self.company_id.track_serial_sales_only and picking_type.code == 'outgoing'):

                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)
                else:
                    if product and product.tracking == 'lot':
                        if not line.lot_name and not line.lot_id:
                            raise UserError(
                                _('You need to supply a Lot/Serial number for product %s.') % product.display_name)
        # Propose to use the sms mechanism the first time a delivery
        # picking is validated. Whatever the user's decision (use it or not),
        # the method button_validate is called again (except if it's cancel),
        # so the checks are made twice in that case, but the flow is not broken
        sms_confirmation = self._check_sms_confirmation_popup()
        if sms_confirmation:
            return sms_confirmation

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        for move in self.move_lines:
            move.partner_id = self.partner_id.id if self.partner_id else False
        return


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _action_done(self):
        """
        Override Original method to disable tracking with serial in receipts and internal transfer`
        """
        Quant = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_to_delete = self.env['stock.move.line']
        for ml in self:
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision \
                                  defined on the unit of measure "%s". Please change the quantity done or the \
                                  rounding precision of your unit of measure.') % (ml.product_id.display_name, ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                # if option of enable in sales only not active or delivery order track normally serial
                if not ml.company_id.track_serial_sales_only or (ml.company_id.track_serial_sales_only and ml.move_id.picking_type_id.code == 'outgoing'):

                    if ml.product_id.tracking != 'none':
                        picking_type_id = ml.move_id.picking_type_id
                        if picking_type_id:
                            if picking_type_id.use_create_lots:
                                # If a picking type is linked, we may have to create a production lot on
                                # the fly before assigning it to the move line if the user checked both
                                # `use_create_lots` and `use_existing_lots`.
                                if ml.lot_name and not ml.lot_id:
                                    lot = self.env['stock.production.lot'].create(
                                        {'name': ml.lot_name, 'product_id': ml.product_id.id, 'company_id': ml.move_id.company_id.id}
                                    )
                                    ml.write({'lot_id': lot.id})
                            elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                                # If the user disabled both `use_create_lots` and `use_existing_lots`
                                # checkboxes on the picking type, he's allowed to enter tracked
                                # products without a `lot_id`.
                                continue
                        elif ml.move_id.inventory_id:
                            # If an inventory adjustment is linked, the user is allowed to enter
                            # tracked products without a `lot_id`.
                            continue

                        if not ml.lot_id:
                            raise UserError(_('You need to supply a Lot/Serial number for product %s.') % ml.product_id.display_name)
                else:
                    if ml.product_id.tracking != 'none':
                        picking_type_id = ml.move_id.picking_type_id
                        if picking_type_id:
                            if picking_type_id.use_create_lots:
                                # If a picking type is linked, we may have to create a production lot on
                                # the fly before assigning it to the move line if the user checked both
                                # `use_create_lots` and `use_existing_lots`.
                                if ml.lot_name and not ml.lot_id:
                                    lot = self.env['stock.production.lot'].create(
                                        {'name': ml.lot_name, 'product_id': ml.product_id.id,
                                         'company_id': ml.move_id.company_id.id}
                                    )
                                    ml.write({'lot_id': lot.id})
                            elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                                # If the user disabled both `use_create_lots` and `use_existing_lots`
                                # checkboxes on the picking type, he's allowed to enter tracked
                                # products without a `lot_id`.
                                continue
                        elif ml.move_id.inventory_id:
                            # If an inventory adjustment is linked, the user is allowed to enter
                            # tracked products without a `lot_id`.
                            continue

                        if not ml.lot_id and ml.product_id.tracking == 'lot':
                            raise UserError(_(
                                'You need to supply a Lot/Serial number for product %s.') % ml.product_id.display_name)

            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            else:
                ml_to_delete |= ml
        ml_to_delete.unlink()

        (self - ml_to_delete)._check_company()

        # Now, we can actually move the quant.
        done_ml = self.env['stock.move.line']
        for ml in self - ml_to_delete:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml._should_bypass_reservation(ml.location_id) and float_compare(ml.qty_done, ml.product_qty, precision_rounding=rounding) > 0:
                    extra_qty = ml.qty_done - ml.product_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, ml_to_ignore=done_ml)
                # unreserve what's been reserved
                if not ml._should_bypass_reservation(ml.location_id) and ml.product_id.type == 'product' and ml.product_qty:
                    try:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    except UserError:
                        Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
            done_ml |= ml
        # Reset the reserved quantity as we just moved it to the destination location.
        (self - ml_to_delete).with_context(bypass_reservation_update=True).write({
            'product_uom_qty': 0.00,
            'date': fields.Datetime.now(),
        })
