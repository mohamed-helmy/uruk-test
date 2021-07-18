from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_usool = fields.Boolean(string="Usool Company")
