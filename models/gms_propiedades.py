from odoo import models, fields

class Propiedades(models.Model):
    _name = 'gms.propiedades'
    _description = 'Propiedades de Producto'

    name = fields.Char(string='Nombre')
    formula = fields.Text(string='Fórmula')
    producto_id = fields.Many2one('product.template', string='Producto')
    unidad_medida = fields.Many2one('uom.uom', string='Unidad de medida') # asumiendo que deseas una unidad de medida estándar
    propiedad = fields.Char(string='Propiedad')