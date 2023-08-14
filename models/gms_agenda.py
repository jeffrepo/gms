from odoo import models, fields, api
import random

class Agenda(models.Model):
    _name = 'gms.agenda'
    _description = 'Agenda'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Booking", required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('gms.agenda'))
    fecha = fields.Date(string='Fecha', required=True, tracking="1")  
    fecha_viaje = fields.Date(string='Fecha de viaje', required=True, tracking="1")  
    origen = fields.Char(string='Origen', required=True, tracking="1")  
    destino = fields.Char(string='Destino', required=True, tracking="1")  
    transportista_id = fields.Many2one('res.partner', string='Trasportista', states={'cancelado': [('readonly', True)]}, tracking="1")  
    camion_id = fields.Many2one('gms.camiones', string='Camión', states={'cancelado': [('readonly', True)]}, tracking="1")  

    state = fields.Selection([
        ('solicitud', 'Solicitud'),
        ('proceso', 'Proceso'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', default='solicitud', required=True)

    follower_ids = fields.Many2many('res.users', string='Followers')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('gms.agenda')
        return super().create(vals_list)
    
    def action_confirm(self):
        viaje = self.env['gms.viaje'].create({
            'name': self.name,
            'fecha_viaje': self.fecha_viaje,
            'origen': self.origen,
            'destino': self.destino,
        })
        self.write({'state': 'confirmado'})

    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_proceso(self):
        self.write({'state': 'proceso'})

   
       
        

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = record.camion_id.nombre if record.camion_id else ''  
            result.append((record.id, name))
        return result