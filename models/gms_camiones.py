from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class Camiones(models.Model):
    _name = 'gms.camiones'
    _description = 'Camiones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "matricula"

    follower_ids = fields.Many2many('res.users', string='Followers')
    nombre = fields.Char(string='Nombre', tracking= 1)
    matricula = fields.Char(string='Matrícula', tracking= 1)
    capacidad_kgs = fields.Float(string='Capacidad en Kgs', tracking= 1)
    minimo_carga_kgs = fields.Float(string='Mínimo de Carga en Kgs', tracking= 1)
    transportista_id = fields.Many2one(
    'res.partner', 
    string='Transportista', 
    domain="[('transportista', '=', True), ('parent_id', '=', False)]", 
    tracking = False
)

    conductor_id = fields.Many2one('res.partner', string='Chofer', required=True, tracking= 1 , domain=[('tipo', '=', 'chofer')])
    disponible = fields.Boolean(string='Disponible', default=True, tracking= 1)
    disponible_zafra = fields.Boolean(string="Zafra", tracking= 1)
     
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Convertir la matrícula a mayúsculas
            matricula = vals.get('matricula', '').upper()
            # Verificar si la matrícula ya existe
            existing = self.search([('matricula', '=', matricula)])
            if existing:
                raise UserError("La matrícula ya existe!")
            vals['matricula'] = matricula
        return super(Camiones, self).create(vals_list)

    def write(self, vals):
        # Si se está actualizando la matrícula
        if 'matricula' in vals:
            matricula = vals['matricula'].upper()
            # Verificar si la matrícula ya existe y no es el mismo registro
            existing = self.search([('matricula', '=', matricula), ('id', '!=', self.id)])
            if existing:
                raise UserError("La matrícula ya existe!")
            vals['matricula'] = matricula
        return super(Camiones, self).write(vals)

    def action_liberar_camion(self):
        for camion in self:
            if not camion.disponible_zafra:
                raise UserError("Este camión no tiene la opción 'Disponible Zafra' configurada.")

            # Buscar disponibilidad del camión
            disponibilidad = self.env['gms.camiones.disponibilidad'].search([
                ('camion_id', '=', camion.id)
            ], limit=1)

            # Si hay una disponibilidad, verificar el estado del viaje asociado
            if disponibilidad:
                viaje_asociado = self.env['gms.viaje'].search([
                    ('camion_disponible_id', '=', disponibilidad.id),
                    ('state', 'in', ['borrador', 'coordinado', 'proceso'])
                ], limit=1)
                
                if viaje_asociado:
                    raise UserError("El camión no se puede liberar porque está ocupado en un viaje.")

            # Si no hay disponibilidad, crear una nueva
            if len(disponibilidad) == 0:
                disponibilidad_vals = {
                    'camion_id': camion.id,
                    'estado': 'disponible',
                    'fecha_hora_liberacion': fields.Datetime.now(),
                    'transportista_id': camion.transportista_id.id,
                    'conductor_id': camion.conductor_id.id,
                }
                self.env['gms.camiones.disponibilidad'].create(disponibilidad_vals)

            camion.write({'disponible': True})




    @api.onchange('transportista_id')
    def _onchange_transportista_id(self):
        res = {}
        if self.transportista_id:
            # Esto obtendrá todos los contactos cuyo padre es el transportista seleccionado
            res['domain'] = {'conductor_id': [('parent_id', '=', self.transportista_id.id)]}
        else:
            res['domain'] = {'conductor_id': [('parent_id', '=', False)]} # Opcional, aquí podrías decidir qué mostrar si no hay transportista seleccionado
        return res
    



    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
            return super(Camiones, self).search(args, offset=offset, limit=limit, order=order)
