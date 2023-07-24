from odoo import models, fields

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'

    # Agrega los campos que necesites para el modelo 'gms.viajes'

    name = fields.Char(string='Nombre del viaje')