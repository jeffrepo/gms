from odoo import models, fields, api

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'

    name = fields.Char(string='Nombre del viaje')
    fecha_viaje = fields.Date(string='Fecha de viaje')

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
        
    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos')


    