# -*- coding: utf-8 -*-

import logging

from odoo import api, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    def create_picking(self):
        try:
            res = super(PosOrderInherit, self).create_picking()
        except Exception as e:
            _logger.warning(str(e))
            res = super(PosOrderInherit, self.sudo()).create_picking()
        return res
