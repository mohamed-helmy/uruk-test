from odoo import api, fields, models


class PartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    swift = fields.Char(string="Swift",  readonly=False)
    iban_no = fields.Char(string="IBAN NO",  readonly=False)

