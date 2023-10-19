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
    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra' , readonly=True)
    purchase_order_line_id = fields.Many2one('purchase.order.line', string='Línea de Orden de Compra', readonly=True)

    proveedor_id = fields.Many2one('res.partner', string='Proveedor', 
                                   domain=[('supplier_rank', '>', 0)], 
                                   help="Este es el proveedor del gasto.")
    # ver solo aquellos partners que tienen una clasificación de proveedor



    estado_compra = fields.Selection([
    ('comprado', 'Comprado'),
    ('no_comprado', 'No comprado'),
    ('no_aplica', 'No Aplica')
], string='Estado de compra', default='no_aplica', tracking="1")


