from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean(string='Transportista')
    camiones_ids = fields.Many2many('gms.camiones', string='Camiones')

