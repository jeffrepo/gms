from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    umbral_tolerancia = fields.Float(string='Umbral de tolerancia', tracking ="1")
    propiedades_ids = fields.One2many('gms.propiedades_lineas', 'producto_id', tracking ="1")