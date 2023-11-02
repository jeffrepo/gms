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
             # Obtener el cliente del pedido de venta
            solicitante = self.sale_id.partner_id.id if self.sale_id else self.partner_id.id
            tipo_viaje = 'entrada' if self.picking_type_id.code == 'incoming' else 'salida'
            _logger.info("Picking type code: %s", self.picking_type_id.code)


            agenda_vals = {
                'fecha': fields.Date.today(),
                'fecha_viaje': fields.Date.today(),
                'solicitante_id': solicitante,
                'origen': self.picking_type_id.warehouse_id.partner_id.id,
                'destino': self.partner_id.id,
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
