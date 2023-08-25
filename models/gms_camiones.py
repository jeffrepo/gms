from odoo import models, fields, api

class Camiones(models.Model):
    _name = 'gms.camiones'
    _description = 'Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name ="matricula"

    follower_ids = fields.Many2many('res.users', string='Followers')
    nombre = fields.Char(string='Nombre', tracking ="1")
    matricula = fields.Char(string='Matrícula', tracking ="1")
    capacidad_kgs = fields.Float(string='Capacidad en Kgs', tracking ="1")
    minimo_carga_kgs = fields.Float(string='Mínimo de Carga en Kgs', tracking ="1")
    conductor_id = fields.Many2one('res.partner', string='Conductor', tracking ="1")
    estado = fields.Selection([
        ('disponible', 'Disponible'),
        ('no_disponible', 'No Disponible')
    ], string='Estado', default='disponible')
    transportista_id = fields.Many2one('res.partner', string='Transportista', readonly=True, tracking ="1")
    

    @api.model
    def create(self, vals):
        # Crea el camión
        camion = super(Camiones, self).create(vals)

        # Crea un registro en 'gms.camiones.disponibilidad' usando el id del camión
        disponibilidad_camion = self.env['gms.camiones.disponibilidad'].create({
            'camion_id': camion.id,
            'fecha_inicio': fields.Date.today(),
        })

        return camion