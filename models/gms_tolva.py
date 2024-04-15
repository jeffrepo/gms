from odoo import models, fields

class Tolva(models.Model):
    _name = 'gms.tolva'
    _description = 'Modelo para las tolvas'

    name = fields.Char(string='Tolva')
    descripcion = fields.Text(string='Descripción')