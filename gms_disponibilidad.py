from odoo import models, fields

class CamionesDisponibilidad(models.Model):
    _name = 'gms.camiones.disponibilidad'
    _description = 'Disponibilidad de Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name ="camion_id"
    _order = 'fecha_hora_liberacion ASC' 
    
    follower_ids = fields.Many2many('res.users', string='Followers')
    camion_id = fields.Many2one('gms.camiones', string='Camión', required=True, order="fecha_hora_liberacion desc")
    fecha_hora_liberacion = fields.Datetime(string='Fecha y Hora de Liberación')
    transportista_id = fields.Many2one('res.partner', string='Trasportista', tracking="1")
    conductor_id = fields.Many2one('res.partner', string='Conductor', tracking="1")
    estado = fields.Selection([
        ('ocupado', 'Ocupado'),
        ('disponible', 'Disponible')
    ], string='Estado', default='disponible', required=True)


    def name_get(self):
        result = []
        for record in self:
            name = "Camión: %s, Conductor: %s" % (record.camion_id.matricula, record.conductor_id.name)
            result.append((record.id, name))
        return result


