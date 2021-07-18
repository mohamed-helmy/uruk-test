from odoo import api, fields, models, _


class Config(models.TransientModel):
    _name = 'google_map.config'
    # TODO -->  set google maps api key in system partametes ..
    # Key = google_map_api_key;
    @api.model
    def get_api_key(self):
        return self.env['ir.config_parameter'].sudo().get_param('google_map_api_key')