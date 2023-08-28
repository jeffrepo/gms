from odoo import models, fields, api

class Camiones(models.Model):
    _name = 'gms.camiones'
    _description = 'Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "matricula"

    follower_ids = fields.Many2many('res.users', string='Followers')
    nombre = fields.Char(string='Nombre', tracking="1")
    matricula = fields.Char(string='Matrícula', tracking="1")
    capacidad_kgs = fields.Float(string='Capacidad en Kgs', tracking="1")
    minimo_carga_kgs = fields.Float(string='Mínimo de Carga en Kgs', tracking="1")
    transportista_id = fields.Many2one('res.partner', string='Transportista', tracking="1")
    conductor_id = fields.Many2one('res.partner', string='Conductor', readonly=True, tracking="1")
    disponible = fields.Boolean(string='Disponible', default=True, tracking="1")
    ocupado = fields.Boolean(string='Ocupado', default=False, tracking="1")

    
    def action_hacer_disponible(self):
        for camion in self:
            if not camion.disponible:
                camion.write({'disponible': True})
                fecha_hora_actual = fields.Datetime.now()
                disponibilidad_vals = {
                    'camion_id': camion.id,
                    'estado': 'disponible',
                    'fecha_hora_liberacion': fecha_hora_actual,
                    # Agrega otros campos de disponibilidad aquí según sea necesario
                }
                self.env['gms.camiones.disponibilidad'].create(disponibilidad_vals)

    
    def action_hacer_ocupado(self):
        for camion in self:
            if camion.disponible:
                camion.write({'disponible': False})
                disponibilidad = camion.env['gms.camiones.disponibilidad'].search([
                    ('camion_id', '=', camion.id),
                    ('estado', '=', 'disponible')
                ], limit=1)
                if disponibilidad:
                    disponibilidad.write({'estado': 'ocupado'})
