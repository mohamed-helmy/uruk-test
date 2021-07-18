# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class DeliveryMethod(models.Model):
    _name = 'delivery.method'

    name = fields.Char(string="Name")
