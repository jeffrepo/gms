from odoo import models, fields, api, _
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

    purchase_order_ids = fields.Many2many('purchase.order', string='Órdenes de Compra')


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
        # Obtener los IDs de los viajes asociados a esta factura
        viaje_ids = self.viajes_ids.ids
        if viaje_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Viajes',
                'res_model': 'gms.viaje',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', viaje_ids)],  # Filtrar para mostrar solo los viajes de esta factura
                'target': 'current',
                'context': self.env.context,
            }
        else:
            # Manejar el caso en que no hay viajes asociados
            return {'type': 'ir.actions.act_window_close'}


    def unlink(self):
        for record in self:
            # Si la factura está en estado distinto de 'borrador' y tiene viajes asociados
            if record.state != 'draft' and record.viajes_ids:
                raise UserError(_("No se puede eliminar la factura en estado '%s' porque está asociada a uno o más viajes.") % record.state)
            
            # Cambiar el estado de los viajes asociados a 'proceso'
            if record.viajes_ids:
                record.viajes_ids.write({'state': 'proceso'})
        
        return super(AccountMove, self).unlink()




    @api.model_create_multi 
    def create(self, vals_list):
        # Crear la factura como normalmente
        record = super(AccountMove, self).create(vals_list)

        # Verificar si la factura está asociada a viajes
        if 'viajes_ids' in vals_list:
            # Recuperar los nombres de los viajes asociados
            viajes_ids = [v_id[1] for v_id in vals_list['viajes_ids'] if v_id[0] == 4]
            viajes = self.env['gms.viaje'].browse(viajes_ids)
            nombres_viajes = viajes.mapped('name')

            # Crear un mensaje en el chatter con los nombres de los viajes
            if nombres_viajes:
                mensaje = _("Factura creada para los viajes: %s") % ', '.join(nombres_viajes)
                record.message_post(body=mensaje)

        return record
    


    
    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Compra',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }
    

    # def action_view_viajes(self):
    #     action = self.env.ref('gms.viaje').read()[0]  
    #     action['domain'] = [('id', 'in', self.viajes_ids.ids)]
    #     action['context'] = {'default_invoice_id': self.id}  
    #     return action
