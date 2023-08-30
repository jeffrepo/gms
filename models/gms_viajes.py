from odoo import models, fields

class Viajes(models.Model):
    _name = 'gms.viaje'
    _description = 'Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')

    name = fields.Char(string='Nombre del viaje', tracking="1")
    fecha_viaje = fields.Date(string='Fecha de viaje', tracking="1")
    origen = fields.Many2one('res.partner', string='Origen', required=True, tracking="1")
    destino = fields.Many2one('res.partner', string='Destino', required=True, tracking="1")
    camion_disponible_id = fields.Many2one('gms.camiones.disponibilidad', string='Camión Disponible', tracking="1")
   


    state = fields.Selection([
        ('cancelado', 'Cancelado'),
        ('borrador', 'Borrador'),
        ('proceso', 'Proceso'),
        ('terminado', 'Terminado'),
        ('liquidado', 'Liquidado')
        
    ], string='Estado', default='borrador', required=True)  

    gastos_ids = fields.One2many('gms.gasto_viaje', 'viaje_id', string='Gastos')

    def action_confirm(self):
        self.write({'state': 'proceso'})


    def action_cancel(self):
        self.write({'state': 'cancelado'})

    def action_done(self):
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
        if camion_id:
            camion_disponible = self.env['gms.camiones.disponibilidad'].search([('camion_id', '=', camion_id), ('estado', '=', 'ocupado')], limit=1)
            if camion_disponible:
                camion_disponible.write({
                'estado': 'disponible',
                'fecha_hora_liberacion': fecha_hora_actual,
            })
                
    def action_paid(self):
        self.write({'state': 'liquidado'})      