from odoo import models, fields

class Camiones(models.Model):
    _name = 'gms.camiones'
    _description = 'Camiones'

    # Agrega los campos que necesites para el modelo 'gms.camiones'

    name = fields.Char(string='Nombre del camión')