from odoo import models, fields

class CamionesDisponibilidad(models.Model):
    _name = 'gms.camiones.disponibilidad'
    _description = 'Disponibilidad de Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name ="camion_id"
    
    follower_ids = fields.Many2many('res.users', string='Followers')
    camion_id = fields.Many2one('gms.camiones', string='Camión', required=True)
    fecha_inicio = fields.Date(string='Fecha de Inicio')

    estado = fields.Selection([
        ('ocupado', 'Ocupado'),
        ('disponible', 'Disponible')
    ], string='Estado', default='disponible', required=True)