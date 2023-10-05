from odoo import models, fields

class GmsPropiedadesLineas(models.Model):
    _name = 'gms.propiedades_lineas'

    umbral_tolerancia = fields.Float(string='Umbral de tolerancia')
    propiedades_id = fields.Many2one('gms.propiedades')
    producto_id =fields.Many2one("product.template", string= "Productos")