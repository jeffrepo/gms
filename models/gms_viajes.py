from odoo import models, fields, api

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    follower_ids = fields.Many2many('res.users', string='Followers')

    
    name = fields.Char(string='Nombre del viaje', tracking ="1")
    fecha_viaje = fields.Date(string='Fecha de viaje', tracking ="1")
    origen = fields.Many2one('res.partner', string='Origen', required=True, tracking ="1")
    destino = fields.Many2one('res.partner', string='Destino', required=True, tracking ="1")

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('proceso', 'Proceso'),
        ('liquidado', 'Liquidado'),
        ('cancelado', 'Cancelado'),
        ('terminado', 'Terminado')
    ], string='Estado', default='borrador', required=True)

    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos')

  
    def action_confirm(self):
        self.write({'state': 'proceso'})

    def action_paid(self):
        self.write({'state': 'liquidado'})

    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_done(self):
        self.write({'state': 'terminado'})
    