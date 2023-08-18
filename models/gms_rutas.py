from odoo import models, fields

class GmsRutas(models.Model):
    _name = 'gms.rutas'
    _description = 'Modelo Rutas'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    follower_ids = fields.Many2many('res.users', string='Followers', tracking ="1")
    nombre_ruta = fields.Char(string='Nombre de la ruta', tracking ="1")
    direccion_origen = fields.Char(string='Dirección de origen', tracking ="1")
    direccion_destino = fields.Char(string='Dirección de destino', tracking ="1")
    kilometros = fields.Float(string='Kilómetros', tracking ="1")
