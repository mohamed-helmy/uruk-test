# -*- coding: utf-8 -*-
import logging
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    lot_tag_id = fields.Many2one(comodel_name="lot.tag", string="Tag NO", copy=False)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", copy=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    serial_map_address = fields.Char('Map Address')
    serial_latitude = fields.Float()
    serial_longitude = fields.Float()
    product_id = fields.Many2one('product.product', 'Product', domain=[])

    def update_location(self, latitude=0.0, longitude=0.0, record=None):
        for rec in self:
            rec.write({
                'serial_latitude': latitude,
                'serial_longitude': longitude
            })

    def init_map_location(self):
        return {
            'lng': self.serial_latitude,
            'lat': self.serial_longitude
        }

    @api.constrains('lot_tag_id', 'product_id')
    def _check_lot_tag_id(self):
        if self.lot_tag_id:
            exist_tag = self.search([('id', '!=', self.id),
                         ('lot_tag_id', '=', self.lot_tag_id.id)])
            if exist_tag:
                raise ValidationError(_("Tag must be unique per product."))

    @api.model
    def create(self, vals):
        """
        override original method because it fills value of customer by default from context in picking
        but we want its value from first sale order only
        """
        vals['partner_id'] = False
        return super(StockProductionLot, self).create(vals)


class LotTag(models.Model):
    _name = 'lot.tag'
    _description = "Lot Tags"

    name = fields.Char(required=True)

    @api.constrains('name')
    def _check_name_unique(self):
        exist_tag = self.search([('id', '!=', self.id),
                     ('name', '=', self.name)])
        if exist_tag:
            raise ValidationError(_("Tag must be unique."))
