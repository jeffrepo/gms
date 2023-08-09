from odoo import models, fields

class Camiones(models.Model):
    _name = 'gms.camiones'
    _description = 'Camiones'

    nombre = fields.Char(string='Nombre')
    matricula = fields.Char(string='Matrícula')
    capacidad_kgs = fields.Float(string='Capacidad en Kgs')
    minimo_carga_kgs = fields.Float(string='Mínimo de Carga en Kgs')
    conductor_id = fields.Many2one('res.partner', string='Conductor')
    estado = fields.Selection([
        ('disponible', 'Disponible'),
        ('no_disponible', 'No Disponible')
    ], string='Estado', default='disponible')
    transportista_id = fields.Many2one('res.partner', string='Transportista', readonly=True)
    