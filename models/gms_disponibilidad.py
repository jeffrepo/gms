from odoo import models, fields

class CamionesDisponibilidad(models.Model):
    _name = 'gms.camiones.disponibilidad'
    _description = 'Disponibilidad de Camiones'

    camion_id = fields.Many2one('gms.camiones', string='Camión', required=True)
    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True)
    estado = fields.Selection([
        ('ocupado', 'Ocupado'),
        ('disponible', 'Disponible')
    ], string='Estado', default='disponible', required=True)