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
            # Buscar si ya existe una disponibilidad para este camión
            disponibilidad_existente = self.env['gms.camiones.disponibilidad'].search([
                ('camion_id', '=', camion.id),
                ('estado', '=', 'ocupado'),  # Buscar si está ocupado
            ], limit=1)

            if disponibilidad_existente:
                # Actualizar la disponibilidad existente a "disponible"
                disponibilidad_existente.write({
                    'estado': 'disponible',
                    'fecha_hora_liberacion': fields.Datetime.now(),
                })
            else:
                # Crear una nueva disponibilidad si no existe
                disponibilidad_vals = {
                    'camion_id': camion.id,
                    'estado': 'disponible',
                    'fecha_hora_liberacion': fields.Datetime.now(),
                    'transportista_id': camion.transportista_id.id,
                }
                self.env['gms.camiones.disponibilidad'].create(disponibilidad_vals)

            # Marcar el camión como disponible
            camion.write({'disponible': True})

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
