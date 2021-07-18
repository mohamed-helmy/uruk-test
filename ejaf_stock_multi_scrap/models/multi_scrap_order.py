# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MultiScrap(models.Model):
    _name = "stock.multi.scrap" 
    _description = "Multi Scrap"
    _order = 'id desc'
    _inherit = ['mail.thread']

    name = fields.Char(
        'Reference',  default=lambda self: _('New'),
        copy=False, readonly=True, required=True,
        states={'done': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, states={'done': [('readonly', True)]})

    def _get_default_scrap_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [company_id, False])], limit=1).id

    def _default_my_date(self):
        return fields.Date.context_today(self)
   
    scrap_location_id = fields.Many2one(
         'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True), ('company_id', 'in', [company_id, False])]", required=True,
        states={'done': [('readonly', True)]}, check_company=True)
   
    expected_date = fields.Date(string='Expected Date', default=_default_my_date)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Status', default="draft", readonly=True, tracking=True)

    scrap_ids = fields.One2many('stock.scrap', 'multi_scrap_id' , string = 'scraps')
    products_ids = fields.One2many('stock.multi.scrap.item' ,'multi_scrap_id',string="Scrap Item")
    analytic_tag_id = fields.Many2one(comodel_name="account.analytic.tag", string="Analytic Tag",
                                      states={'done': [('readonly', True)]})



    def _create_scrap_record(self , line):
        inv_obj = self.env['stock.scrap']
        scrap = inv_obj.create({
            'company_id': self.company_id.id,
            'product_id': line.product_id.id,
            'date_done': self.expected_date,
            'scrap_qty': line.scrap_qty,
            'product_uom_id' : line.product_uom_id.id,
            'multi_scrap_id' : self.id,
            'scrap_location_id' : self.scrap_location_id.id,
            'location_id' :  line.location_id.id,
            'lot_id' : line.lot_id.id,
            'origin' : self.name

        })
        return scrap


    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_('You cannot delete a multi scrap which is done.'))
        return super(MultiScrap, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.multi.scrap.sequence') or _('New')
        result = super(MultiScrap, self).create(vals)
        return result

    def action_create_order_scrap(self):
        for product in self.products_ids:
            scrap = self._create_scrap_record(product)
            scrap.do_scrap()
        self.state = 'done'
        return True


    def action_view_scrapes(self):
        action = self.env.ref('stock.action_stock_scrap')
        result = action.read()[0]
        result['domain'] = "[('id','in',%s)]" % (self.scrap_ids.ids)
        return result






