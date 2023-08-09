from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean(string='Transportista')
    camiones_ids = fields.One2many('gms.camiones', 'transportista_id', string='Camiones')

