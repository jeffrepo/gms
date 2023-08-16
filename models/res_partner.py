from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean(string='Transportista', tracking ="1")
    camiones_ids = fields.One2many('gms.camiones', 'transportista_id', string='Camiones', tracking ="1")

