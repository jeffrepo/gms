from odoo import models, fields

class DatosHumedad(models.Model):
    _name = 'gms.datos_humedad'
    _description = 'Datos de Humedad'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    humedad = fields.Float(string='Humedad')
    tarifa = fields.Float(string='Tarifa', digits=(16, 4)) 