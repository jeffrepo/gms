from odoo import models, fields

class Propiedades(models.Model):
    _name = 'gms.propiedades'
    _description = 'Propiedades de Producto'

    name = fields.Char(string='Nombre')
    formula = fields.Text(string='Fórmula')
    producto_id = fields.Many2one('product.template', string='Producto')
    umbral_tolerancia = fields.Float(string='Umbral de tolerancia')
    propiedad = fields.Char(string='Propiedad')