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
        _logger.info("Iniciando button_schedule_trip para el albarán: %s", self.name)
    
        agendas = self.agenda_ids.filtered(lambda r: r.state in ['solicitud', 'proceso', 'confirmado'])
        if agendas:
            raise UserError('Ya existe una agenda en estado Solicitud, Proceso o Confirmado.')
        else:
            tipo_viaje = 'entrada' if self.picking_type_id.code == 'incoming' else 'salida'
            _logger.info("Picking type code: %s", self.picking_type_id.code)
    
            if tipo_viaje == 'entrada':
                # Verifica el tipo del partner asociado al albarán
                if self.partner_id.tipo != 'chacra':
                    # Lanzar un error si el origen no es de tipo 'chacra'
                    raise UserError("El origen no es de tipo 'chacra'. No se puede agendar el viaje.")
                origen = self.partner_id.id
    
                destino = self.picking_type_id.warehouse_id.partner_id.id
            else:
                origen = self.picking_type_id.warehouse_id.partner_id.id
                destino = self.partner_id.id
    
            agenda_vals = {
                'fecha': fields.Date.today(),
                'fecha_viaje': fields.Date.today(),
                'solicitante_id': self.partner_id.id,
                'origen': origen,
                'destino': destino,
                'picking_id': self.id,
                'tipo_viaje': tipo_viaje,
            }
    
            _logger.info("Valores de la agenda a crear: %s", agenda_vals)
            self.env['gms.agenda'].create(agenda_vals)
    
        _logger.info("Finalizando button_schedule_trip para el albarán: %s", self.name)
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


    viaje_ids = fields.One2many('gms.viaje', 'picking_id', string='Viajes Relacionados')
    viaje_count = fields.Integer(string='Número de Viajes', compute='_compute_viaje_count')

    @api.depends('viaje_ids')
    def _compute_viaje_count(self):
        for picking in self:
            picking.viaje_count = len(picking.viaje_ids)
    
    def button_create_trip(self):
        _logger.info(f"Iniciando button_create_trip para el albarán {self.name} con estado {self.state} y tipo {self.picking_type_id.code}")
        order = None  # Inicializar la variable 'order'
        tipo_viaje = 'entrada' if self.picking_type_id.code == 'incoming' else 'salida'
    
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

        if tipo_viaje == 'entrada':
                # Verificar si el tipo del partner_id es 'chacra' o 'planta'
                #if self.partner_id.tipo not in ['chacra', 'planta']:
                    # Lanzar un error si el tipo no es ni 'chacra' ni 'planta'
                    #raise UserError("El Solicitante no es de tipo 'Chacra' ni 'Planta'. No se puede agendar el viaje.")
                origen = self.partner_id.id
    
                sub_contactos_origen = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id)], limit=1)
                if sub_contactos_origen:
                    origen = sub_contactos_origen.id
                else:
                    raise UserError("No se encontraron sub contactos para el solicitante.")
                destino = self.picking_type_id.warehouse_id.partner_id.id
        else:
                origen = self.picking_type_id.warehouse_id.partner_id.id
                # Buscar el primer sub contacto del destinatario para viajes de salida
                sub_contactos_destino = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id)], limit=1)
                if sub_contactos_destino:
                    destino = sub_contactos_destino.id
                else:
                    # Si no se encuentra sub contacto para el destinatario, usar el ID del partner_id como destino
                    destino = self.partner_id.id
    
        # Determinar el producto transportado y la cantidad
        if len(self.move_ids_without_package) > 0:
            producto_transportado_id = self.move_ids_without_package[0].product_id.id
            cantidad = self.move_ids_without_package[0].quantity_done
        else:
            producto_transportado_id = False
            cantidad = 0.0


        ruta = self.env['gms.rutas'].search([
            ('direccion_origen_id', '=', origen),
            ('direccion_destino_id', '=', destino),
        ], limit=1)
    

        # Crear el viaje
        viaje_vals = {
            'fecha_viaje': fields.Date.today(),
            'arribo': fields.Datetime.now(),
            'solicitante_id': self.partner_id.id,
            'origen': origen,
            'destino': destino,
            'picking_id': self.id,
            'tipo_viaje': tipo_viaje,
            'producto_transportado_id': producto_transportado_id,
            'ruta_id': ruta.id if ruta else False,
            'creado_desde_albaran': True,
            'albaran_id': self.id,
            
        }
        self.env['gms.viaje'].create(viaje_vals)  

        return True
    
    def action_view_trip(self):
        self.ensure_one()
        last_viaje_id = self.viaje_ids and max(self.viaje_ids.ids) or False
        if last_viaje_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Viaje',
                'res_model': 'gms.viaje',
                'view_mode': 'form',
                'res_id': last_viaje_id,  # ID del último viaje creado
                'target': 'current',
                'context': self.env.context,
            }
        else:
            # Manejar el caso en que no hay viajes asociados
            return {'type': 'ir.actions.act_window_close'}
    
    
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
            viaje_confirmado = any(viaje.state == 'terminado' for viaje in self.viaje_ids)
            if not viaje_confirmado:
                raise UserError("No se puede validar el albarán hasta que el viaje esté confirmado.")
         # Sumar el total de los productos en el albarán
            total_albaran = sum(move.quantity_done  for move in self.move_ids_without_package)
            
            # Sumar el total de los viajes asociados
            total_viaje = sum(viaje.kilogramos_a_liquidar for viaje in self.viaje_ids)

            #if total_albaran != total_viaje:
                #raise UserError("El total del albarán no coincide con el total del viaje.")

        return super(StockPicking, self).button_validate()



    @api.model
    def create(self, vals):
        # Solo para albaranes de entrada (compras)
        if vals.get('picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            if picking_type.code == 'incoming':
                # Establecer 'owner_id' igual a 'partner_id'
                vals['owner_id'] = vals.get('partner_id')
        return super(StockPicking, self).create(vals)

