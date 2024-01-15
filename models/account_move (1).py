from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo adicional para asignar propietario
    ap_id = fields.Many2one('res.partner', string='Asignar Propietario')
    #conector hacia viajes
    viajes_ids = fields.Many2many('gms.viaje', string='Viajes Asociados')

    total_descontar = fields.Char(string="Total a descontar", tracking="1")

    def action_post(self):
        # Llamar al método original
        res = super(AccountMove, self).action_post()

        # Establecer el propietario en los albaranes asociados
        for invoice in self:
            if invoice.move_type in ['in_invoice', 'in_refund']:
                # Encontrar los pedidos de compra relacionados con la factura
                purchase_orders = invoice.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
                
                for order in purchase_orders:
                    # Para cada pedido de compra, encontrar los albaranes asociados
                    pickings = order.picking_ids

                    for picking in pickings:
                        # Actualizar el 'owner_id' con el valor de 'ap_id' de la factura
                        picking.write({'owner_id': invoice.ap_id.id})
                        _logger.info(f"Actualizado owner_id en el albarán {picking.name} con el valor {invoice.ap_id.id}")

        return res


    def action_view_viajes(self):
        self.ensure_one() 
        if self.viajes_ids:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'gms.viaje',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.viajes_ids.ids)],
                'context': {'create': False},
                'target': 'current',
            }
        else:
            raise UserError('No hay viajes asociados a esta factura.')



    def unlink(self):
        # Verificar si alguna de las facturas está asociada a un viaje
        for record in self:
            if record.viajes_ids:
                raise UserError("No se puede eliminar la factura, porque está asociada a un viaje.")
        
       
        return super(AccountMove, self).unlink()
    