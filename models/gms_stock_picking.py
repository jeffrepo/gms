from odoo import models, fields, api 
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = 'stock.picking'
  


    agenda_ids = fields.One2many('gms.agenda', 'picking_id', string='Agendas')
    agenda_count = fields.Integer(string='Agenda Count', compute='_compute_agenda_count')

    
    @api.depends('agenda_ids')
    def _compute_agenda_count(self):
        for picking in self:
            picking.agenda_count = len(picking.agenda_ids)

   
    def button_schedule_trip(self):
        # Verificar si ya hay una agenda con estados solicitud, proceso o confirmado
        agendas = self.agenda_ids.filtered(lambda r: r.state in ['solicitud', 'proceso', 'confirmado'])
        if agendas:
            # Si hay, lanzar un mensaje de advertencia
            raise UserError('Ya existe una agenda en estado Solicitud, Proceso o Confirmado.')
        else:
            # Determinar si es un viaje de entrada o salida
            tipo_viaje = 'entrada' if self.picking_type_id.code == 'incoming' else 'salida'
            _logger.info("Picking type code: %s", self.picking_type_id.code)

            # Definir origen y destino basado en el tipo de viaje
            if tipo_viaje == 'entrada':
                origen = self.partner_id.id  # Proveedor
                destino = self.picking_type_id.warehouse_id.partner_id.id  # Almacén
            else:
                origen = self.picking_type_id.warehouse_id.partner_id.id  # Almacén
                destino = self.partner_id.id  # Cliente o destino final

            agenda_vals = {
                'fecha': fields.Date.today(),
                'fecha_viaje': fields.Date.today(),
                'solicitante_id': self.partner_id.id,
                'origen': origen,
                'destino': destino,
                'picking_id': self.id,
                'tipo_viaje': tipo_viaje,
            }
            agenda = self.env['gms.agenda'].create(agenda_vals)
        return True


    
    def action_view_agenda(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Agendas',
            'res_model': 'gms.agenda',
            'view_mode': 'tree,form',
            'domain': [('picking_id', '=', self.id)],
        }









    viaje_ids = fields.One2many('gms.viaje', 'albaran_id', string='Viajes Relacionados')
    viaje_count = fields.Integer(string='Número de Viajes', compute='_compute_viaje_count')

    @api.depends('viaje_ids')
    def _compute_viaje_count(self):
        for picking in self:
            picking.viaje_count = len(picking.viaje_ids)

    def button_create_trip(self):
        # Verificar si ya existe un viaje para este albarán
        if self.viaje_ids:
            raise UserError('Ya existe un viaje para este albarán.')
        else:
            # Abrir el asistente para seleccionar camión
            return {
                'name': 'Seleccionar Camión Disponible',
                'type': 'ir.actions.act_window',
                'res_model': 'gms.camion.seleccion.asistente',
                'view_mode': 'form',
                'view_id': self.env.ref('gms.view_camion_seleccion_asistente_form').id,
                'target': 'new',
                'context': {'default_albaran_id': self.id}
            }
        

           
    


    def action_cancel(self):
        _logger.info("Iniciando el proceso de cancelación del albarán")
        
        # Recorrer todos los viajes relacionados y cancelarlos
        for viaje in self.viaje_ids:
            _logger.info(f"Cancelando el viaje {viaje.name}")
            viaje.action_cancel()

            # Si hay un camión asociado, cambiar su estado a 'disponible'
        if viaje.camion_disponible_id and viaje.camion_disponible_id.camion_id:
            _logger.info(f"Cambiando el estado del camión {viaje.camion_disponible_id.camion_id.matricula} a disponible")
            viaje.camion_disponible_id.write({'estado': 'disponible'})
        else:
            _logger.info("No hay camión asignado a este viaje")

        # Llamada al método original
        res = super(StockPicking, self).action_cancel()

        _logger.info("Finalizado el proceso de cancelación del albarán")

        return res


    def action_view_trip(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Viajes',
            'res_model': 'gms.viaje',
            'view_mode': 'tree,form',
            'domain': [('albaran_id', '=', self.id)],
        }