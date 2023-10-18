from odoo import models, fields, api

class HistorialAgendasCamiones(models.Model):
    _name = 'gms.historial'
    _description = 'Historial de Agendas de Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    follower_ids = fields.Many2many('res.users', string='Followers', readonly=True)
    camion_id = fields.Many2one('gms.camiones', string='Camión', readonly=True)
    fecha_hora_liberacion = fields.Datetime(string='Fecha y Hora de Liberación', readonly=True)
    fecha = fields.Date(string='Fecha', readonly=True)
    agenda_id = fields.Many2one('gms.agenda', string='Agenda', readonly=True)

    # _sql_constraints = [
    #     ('camion_disponibilidad_check', 'CHECK(disponibilidad_id.camion_id = camion_id)', 'La disponibilidad debe pertenecer al mismo camión.'),
    # ]
