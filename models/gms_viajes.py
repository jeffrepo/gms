from odoo import models, fields

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'

    name = fields.Char(string='Nombre del viaje')
    duracion_viaje = fields.Float(string='Duración del Viaje')
    gastos_combustible = fields.Float(string='Gastos de Combustible')
    gastos_peaje = fields.Float(string='Gastos de Peaje')
    observaciones = fields.Text(string='Observaciones')

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('proceso', 'Proceso'),
        ('liquidado', 'Liquidado'),
        ('cancelado', 'Cancelado'),
        ('terminado', 'Terminado')
    ], string='Estado', default='borrador', required=True)

    def action_confirm(self):
        self.write({'state': 'proceso'})

    def action_paid(self):
        self.write({'state': 'liquidado'})

    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_done(self):
        self.write({'state': 'terminado'})
