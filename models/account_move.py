from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    ap_id = fields.Many2one('res.partner', string='Asignar Propietario')

    # Campo Many2many para viajes asociados
    viajes_ids = fields.Many2many(
        'gms.viaje', 
        string='Viajes Asociados',
        relation='account_move_viaje_rel',  
    )

    # Campo Many2many para liquidar viajes con una nueva tabla de relación
    viajes_liquidar_ids = fields.Many2many(
        'gms.viaje', 
        string='Viajes',
        domain="[('solicitante_id', '=', partner_id), ('state', 'in', ['coordinado', 'proceso', 'terminado','pendiente_liquidar'])]",
        relation='account_move_viaje_liquidar_rel',  
    )

    total_descontar = fields.Char(string="Total a descontar", tracking="1")

    purchase_order_ids = fields.Many2many('purchase.order', string='Órdenes de Compra')
    sale_order_ids = fields.Many2many('sale.order', string='Órdenes de Venta', tracking=True)

    # total de kg seleccionados
    total_kg_seleccionados = fields.Float(
        string='Total kg a Liquidar', 
        compute='_compute_total_kg_seleccionados', 
        store=True
    )

    @api.depends('viajes_liquidar_ids')
    def _compute_total_kg_seleccionados(self):
        for record in self:
            total_kg = 0.0
            for viaje in record.viajes_liquidar_ids:
                if viaje.state == 'pendiente_liquidar':
                    total_kg += viaje.kg_pendiente_liquidar
                else:
                    total_kg += viaje.kilogramos_a_liquidar
            record.total_kg_seleccionados = total_kg

    def action_view_viajes(self):
        self.ensure_one()
        viaje_ids = self.viajes_ids.ids
        if viaje_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Viajes a Liquidar',
                'res_model': 'gms.viaje',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', viaje_ids)],
                'target': 'current',
                'context': self.env.context,
            }
        else:
            return {'type': 'ir.actions.act_window_close'}

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for invoice in self:
            if invoice.move_type in ['in_invoice', 'in_refund']:
                purchase_orders = invoice.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
                for order in purchase_orders:
                    pickings = order.picking_ids
                    for picking in pickings:
                        picking.write({'owner_id': invoice.ap_id.id})
                        _logger.info(f"Actualizado owner_id en el albarán {picking.name} con el valor {invoice.ap_id.id}")
        return res

    def unlink(self):
        for record in self:
            if record.state != 'draft' and record.viajes_ids:
                raise UserError(_("No se puede eliminar la factura en estado '%s' porque está asociada a uno o más viajes.") % record.state)
            if record.viajes_ids:
                record.viajes_ids.write({'state': 'proceso'})
        return super(AccountMove, self).unlink()

    @api.model_create_multi 
    def create(self, vals_list):
        record = super(AccountMove, self).create(vals_list)
        if 'viajes_ids' in vals_list:
            viajes_ids = [v_id[1] for v_id in vals_list['viajes_ids'] if v_id[0] == 4]
            viajes = self.env['gms.viaje'].browse(viajes_ids)
            nombres_viajes = viajes.mapped('name')
            if nombres_viajes:
                mensaje = _("Factura creada para los viajes: %s") % ', '.join(nombres_viajes)
                record.message_post(body=mensaje)
        return record

    def action_view_purchase_orders(self):
        self.ensure_one()
        _logger.info(f"Acción llamada para el registro con ID: {self.id}")
        _logger.debug(f"Purchase Order IDs: {self.purchase_order_ids.ids}")
        if not self.purchase_order_ids:
            _logger.warning("No hay órdenes de compra relacionadas para este registro.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Compra',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Venta',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }


    def action_liquidar_viajes_desde_factura(self):
        self.ensure_one()  # Asegurarse de que solo una factura esté siendo procesada
    
        if not self.viajes_liquidar_ids:
            raise UserError("No se seleccionaron viajes para liquidar.")
    
        _logger.info("Iniciando el proceso de liquidación de viajes desde la factura...")
    
        # Verificar si la factura ya tiene un viaje en estado 'pendiente_liquidar'
        if any(viaje.state == 'pendiente_liquidar' for viaje in self.viajes_ids):
            raise UserError("No se pueden agregar más viajes se paso de la cantidad a liquidar.")
    
        # Obtener la línea de la factura y su cantidad
        if len(self.invoice_line_ids) != 1:
            raise UserError("La factura debe tener exactamente una línea de producto.")
    
        linea_factura = self.invoice_line_ids[0]
        cantidad_factura = linea_factura.quantity
    
        # Filtrar solo los viajes que no están liquidados
        viajes_a_liquidar = self.viajes_liquidar_ids.filtered(lambda v: v.state != 'liquidado')
    
        if not viajes_a_liquidar:
            raise UserError("Todos los viajes seleccionados ya están liquidados. No hay nada para procesar.")
    
        viajes_liquidados = []  # Lista para almacenar los viajes que se liquidan
        viajes_pendientes = []  # Lista para almacenar los viajes que quedan pendientes
    
        for viaje in viajes_a_liquidar:
            _logger.info(f"Procesando viaje: {viaje.name}")
    
            # Determinar la cantidad a liquidar, usando kg_pendiente_liquidar si el viaje está en estado 'pendiente_liquidar'
            kg_a_liquidar = viaje.kg_pendiente_liquidar if viaje.state == 'pendiente_liquidar' else viaje.kilogramos_a_liquidar
    
            # Restar la cantidad del viaje de la cantidad de la factura
            if cantidad_factura >= kg_a_liquidar:
                # Se puede liquidar completamente este viaje
                cantidad_factura -= kg_a_liquidar
                viaje.write({'state': 'liquidado', 'kg_pendiente_liquidar': 0, 'factura_id': self.id})
                _logger.info(f"Viaje {viaje.name} liquidado completamente.")
                viajes_liquidados.append(viaje.id)
            else:
                # No se puede liquidar completamente este viaje
                kg_pendientes = kg_a_liquidar - cantidad_factura
                viaje.write({'state': 'pendiente_liquidar', 'kg_pendiente_liquidar': kg_pendientes, 'factura_id': self.id})
                _logger.info(f"Viaje {viaje.name} no liquidado completamente. Quedan pendientes {kg_pendientes} kg.")
                cantidad_factura = 0  # No queda cantidad disponible en la factura para más viajes
                viajes_pendientes.append(viaje.id)
                break  # Se interrumpe el proceso al no poder liquidar más
    
        # Actualizar el campo 'viajes_ids' en la factura para incluir todos los viajes procesados
        if viajes_liquidados or viajes_pendientes:
            self.write({'viajes_ids': [(4, vid) for vid in viajes_liquidados + viajes_pendientes]})
    
        _logger.info("Proceso de liquidación de viajes desde la factura finalizado.")
