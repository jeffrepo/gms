from odoo import models, fields

class HistorialCamiones(models.Model):
    _name = 'gms.historial'
    _description = 'Historial de Camiones'

    camion_id = fields.Many2one('gms.camiones', string='Camión', required=True)
    fecha_evento = fields.Date(string='Fecha del Evento', required=True)
    evento = fields.Text(string='Evento', required=True)

    # Restricción para asegurarse de que el campo disponibilidad_id esté relacionado con el camión correcto
    _sql_constraints = [
        ('camion_disponibilidad_check', 'CHECK(disponibilidad_id.camion_id = camion_id)', 'La disponibilidad debe pertenecer al mismo camión.'),
    ]
