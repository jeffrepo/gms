from odoo import models, fields

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'

    # Agrega los campos que necesites para el modelo 'gms.viajes'

    name = fields.Char(string='Nombre del viaje')
    duracion_viaje = fields.Float(string='Duración del Viaje')
    gastos_combustible = fields.Float(string='Gastos de Combustible')
    gastos_peaje = fields.Float(string='Gastos de Peaje')
    observaciones = fields.Text(string='Observaciones')