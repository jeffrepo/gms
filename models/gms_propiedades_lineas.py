from odoo import models, fields

class PropiedadesLineas(models.Model):
    _name = 'gms.propiedades_lineas'
    _description = 'Líneas de Propiedades de Producto'

    propiedades_id = fields.Many2one('gms.propiedades', string='Propiedad')
    producto_id = fields.Many2one('product.template', string='Producto')
    valor = fields.Float(string='Valor')
    umbral_tolerancia = fields.Float(string='Umbral de tolerancia', tracking ="1")
    valor_extra = fields.Float(String = "Valor extra", tracking = "1")