from odoo import models, fields

class Propiedades(models.Model):
    _name = 'gms.propiedades'
    _description = 'Propiedades de Producto'

    name = fields.Char(string='Nombre')
    formula = fields.Text(string='Fórmula')