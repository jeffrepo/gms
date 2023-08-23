from odoo import models, fields, api

class HistorialAgendasCamiones(models.Model):
    _name = 'gms.historial'
    _description = 'Historial de Agendas de Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers')
    camion_id = fields.Many2one('gms.camiones', string='Camión', required=True)
    fecha_hora_liberacion = fields.Datetime(string='Fecha y Hora de Liberación', required=True)
    fecha = fields.Date(string='Fecha')
    agenda_id = fields.Many2one('gms.agenda', string='Agenda', required=True)  # Cambiamos el modelo relacionado

    # Restricción para asegurarse de que el campo disponibilidad_id esté relacionado con el camión correcto
    _sql_constraints = [
        ('camion_disponibilidad_check', 'CHECK(disponibilidad_id.camion_id = camion_id)', 'La disponibilidad debe pertenecer al mismo camión.'),
    ]
