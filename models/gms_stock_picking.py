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
                destino = self.picking_type_id.warehouse_id.partner_id.id  
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
        _logger.info(f"Iniciando button_create_trip para el albarán {self.name} con estado {self.state} y tipo {self.picking_type_id.code}")
        order = None  # Inicializar la variable 'order'

        # Verificar si ya existe un viaje para este albarán
        if self.viaje_ids:
            raise UserError('Ya existe un viaje para este albarán.')

        _logger.info(f"Albarán {self.name}: Sin viajes existentes. Procesando creación de orden...")

        # Crear orden de compra o venta si no existe
        if not self.origin:
            if self.picking_type_id.code == 'incoming':
                _logger.info(f"Albarán {self.name}: Creando orden de compra.")
                order_vals = self._prepare_purchase_order_vals()
                order = self.env['purchase.order'].create(order_vals)
                self.origin = order.name
            elif self.picking_type_id.code == 'outgoing':
                _logger.info(f"Albarán {self.name}: Creando orden de venta.")
                order_vals = self._prepare_sale_order_vals()
                order = self.env['sale.order'].create(order_vals)
                self.origin = order.name

        # Pasar la información de la orden al asistente, si la orden fue creada
        if order:
            order_type = 'purchase' if self.picking_type_id.code == 'incoming' else 'sale'
            order_id = order.id
        else:
            order_type = None
            order_id = None

        # Abrir el asistente para seleccionar camión
        return {
            'name': 'Seleccionar Camión Disponible',
            'type': 'ir.actions.act_window',
            'res_model': 'gms.camion.seleccion.asistente',
            'view_mode': 'form',
            'view_id': self.env.ref('gms.view_camion_seleccion_asistente_form').id,
            'target': 'new',
            'context': {
                'default_albaran_id': self.id,
                'order_type': order_type,
                'order_id': order_id
            }
        }

    
    def _prepare_purchase_order_vals(self):
        # Preparar valores para la creación de la orden de compra
        line_vals = []
        for move in self.move_ids:  
            line_vals.append((0, 0, {
                'product_id': move.product_id.id,
                'product_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'price_unit': move.product_id.standard_price,
                'date_planned': fields.Date.today(),
            }))
        return {
            'partner_id': self.partner_id.id,
            'order_line': line_vals,
        }


    def _prepare_sale_order_vals(self):
    # Preparar valores para la creación de la orden de venta
        line_vals = []
        for move in self.move_ids:
            line_vals.append((0, 0, {
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'price_unit': move.product_id.list_price,
            }))
        return {
            'partner_id': self.partner_id.id,
            'order_line': line_vals,
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
    




    # Campo calculado para controlar la visibilidad del botón "Agendar viaje"
    show_button_schedule_trip = fields.Boolean(compute='_compute_show_buttons')
    # Campo calculado para controlar la visibilidad del botón "Crear viaje"
    show_button_create_trip = fields.Boolean(compute='_compute_show_buttons')

    @api.depends('agenda_ids', 'viaje_ids')
    def _compute_show_buttons(self):
        for record in self:
            # Si hay alguna agenda o algún viaje, ambos botones deben estar ocultos.
            agenda_exists = any(agenda.state in ['solicitud', 'proceso', 'confirmado'] for agenda in record.agenda_ids)
            viaje_exists = bool(record.viaje_ids)
            record.show_button_schedule_trip = not (agenda_exists or viaje_exists)
            record.show_button_create_trip = not (agenda_exists or viaje_exists)
            _logger.info(f"Record {record.id}: show_button_schedule_trip = {record.show_button_schedule_trip}, show_button_create_trip = {record.show_button_create_trip}")



    def button_validate(self):
        if self.picking_type_id.code == 'incoming' and self.viaje_ids:
            viaje_confirmado = any(viaje.state == 'confirmado' for viaje in self.viaje_ids)
            if not viaje_confirmado:
                raise UserError("No se puede validar el albarán hasta que el viaje esté confirmado.")
        return super(StockPicking, self).button_validate()



    def write(self, vals):
        if 'state' in vals and self.viaje_ids:
            raise UserError("No se puede cambiar el albarán que tiene viajes asociados.")
        return super(StockPicking, self).write(vals)


    @api.model
    def create(self, vals):
        # Solo para albaranes de entrada (compras)
        if vals.get('picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if picking_type.code == 'incoming':
                # Establecer 'owner_id' igual a 'partner_id'
                vals['owner_id'] = vals.get('partner_id')
        return super(StockPicking, self).create(vals)

