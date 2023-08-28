from odoo import models, fields

class CamionesDisponibilidad(models.Model):
    _name = 'gms.camiones.disponibilidad'
    _description = 'Disponibilidad de Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name ="camion_id"
    _order = 'fecha_hora_liberacion DESC' 
    
    follower_ids = fields.Many2many('res.users', string='Followers')
    camion_id = fields.Many2one('gms.camiones', string='Camión', required=True, order="fecha_hora_liberacion desc")
    fecha_hora_liberacion = fields.Datetime(string='Fecha y Hora de Liberación')
    transportista_id = fields.Many2one('res.partner', string='Trasportista', tracking="1")
    estado = fields.Selection([
        ('ocupado', 'Ocupado'),
        ('disponible', 'Disponible')
    ], string='Estado', default='disponible', required=True)