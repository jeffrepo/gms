from odoo import models, fields

class Rutas(models.Model):
    _name = 'gms.rutas'
    _description = 'Modelo de Rutas'

    name = fields.Char(string='Nombre de la Ruta', required=True)
    # Agrega más campos según tus necesidades

    # Agrega métodos adicionales según tus necesidades
