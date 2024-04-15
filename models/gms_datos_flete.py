from odoo import models, fields

class DatosFlete(models.Model):
    _name = 'gms.datos_flete'
    _description = 'Datos de Flete'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')
    flete_km = fields.Float(string='Flete kilometros')
    tarifa = fields.Float(string='Tarifa', digits=(16, 4))  #4 decimales
