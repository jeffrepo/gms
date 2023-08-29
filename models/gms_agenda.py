from odoo import models, fields, api
import random

class Agenda(models.Model):
    _name = 'gms.agenda'
    _description = 'Agenda'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name ="name"

    name = fields.Char(string="Booking", required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('gms.agenda'))
    fecha = fields.Date(string='Fecha', required=True, tracking="1")  
    fecha_viaje = fields.Date(string='Fecha de viaje', required=True, tracking="1")  
    origen = fields.Many2one('res.partner', string='Origen', required=True, tracking ="1")
    destino = fields.Many2one('res.partner', string='Destino', required=True, tracking ="1")
    transportista_id = fields.Many2one('res.partner', string='Trasportista', states={'cancelado': [('readonly', True)]}, tracking="1")  
    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Disponibilidad Camión', states={'cancelado': [('readonly', True)]}, tracking="1",  domain="[('estado', '=', 'disponible'), ('transportista_id', '=', transportista_id)]")
    #camion_id = fields.Many2one('gms.camiones', string='Camión', states={'cancelado': [('readonly', True)]}, tracking="1")
    #viaje_ids = fields.One2many('gms.viaje', 'agenda_id', string='Viajes')
  

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
    
    
    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_proceso(self):
        self.write({'state': 'proceso'})

    def action_view_scheduled_trips(self):
        action = self.env.ref('gms.action_view_scheduled_trips').read()[0]
        action['context'] = {
            'search_default_agenda_id': self.id,
        }
        return action

       
         # Actualiza el método action_confirm
    def action_confirm(self):
        if self.camion_disponible_id:
            self.camion_disponible_id.write({'estado': 'ocupado'})

        viaje = self.env['gms.viaje'].create({
            'name': self.name,
            'fecha_viaje': self.fecha_viaje,
            'origen': self.origen.id,
            'destino': self.destino.id,
            'camion_disponible_id': self.camion_disponible_id.id,
        })


        # Manda los datos a historial utilizando el camion_disponible_id
        if self.camion_disponible_id:
            self.env['gms.historial'].create({
                'fecha': self.fecha,
                'camion_id': self.camion_disponible_id.camion_id.id,
                'agenda_id': self.id,
        })

        

        self.write({'state': 'confirmado'})

        # Abre la vista de viajes agendados después de la confirmación
        action = self.env.ref('gms.action_view_scheduled_trips').read()[0]
        action['context'] = {
            'search_default_agenda_id': self.id,
        }
        return action

