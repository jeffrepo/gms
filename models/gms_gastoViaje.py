from odoo import models, fields

class GastosViaje(models.Model):
    _name = 'gms.gasto_viaje'
    _description = 'Gastos de Viaje'

    name = fields.Char(string='Descripción', required=True)
    producto_id = fields.Many2one('product.product', string='Producto')
    precio_total = fields.Float(string='Precio Total')
    viaje_id = fields.Many2one('gms.viaje', string='Viaje')
