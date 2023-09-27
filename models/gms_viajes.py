from odoo import models, fields, api, _
import datetime

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    name = fields.Char(
    'Name', default=lambda self: _('New'),
    copy=False, readonly=True, tracking=True)

    agenda = fields.Many2one('gms.agenda', string='Agenda')
    fecha_viaje = fields.Date(string='Fecha de viaje', tracking="1")
    origen = fields.Many2one('res.partner', string='Origen', required=True, tracking="1")
    destino = fields.Many2one('res.partner', string='Destino', required=True, tracking="1")
    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Camión Disponible', tracking="1")
    camion_id = fields.Many2one('gms.camiones', string='Camiones')
    conductor_id = fields.Many2one('res.partner', string='Chofer')
    solicitante_id = fields.Many2one('res.partner', string='Solicitante')
    
    
    state = fields.Selection([
        ('cancelado', 'Cancelado'),
        ('borrador', 'Borrador'),
        ('coordinado', 'Coordinado'),
        ('proceso', 'Proceso'),
        ('terminado', 'Terminado'),
        ('liquidado', 'Liquidado')
    ], string='Estado', default='borrador', required=True)


    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos')


    def action_proceso(self):
        self.write({'state': 'proceso'})


    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_terminado(self):
        # Cambia el estado a 'terminado'
        self.write({'state': 'terminado'})

        # Guarda la fecha y hora actual
        fecha_hora_actual = fields.Datetime.now()

        # Busca el registro en gms.historial que tenga la misma agenda_id que el nombre del viaje
        historial = self.env['gms.historial'].search([('agenda_id.name', '=', self.name)], limit=1)

        if historial:
            # Actualiza la fecha_hora_liberacion en el registro existente
            historial.write({'fecha_hora_liberacion': fecha_hora_actual})

        # Recupera el camión asociado a este viaje (si existe)
        camion_id = self.camion_disponible_id.camion_id.id if self.camion_disponible_id else False

         # Actualiza el estado del camión a 'disponible' si existe
        self.camion_disponible_id.estado = "disponible"
        self.camion_disponible_id.fecha_hora_liberacion = fecha_hora_actual
        # if camion_id:
        #     camion_disponible = self.env['gms.camiones.disponibilidad'].search([('camion_id', '=', camion_id), ('estado', '=', 'ocupado')], limit=1)
        #     if camion_disponible:
        #         camion_disponible.write({
        #         'estado': 'disponible',
        #         'fecha_hora_liberacion': fecha_hora_actual,
        #     })
                
    def action_liquidado(self):
        self.write({'state': 'liquidado'})  
        
    def action_coordinado(self):
        self.write({'state': 'coordinado'})

    def action_borrador(self):
        self.write({'state': 'borrador'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gms.viaje')
        return super().create(vals)

