from odoo import models, fields

class Propiedades(models.Model):
    _name = 'gms.propiedades'
    _description = 'Propiedades de Producto'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    follower_ids = fields.Many2many('res.users', string='Followers')
    name = fields.Char(string='Nombre', tracking ="1")
    formula = fields.Text(string='Fórmula', tracking ="1")
    producto_id = fields.Many2one('product.template', string='Producto', tracking ="1")
    umbral_tolerancia = fields.Float(string='Umbral de tolerancia', tracking ="1")
    propiedad = fields.Char(string='Propiedad', tracking ="1")