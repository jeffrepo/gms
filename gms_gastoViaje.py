from odoo import models, fields

class GastosViaje(models.Model):
    _name = 'gms.gasto_viaje'
    _description = 'Gastos de Viaje'
    #_inherit = ['mail.thread', 'mail.activity.mixin']


    #follower_ids = fields.Many2many('res.users', string='Followers')
    name = fields.Char(string='Descripción', required=True, tracking ="1")
    producto_id = fields.Many2one('product.product', string='Producto', tracking ="1")
    precio_total = fields.Float(string='Precio Total', tracking ="1")
    viaje_id = fields.Many2one('gms.viaje', string='Viaje', tracking ="1")

    estado_compra = fields.Selection([
    ('comprado', 'Comprado'),
    ('no_comprado', 'No comprado'),
    ('no_aplica', 'No Aplica')
], string='Estado de compra', default='no_aplica', tracking="1")


